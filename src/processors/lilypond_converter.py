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

    def transform_to_parallel_music(self, input_path: Path) -> Path:
        """Transform a LilyPond file with separate tracks into one using parallelMusic notation.

        This makes the file easier to manually edit by co-locating corresponding bars from both tracks.

        Args:
            input_path: Path to the input LilyPond file with separate tracks

        Returns:
            Path to the transformed LilyPond file
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input LilyPond file not found: {input_path}")

        # Read the input file
        with open(input_path, "r") as f:
            content = f.read()

        # Extract the header information (everything before the first track)
        header_end = content.find('"track1"')
        header = content[:header_end].strip()

        # Extract the two tracks
        tracks = []
        track_starts = [content.find(f'"track{i}"') for i in range(1, 3)]

        for i, start in enumerate(track_starts):
            # Find the start of the actual track content
            content_start = content.find("{", start) + 1

            # Find the end of the track
            if i < len(track_starts) - 1:
                content_end = track_starts[i + 1]
            else:
                # For the last track, find the score section
                content_end = content.find("\\score")

            # Extract the track content
            track_content = content[content_start:content_end].strip()
            if track_content.endswith("}"):
                track_content = track_content[:-1].strip()

            tracks.append(track_content)

        # Split each track into bars
        track_bars = []
        for track in tracks:
            # Split by the bar symbol '|' but keep the symbol
            bars = []
            current_bar = ""

            # Handle nested brackets and quotes for proper parsing
            bracket_depth = 0
            in_quotes = False

            for char in track:
                current_bar += char

                if char == "{":
                    bracket_depth += 1
                elif char == "}":
                    bracket_depth -= 1
                elif char == '"' and (len(current_bar) == 0 or current_bar[-2] != "\\"):
                    in_quotes = not in_quotes

                # Only consider bar lines outside of brackets and quotes
                if char == "|" and bracket_depth == 0 and not in_quotes:
                    bars.append(current_bar.strip())
                    current_bar = ""

            # Add the last bar if there's content
            if current_bar.strip():
                bars.append(current_bar.strip())

            track_bars.append(bars)

        # Create the output content with parallelMusic
        output_content = f"{header}\n\\parallelMusic voiceA,voiceB {{\n"

        # Combine corresponding bars from both tracks
        max_bars = max(len(track_bars[0]), len(track_bars[1]))

        for i in range(max_bars):
            # Check if this is the last bar with \fine
            is_fine_bar = any(
                "\\fine" in bars[i] if i < len(bars) else False for bars in track_bars
            )

            # Add bar number comment (except for \fine)
            if not is_fine_bar:
                output_content += f"  %   bar {i+1}\n"

            # Add bars from each track
            for track_idx, bars in enumerate(track_bars):
                if i < len(bars):
                    output_content += f"  {bars[i]}\n"
                else:
                    # If a track has fewer bars, add a placeholder
                    output_content += "  r1 |\n"

            # Add a blank line between bars for readability
            if not is_fine_bar:
                output_content += "\n"

        # Close the parallelMusic section and add the | after \fine
        output_content = output_content.replace("\\fine\n", "\\fine |\n")
        output_content += "}\n"

        # Add the score section
        output_content += """\\score {
  \\new PianoStaff <<
    \\new Staff = "up" { \\voiceA }
    \\new Staff = "down" { \\voiceB }
  >>
  \\layout {}
  \\midi {}
}
"""

        # Write the output file
        output_path = input_path.with_stem(f"{input_path.stem}_parallel")
        with open(output_path, "w") as f:
            f.write(output_content)

        return output_path
