"""Main audio processor for Audio Pond."""

import os
from pathlib import Path

from src.processors.source_processor import SourceProcessor
from src.processors.midi_transcriber import MidiTranscriber
from src.processors.midi_processor import MidiProcessor
from src.processors.lilypond_converter import LilypondConverter


class AudioProcessor:
    """Main processor that coordinates the audio processing pipeline."""

    def __init__(self, output_dir: Path):
        """Initialize the audio processor.

        Args:
            output_dir: Directory for output files
        """
        os.makedirs(output_dir, exist_ok=True)

        self.source_processor = SourceProcessor(output_dir)
        self.midi_transcriber = MidiTranscriber(output_dir)
        self.midi_processor = MidiProcessor(output_dir)
        self.lilypond_converter = LilypondConverter(output_dir)

    def process_youtube(self, url: str) -> Path:
        return self.source_processor.process_youtube(url)

    def process_audio_file(self, audio_path: Path) -> Path:
        return self.source_processor.process_audio_file(audio_path)

    def transcribe_audio(self, audio_path: Path) -> Path:
        return self.midi_transcriber.transcribe_audio(audio_path)

    def trim_midi_silence(self, midi_path: Path) -> Path:
        return self.midi_processor.trim_midi_silence(midi_path)

    def split_midi_tracks(self, midi_path: Path) -> Path:
        return self.midi_processor.split_midi_tracks(midi_path)

    def midi_to_lilypond(
        self, midi_path: Path, time: str, key: str, quant: str
    ) -> Path:
        return self.lilypond_converter.midi_to_lilypond(midi_path, time, key, quant)

    def transform_to_parallel_music(self, ly_path: Path) -> Path:
        return self.lilypond_converter.transform_to_parallel_music(ly_path)

    def render_sheet_music(self, ly_path: Path) -> Path:
        return self.lilypond_converter.render_sheet_music(ly_path)
