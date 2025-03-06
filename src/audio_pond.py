"""Audio Pond - Convert piano performances into sheet music."""

import logging
import click
from pathlib import Path
from dotenv import load_dotenv

from src.processors.audio_processor import AudioProcessor

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
    no_trim: bool,
    no_split: bool,
    time: str,
    key: str,
    quant: str,
):
    """Convert piano performances into sheet music."""
    processor = AudioProcessor(Path(output_dir))

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

        if not ly_file:
            if not no_trim:
                midi_path = processor.trim_midi_silence(midi_path)

            if not no_split:
                midi_path = processor.split_midi_tracks(midi_path)

            ly_path = processor.midi_to_lilypond(
                midi_path, time=time, key=key, quant=quant
            )

        ly_path = processor.transform_to_parallel_music(ly_path)
        # absolute path needed in docker container
        processor.render_sheet_music(ly_path.absolute())

        click.echo(f"Sheet music has been generated in {output_dir}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
