# Audio Pond - Product Requirements Document

## 1. Product Overview

Audio Pond is a command-line tool that converts piano performances (from YouTube or audio files) into professional sheet music that can be edited with LilyPond. It provides a seamless pipeline from audio input to PDF sheet music output, utilizing state-of-the-art music transcription technology.

## 2. User Stories

### Primary Use Case

As a musician I want to convert piano performances from YouTube into sheet music so that I can study and play the pieces myself

### Secondary Use Case

As a musician I want to convert my own piano audio recordings into sheet music so that I can document and share my compositions

## 3. Technical Specifications

### Command Line Interface

```bash
# Primary usage (YouTube)
python audio-pond.py https://www.youtube.com/...

# Alternative usage (local audio)
python audio-pond.py --audio-file path/to/audio/file
```

### Technology Stack

- **Environment Management**: Nix + direnv
- **Package Management**: uv
- **Core Dependencies**:
  - yt-dlp (video download)
  - basic-pitch (audio transcription)
  - lilypond (music notation)
  - ffmpeg (audio processing)

### Output Files

For each conversion, the following files will be generated:

- `output.wav` (extracted audio from YouTube video)
- `output.midi` (transcribed MIDI)
- `output_midi.wav` (MIDI audio rendering)
- `output.ly` (LilyPond notation)
- `output.pdf` (sheet music)
