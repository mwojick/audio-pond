"""
Audio Pond - Convert piano performances into professional sheet music.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
import logging

# Configure TensorFlow GPU settings
os.environ["CUDA_DEVICE_ORDER"] = (
    "PCI_BUS_ID"  # Use PCI_BUS_ID for consistent GPU device ordering
)

import click
import yt_dlp
import tensorflow as tf  # Import tensorflow to configure GPU
from basic_pitch.inference import predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
from pydub import AudioSegment

basic_pitch_model = Model(ICASSP_2022_MODEL_PATH)


def setup_gpu():
    """Configure and verify GPU setup."""
    try:
        gpus = tf.config.list_physical_devices("GPU")
        if not gpus:
            logging.warning(
                "No GPU devices found. To enable GPU support, please install:\n"
                "1. NVIDIA GPU drivers (>= 525.60.13)\n"
                "2. CUDA Toolkit 12.3\n"
                "3. cuDNN SDK 8.9.7\n"
                "For now, falling back to CPU."
            )
            return False

        logging.info(f"GPU setup successful. Found {len(gpus)} GPU(s)")
        return True
    except Exception as e:
        logging.warning(f"Failed to configure GPU: {str(e)}")
        return False


class AudioProcessor:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.gpu_available = setup_gpu()

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
            "outtmpl": str(self.output_dir / "output.%(ext)s"),
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return self.output_dir / "output.wav"

    def process_audio_file(self, audio_path: Path) -> Path:
        """Process local audio file to WAV format."""
        output_path = self.output_dir / "output.wav"
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(output_path), format="wav")
        return output_path

    def transcribe_audio(self, audio_path: Path):
        """Transcribe audio to MIDI and LilyPond."""
        # Transcribe audio to MIDI using Basic Pitch

        predict_and_save(
            [str(audio_path)],
            str(self.output_dir),
            True,
            True,
            False,
            False,
            basic_pitch_model,
        )

        # Convert MIDI to LilyPond using midi2ly
        self._midi_to_lilypond(self.output_dir / "output_basic_pitch.midi")

    def _midi_to_lilypond(self, midi_path: Path):
        """Convert MIDI to LilyPond notation using midi2ly."""
        try:
            # Run midi2ly to convert MIDI to LilyPond
            # Options:
            # -s 1: set staff size to 1 (default)
            # -k 0: no key signature guessing
            # -o: output file
            subprocess.run(
                [
                    "midi2ly",
                    "-s",
                    "1",
                    "-k",
                    "0",
                    "-o",
                    str(self.output_dir / "output.ly"),
                    str(midi_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to convert MIDI to LilyPond: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "midi2ly not found. Please make sure LilyPond is installed and available in PATH."
            )

        # Add title and remove default tagline
        ly_path = self.output_dir / "output.ly"
        with open(ly_path, "r") as f:
            content = f.read()

        # Insert header after version declaration
        header = r"""
\header {
  title = "Transcribed Piano Performance"
  tagline = ##f  % Remove default LilyPond tagline
}
"""
        content = content.replace(r"\version", header + r"\version")

        with open(ly_path, "w") as f:
            f.write(content)

    def render_sheet_music(self):
        """Render LilyPond file to PDF."""
        ly_path = self.output_dir / "output.ly"
        if not ly_path.exists():
            raise FileNotFoundError("LilyPond file not found. Run transcription first.")

        try:
            # Run lilypond to generate PDF
            subprocess.run(
                ["lilypond", "-o", str(self.output_dir / "output"), str(ly_path)],
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
    "--output-dir",
    type=click.Path(),
    default="./output",
    help="Directory for output files",
)
def main(source: str, audio_file: bool, output_dir: str):
    """Convert piano performances into sheet music."""
    processor = AudioProcessor(Path(output_dir))

    try:
        if audio_file:
            audio_path = processor.process_audio_file(Path(source))
        else:
            audio_path = processor.process_youtube(source)

        processor.transcribe_audio(audio_path)
        processor.render_sheet_music()

        click.echo(f"Sheet music has been generated in {output_dir}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
