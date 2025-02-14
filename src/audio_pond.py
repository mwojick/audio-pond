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
        self.midi2lily_path = midi2lily_path or os.getenv("MIDI2LILY_PATH")
        if not self.midi2lily_path:
            raise ValueError(
                "MidiToLily path not provided. Set it via MIDI2LILY_PATH environment variable or --midi2lily-path option"
            )
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

    def midi_to_lilypond(self, midi_path: Path) -> Path:
        """Convert MIDI to LilyPond notation using https://github.com/victimofleisure/MidiToLily."""

        try:
            ly_output_path = self.output_dir / "3_lilypond.ly"
            # Run MidiToLily to convert MIDI to LilyPond
            subprocess.run(
                [
                    # Path to MidiToLily executable
                    self.midi2lily_path,
                    str(midi_path),
                    "-quant",
                    "16",
                    "-time",
                    "1=4/4",
                    "-key",
                    "1=g,29=c",
                    "-staves",
                    "1",
                    "-output",
                    str(ly_output_path),
                ],
                check=True,
                capture_output=True,
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
                capture_output=True,
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
    "--output-dir",
    type=click.Path(),
    default="./output",
    help="Directory for output files",
)
@click.option(
    "--midi2lily-path",
    type=click.Path(),
    help="Path to MidiToLily executable (defaults to MIDI2LILY_PATH env var)",
)
def main(
    source: str,
    audio_file: bool,
    midi_file: bool,
    output_dir: str,
    midi2lily_path: str | None,
):
    """Convert piano performances into sheet music."""
    processor = AudioProcessor(Path(output_dir), midi2lily_path=midi2lily_path)

    try:
        if midi_file:
            midi_path = Path(source)
        else:
            if audio_file:
                audio_path = processor.process_audio_file(Path(source))
            else:
                audio_path = processor.process_youtube(source)

            midi_path = processor.transcribe_audio(audio_path)

        ly_path = processor.midi_to_lilypond(midi_path)
        processor.render_sheet_music(ly_path)

        click.echo(f"Sheet music has been generated in {output_dir}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
