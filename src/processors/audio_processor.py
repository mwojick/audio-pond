"""Main audio processor for Audio Pond."""

import os
from pathlib import Path
from dataclasses import dataclass

from src.processors.source_processor import SourceProcessor
from src.processors.midi_transcriber import MidiTranscriber
from src.processors.midi_processor import MidiProcessor
from src.processors.lilypond_converter import LilypondConverter


@dataclass
class ProcessorConfig:
    """Configuration for the audio processing pipeline."""

    source: str
    output_dir: Path
    audio_file: bool = False
    midi_file: bool = False
    ly_file: bool = False
    no_trim: bool = False
    no_split: bool = False
    time: str = "1=4/4"
    key: str = "1=c"
    quant: str = "16"


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

    def run(self, config: ProcessorConfig) -> Path:
        """Run the complete audio processing pipeline based on the provided configuration.

        Args:
            config: Configuration parameters for the processing pipeline

        Returns:
            Path to the generated sheet music

        Raises:
            Exception: If any step in the pipeline fails
        """
        if config.ly_file:
            ly_path = Path(config.source)
        elif config.midi_file:
            midi_path = Path(config.source)
        else:
            if config.audio_file:
                audio_path = self.source_processor.process_audio_file(
                    Path(config.source)
                )
            else:
                audio_path = self.source_processor.process_youtube(config.source)

            midi_path = self.midi_transcriber.transcribe_audio(audio_path)

        if not config.ly_file:
            if not config.no_trim:
                midi_path = self.midi_processor.trim_midi_silence(midi_path)

            if not config.no_split:
                midi_path = self.midi_processor.split_midi_tracks(midi_path)

            ly_path = self.lilypond_converter.midi_to_lilypond(
                midi_path, time=config.time, key=config.key, quant=config.quant
            )

        ly_path = self.lilypond_converter.transform_to_parallel_music(ly_path)
        # absolute path needed in docker container
        sheet_music_path = self.lilypond_converter.render_sheet_music(
            ly_path.absolute()
        )

        return sheet_music_path
