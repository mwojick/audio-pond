"""MIDI transcriber for Audio Pond."""

import os
from pathlib import Path
import librosa
from piano_transcription_inference import PianoTranscription, sample_rate
from src.utils.gpu_utils import check_gpu


class MidiTranscriber:
    """Handles audio to MIDI transcription."""

    def __init__(self, output_dir: Path):
        """Initialize the MIDI transcriber.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Check GPU for transcription
        gpu_available = check_gpu()
        self.device = "cuda" if gpu_available else "cpu"

    def transcribe_audio(self, audio_path: Path) -> Path:
        """Transcribe audio to MIDI using Piano Transcription Inference.

        Args:
            audio_path: Path to the input audio file

        Returns:
            Path to the transcribed MIDI file
        """
        # Load audio
        audio, _ = librosa.load(path=audio_path, sr=sample_rate, mono=True)

        # Transcriptor
        transcriptor = PianoTranscription(
            device=self.device, checkpoint_path=None
        )  # device: 'cuda' | 'cpu'

        midi_output_path = self.output_dir / "2_transcription.midi"

        # Transcribe and write out to MIDI file
        transcribed_dict = transcriptor.transcribe(audio, str(midi_output_path))
        print(transcribed_dict)
        return midi_output_path
