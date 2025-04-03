"""Audio Pond - Convert piano performances into sheet music."""

import logging
import click
from pathlib import Path
from dotenv import load_dotenv

from src.processors.audio_processor import AudioProcessor, ProcessorConfig

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
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
    "--no-trim",
    is_flag=True,
    help="Skip trimming silence from start of MIDI file before conversion",
)
@click.option(
    "--no-split",
    is_flag=True,
    help="Skip splitting MIDI file into treble and bass tracks",
)
@click.option(
    "--no-tempo-adjust",
    is_flag=True,
    help="Skip adjusting note durations to match the target tempo",
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
@click.option(
    "--bpm",
    type=float,
    default=120,
    help="BPM of the piece",
)
def main(
    source: str,
    audio_file: bool,
    midi_file: bool,
    ly_file: bool,
    output_dir: str,
    no_trim: bool,
    no_split: bool,
    no_tempo_adjust: bool,
    time: str,
    key: str,
    quant: str,
    bpm: float,
):
    """Convert piano performances into sheet music."""
    output_path = Path(output_dir)
    processor = AudioProcessor(output_path)

    config = ProcessorConfig(
        source=source,
        output_dir=output_path,
        audio_file=audio_file,
        midi_file=midi_file,
        ly_file=ly_file,
        no_trim=no_trim,
        no_split=no_split,
        no_tempo_adjust=no_tempo_adjust,
        time=time,
        key=key,
        quant=quant,
        bpm=bpm,
    )

    try:
        processor.run(config)
        click.echo(f"Sheet music has been generated in {output_dir}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
