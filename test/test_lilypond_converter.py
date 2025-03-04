#!/usr/bin/env python3
"""Test script for the LilypondConverter's transform_to_parallel_music function."""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processors.lilypond_converter import LilypondConverter


def main():
    """Test the transform_to_parallel_music function."""
    # Create a converter instance
    output_dir = Path("test")
    converter = LilypondConverter(output_dir)

    # Path to the input file
    input_path = Path("test/input.ly")

    # Transform the file
    output_path = converter.transform_to_parallel_music(input_path)

    print(f"Transformed file saved to: {output_path}")

    # Optionally, compare with the expected output
    expected_output_path = Path("test/output.ly")
    if expected_output_path.exists():
        with open(output_path, "r") as f:
            actual_output = f.read()
        with open(expected_output_path, "r") as f:
            expected_output = f.read()

        # Simple comparison - in a real test you might want to use a more sophisticated comparison
        if actual_output.strip() == expected_output.strip():
            print("Output matches expected result!")
        else:
            print("Output differs from expected result.")
            # You could add more detailed comparison here


if __name__ == "__main__":
    main()
