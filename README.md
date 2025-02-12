# Audio Pond

Convert piano performances from YouTube or audio files into lilypond files and sheet music.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/mwojick/audio-pond.git
cd audio-pond
```

2. Set up the development environment:

```bash
# Make sure direnv and nix-direnv are installed before running this
direnv allow

# Compile and install dependencies with [uv](https://github.com/astral-sh/uv)
uv pip compile pyproject.toml -o requirements.txt && uv pip install -r requirements.txt
```

## Usage

### Convert from YouTube:

```bash
python src/audio_pond.py https://www.youtube.com/watch?v=your-video-id
```

### Convert from local audio file:

```bash
python src/audio_pond.py --audio-file path/to/your/audio/file.wav
```

### Convert from local MIDI file:

```bash
python src/audio_pond.py --midi-file path/to/your/midi/file.mid
```

### Options:

- `--audio-file`: Process a local audio file instead of YouTube URL
- `--midi-file`: Process a local MIDI file instead of transcribing from audio
- `--output-dir`: Specify output directory (default: ./output)

## Output Files

For each conversion, the following files will be generated in the output directory:

- `output.wav`: Extracted audio from source
- `output.midi`: Transcribed MIDI
- `output.ly`: LilyPond notation
- `output.pdf`: Sheet music

### To inspect MIDI quality: https://signal.vercel.app/edit
