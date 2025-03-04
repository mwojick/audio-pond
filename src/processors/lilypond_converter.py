"""LilyPond converter for Audio Pond."""

import os
import subprocess
import logging
from pathlib import Path


class LilypondConverter:
    """Handles MIDI to LilyPond conversion and rendering."""

    def __init__(self, output_dir: Path):
        """Initialize the LilyPond converter.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Configure MidiToLily executable path
        midi2lily_path = os.getenv("MIDI2LILY_PATH")
        self.midi2lily_exe = (
            [midi2lily_path] if midi2lily_path else ["wine64", "src/MidiToLily.exe"]
        )
        print(f"MIDI2LILY_LOCATION: {self.midi2lily_exe}")

    def midi_to_lilypond(
        self, midi_path: Path, time: str, key: str, quant: str
    ) -> Path:
        """Convert MIDI to LilyPond notation using https://github.com/victimofleisure/MidiToLily.

        Args:
            midi_path: Path to the input MIDI file
            time: Time signature specification
            key: Key signature specification
            quant: Quantization value

        Returns:
            Path to the generated LilyPond file
        """
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

    def render_sheet_music(self, ly_path: Path) -> Path:
        """Render LilyPond file to PDF.

        Args:
            ly_path: Path to the input LilyPond file

        Returns:
            Path to the generated PDF file
        """
        if not ly_path.exists():
            raise FileNotFoundError("LilyPond file not found. Run transcription first.")

        try:
            output_base = self.output_dir / "4_sheet_music"
            # Run lilypond to generate PDF
            subprocess.run(
                [
                    "lilypond",
                    "-o",
                    str(output_base),
                    str(ly_path),
                ],
                check=True,
                text=True,
            )
            return output_base.with_suffix(".pdf")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to render sheet music: {e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "LilyPond not found. Please make sure LilyPond is installed and available in PATH."
            )
