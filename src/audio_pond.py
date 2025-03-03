import os
import subprocess
from pathlib import Path
import logging
import click
import yt_dlp
import torch
import librosa
from pydub import AudioSegment
from piano_transcription_inference import PianoTranscription, sample_rate
from dotenv import load_dotenv
from mido import MidiFile, MidiTrack, MetaMessage

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Configure TensorFlow GPU settings
os.environ["CUDA_DEVICE_ORDER"] = (
    "PCI_BUS_ID"  # Use PCI_BUS_ID for consistent GPU device ordering
)


def setup_gpu():
    """Configure and verify GPU setup."""
    try:
        num_gpus = torch.cuda.device_count()
        if not num_gpus:
            logging.warning("No GPU devices found. For now, falling back to CPU.")
            return False

        logging.info(f"GPU setup successful. Found {num_gpus} GPU(s)")
        return True
    except Exception as e:
        logging.warning(f"Failed to configure GPU: {str(e)}")
        return False


class AudioProcessor:
    def __init__(self, output_dir: Path, midi2lily_path: str | None = None):
        self.output_dir = output_dir
        # look for arg first, then MIDI2LILY_PATH env var, then default to using wine with the provided exe
        midi2lily_path = midi2lily_path or os.getenv("MIDI2LILY_PATH")
        self.midi2lily_exe = (
            [midi2lily_path] if midi2lily_path else ["wine64", "src/MidiToLily.exe"]
        )
        print(f"MIDI2LILY_LOCATION: {self.midi2lily_exe}")
        os.makedirs(output_dir, exist_ok=True)

    def process_youtube(self, url: str) -> Path:
        """Download YouTube video and extract audio."""
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                }
            ],
            "outtmpl": str(self.output_dir / "1_raw_audio.%(ext)s"),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ytdlp = ydl.download([url])
            print(ytdlp)

        return self.output_dir / "1_raw_audio.wav"

    def process_audio_file(self, audio_path: Path) -> Path:
        """Process local audio file to WAV format."""
        audio_output_path = self.output_dir / "1_raw_audio.wav"
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(audio_output_path), format="wav")
        return audio_output_path

    def transcribe_audio(self, audio_path: Path) -> Path:
        """Transcribe audio to MIDI using Piano Transcription Inference"""

        # Setup GPU for transcription
        gpu_available = setup_gpu()
        device = "cuda" if gpu_available else "cpu"

        # Load audio
        audio, _ = librosa.load(path=audio_path, sr=sample_rate, mono=True)

        # Transcriptor
        transcriptor = PianoTranscription(
            device=device, checkpoint_path=None
        )  # device: 'cuda' | 'cpu'

        midi_output_path = self.output_dir / "2_transcription.midi"

        # Transcribe and write out to MIDI file
        transcribed_dict = transcriptor.transcribe(audio, str(midi_output_path))
        print(transcribed_dict)
        return midi_output_path

    def trim_midi_silence(self, midi_path: Path) -> Path:
        """Remove initial silence from MIDI file."""

        # Load the file
        mid = MidiFile(str(midi_path))

        # First, determine the absolute time (in ticks) of each message and find the earliest note_on event.
        offset = None
        for track in mid.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                # Check for note_on events with a non-zero velocity (ignore note_on with velocity 0 which are note offs)
                if msg.type == "note_on" and msg.velocity > 0:
                    if offset is None or abs_time < offset:
                        offset = abs_time

        # If no note_on was found, there's nothing to trim.
        if offset is None:
            offset = 0

        # Now subtract the offset from every message in each track and recalc delta times.
        for track in mid.tracks:
            abs_times = []
            running_time = 0
            # First compute new absolute times (ensuring they don't go below 0)
            for msg in track:
                running_time += msg.time
                new_time = running_time - offset
                abs_times.append(new_time if new_time > 0 else 0)
            # Then convert absolute times back to delta times
            prev = 0
            for i, msg in enumerate(track):
                new_delta = abs_times[i] - prev
                msg.time = new_delta
                prev = abs_times[i]

        # Save the trimmed MIDI file
        output_path = self.output_dir / "2_transcription_trimmed.midi"
        mid.save(str(output_path))

        return output_path

    def split_midi_tracks(self, midi_path: Path) -> Path:
        """Split MIDI file into treble and bass tracks."""

        # Load original MIDI file
        mid = MidiFile(str(midi_path))

        new_mid = MidiFile()
        new_mid.ticks_per_beat = mid.ticks_per_beat

        # Create two tracks (treble + bass)
        treble_track = MidiTrack()
        bass_track = MidiTrack()
        new_mid.tracks = [[], treble_track, bass_track]

        treble_track.append(MetaMessage("track_name", name="Upper", time=0))
        bass_track.append(MetaMessage("track_name", name="Lower", time=0))

        # Define the note threshold: notes below C4 (MIDI 60) go to bass,
        # notes at or above C4 go to treble
        NOTE_THRESHOLD = 60

        # Collect all messages from all tracks
        all_messages = []
        for track in mid.tracks:
            current_time = 0
            for msg in track:
                current_time += msg.time
                all_messages.append((msg, current_time))

        treble_msgs = []
        bass_msgs = []

        for msg, time in all_messages:
            if msg.type == "set_tempo":
                bass_msgs.append((msg, time))
                treble_msgs.append((msg, time))
            elif msg.type == "time_signature":
                bass_msgs.append((msg, time))
                treble_msgs.append((msg, time))
            elif msg.type == "note_on":
                if msg.note >= NOTE_THRESHOLD:
                    # upper voice
                    msg.channel = 0
                    treble_msgs.append((msg, time))
                else:
                    # lower voice
                    msg.channel = 1
                    bass_msgs.append((msg, time))

        # Convert absolute times back to delta times for each track
        def convert_to_delta_time(messages):
            delta_messages = []
            prev_time = 0
            for msg, abs_time in messages:
                delta = abs_time - prev_time
                msg.time = int(delta)
                delta_messages.append(msg)
                prev_time = abs_time
            return delta_messages

        # Convert and add messages to tracks
        for msg in convert_to_delta_time(treble_msgs):
            treble_track.append(msg)
        for msg in convert_to_delta_time(bass_msgs):
            bass_track.append(msg)

        # Ensure each track ends with an end_of_track message
        if treble_track[-1].type != "end_of_track":
            treble_track.append(MetaMessage("end_of_track", time=0))
        if bass_track[-1].type != "end_of_track":
            bass_track.append(MetaMessage("end_of_track", time=0))

        # Save the new MIDI file
        output_path = self.output_dir / "2_transcription_split.midi"
        new_mid.save(str(output_path))

        return output_path

    def midi_to_lilypond(
        self, midi_path: Path, time: str, key: str, quant: str
    ) -> Path:
        """Convert MIDI to LilyPond notation using https://github.com/victimofleisure/MidiToLily."""

        try:
            ly_output_path = self.output_dir / "3_lilypond.ly"
            # Run MidiToLily to convert MIDI to LilyPond
            subprocess.run(
                [
                    # Path to MidiToLily executable
                    *self.midi2lily_exe,
                    str(midi_path),
                    "-quant",
                    quant,
                    "-time",
                    time,
                    "-key",
                    key,
                    "-staves",
                    "1,2",
                    "-output",
                    str(ly_output_path),
                ],
                check=True,
                text=True,
            )
            return ly_output_path
        except subprocess.CalledProcessError as e:
            logging.error(f"MidiToLily output: {e.stdout}")
            raise RuntimeError(f"Failed to convert MIDI to LilyPond: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "MidiToLily not found. Please make sure LilyPond is installed and available in PATH."
            )

    def render_sheet_music(self, ly_path: Path):
        """Render LilyPond file to PDF."""
        if not ly_path.exists():
            raise FileNotFoundError("LilyPond file not found. Run transcription first.")

        try:
            # Run lilypond to generate PDF
            subprocess.run(
                [
                    "lilypond",
                    "-o",
                    str(self.output_dir / "4_sheet_music"),
                    str(ly_path),
                ],
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to render sheet music: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "LilyPond not found. Please make sure LilyPond is installed and available in PATH."
            )


@click.command()
@click.argument("source")
@click.option(
    "--audio-file", is_flag=True, help="Process local audio file instead of YouTube URL"
)
@click.option(
    "--midi-file",
    is_flag=True,
    help="Process local MIDI file directly, skipping transcription",
)
@click.option(
    "--ly-file",
    is_flag=True,
    help="Use local LilyPond file directly, skipping transcription and LilyPond conversion",
)
@click.option(
    "--output-dir",
    type=click.Path(),
    default="./output",
    help="Directory for output files",
)
@click.option(
    "--midi2lily-path",
    type=click.Path(),
    help="Path to MidiToLily executable (defaults to `MIDI2LILY_PATH` env var or `wine64 src/MidiToLily.exe` if neither are provided)",
)
@click.option(
    "--trim-start",
    is_flag=True,
    help="Trim silence from start of MIDI file before conversion",
)
@click.option(
    "--split-tracks",
    is_flag=True,
    help="Split MIDI file into treble and bass tracks",
)
@click.option(
    "--time",
    type=str,
    default="1=4/4",
    help="Comma-separated list of time signatures, each consisting of M=n/d where M is a one-based measure number, and n and d are the the time signature's numerator and denominator.",
)
@click.option(
    "--key",
    type=str,
    default="1=c",
    help="Comma-separated list of key signatures, each consisting of  M=k where M is a one-based measure number, and k is the key signature in LilyPond note format, optionally followed by the letter 'm' to indicate a minor key.",
)
@click.option(
    "--quant",
    type=str,
    default="16",
    help="Quantize note start and end times to the specified duration (1=whole, 2=half, 4=quarter, etc.)",
)
def main(
    source: str,
    audio_file: bool,
    midi_file: bool,
    ly_file: bool,
    output_dir: str,
    midi2lily_path: str | None,
    trim_start: bool,
    split_tracks: bool,
    time: str,
    key: str,
    quant: str,
):
    """Convert piano performances into sheet music."""
    processor = AudioProcessor(Path(output_dir), midi2lily_path=midi2lily_path)

    try:
        if ly_file:
            ly_path = Path(source)
        elif midi_file:
            midi_path = Path(source)
        else:
            if audio_file:
                audio_path = processor.process_audio_file(Path(source))
            else:
                audio_path = processor.process_youtube(source)

            midi_path = processor.transcribe_audio(audio_path)

        # Trim silence before conversion
        if trim_start:
            midi_path = processor.trim_midi_silence(midi_path)

        if split_tracks:
            midi_path = processor.split_midi_tracks(midi_path)

        if not ly_file:
            ly_path = processor.midi_to_lilypond(
                midi_path, time=time, key=key, quant=quant
            )

        processor.render_sheet_music(ly_path)

        click.echo(f"Sheet music has been generated in {output_dir}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
