# Audio Pond - Product Requirements Document

## 1. Product Overview

Audio Pond is a command-line tool that converts piano performances (from YouTube or audio files) into professional sheet music that can be edited with LilyPond. It provides a seamless pipeline from audio input to PDF sheet music output, utilizing state-of-the-art music transcription technology.

## 2. User Stories

### First Use Case

As a musician I want to convert piano performances from YouTube into lilypond and sheet music

### Second Use Case

As a musician I want to convert my own piano audio into lilypond and sheet music

### Third Use Case

As a musician I want to convert already existing MIDI files into lilypond and sheet music

## 3. Technical Specifications

### Command Line Interface

```bash
# Primary usage (YouTube)
python src/audio_pond.py https://www.youtube.com/...

# Alternative usage (local audio)
python src/audio_pond.py --audio-file path/to/audio/file

# Alternative usage (local MIDI)
python src/audio_pond.py --midi-file path/to/midi/file
```

### Technology Stack

- **Environment Management**: Nix + direnv
- **Package Management**: uv
- **Core Dependencies**:
  - yt-dlp (video download)
  - piano-transcription-inference (audio transcription)
  - torch (GPU acceleration)
  - lilypond (midi to lilypond conversion)
  - ffmpeg (audio processing)

### Output Files

For each conversion, the following files will be generated:

- `output.wav` (extracted audio from YouTube video)
- `output.midi` (transcribed MIDI)
- `output.ly` (LilyPond notation)
- `output.pdf` (sheet music)
