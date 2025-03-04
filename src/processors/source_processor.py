"""Source processor for Audio Pond."""

from pathlib import Path
import yt_dlp
from pydub import AudioSegment


class SourceProcessor:
    """Handles downloading from YouTube or processing local files."""

    def __init__(self, output_dir: Path):
        """Initialize the source processor.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir

    def process_youtube(self, url: str) -> Path:
        """Download YouTube video and extract audio.

        Args:
            url: YouTube URL

        Returns:
            Path to the downloaded audio file
        """
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
        """Process local audio file to WAV format.

        Args:
            audio_path: Path to the input audio file

        Returns:
            Path to the processed WAV file
        """
        audio_output_path = self.output_dir / "1_raw_audio.wav"
        audio = AudioSegment.from_file(str(audio_path))
        audio.export(str(audio_output_path), format="wav")
        return audio_output_path
