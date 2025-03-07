# Audio Pond

Convert piano music from YouTube or audio files into editable LilyPond files and sheet music.

## Docker

Audio Pond can be run in a Docker container, which includes all the necessary dependencies (ffmpeg, wine, lilypond, etc.). See [DOCKER.md](DOCKER.md) for instructions.

## Development

1. Clone this repository:

```bash
git clone https://github.com/mwojick/audio-pond.git
cd audio-pond
```

2. Set up the development environment:

#### Make sure nix (with flakes enabled), direnv, and nix-direnv are installed before running this

```bash
direnv allow
```

#### Install dependencies with [uv](https://github.com/astral-sh/uv)

```bash
uv pip install -r requirements.txt
```

Optional, in case wine doesn't work:

3. Download MidiToLily from https://github.com/victimofleisure/MidiToLily/releases

4. Create `.env` file with `MIDI2LILY_PATH` set to the path of the MidiToLily executable

## Usage

### Convert from YouTube:

```bash
python -m src.audio_pond https://www.youtube.com/watch?v=your-video-id --key 1=g,28=c
```

### Convert from local audio file:

```bash
python -m src.audio_pond --audio-file path/to/your/audio/file.wav
```

### Convert from local MIDI file:

```bash
python -m src.audio_pond --midi-file path/to/your/midi/file.mid
```

### Options:

- `--help`: Show help
- `--audio-file`: Process local audio file instead of YouTube URL
- `--midi-file`: Process local MIDI file directly, skipping transcription
- `--ly-file`: Use local LilyPond file directly, skipping transcription and LilyPond conversion
- `--output-dir`: Specify output directory (default: ./output)
- `--no-trim`: Skip trimming silence from start of MIDI file before conversion
- `--no-split`: Skip splitting MIDI file into treble and bass tracks
- `--time`: Time signature for LilyPond output
- `--key`: Key signature for LilyPond output
- `--quant`: Quantization value for LilyPond output

## Output Files

For each conversion, the following files will be generated in the output directory:

- `1_raw_audio.wav`: Extracted audio from source
- `2_transcription.midi`: Transcribed MIDI
- `2_transcription_trimmed.midi`: Transcribed MIDI with initial silence removed
- `2_transcription_split.midi`: Transcribed MIDI split into treble and bass tracks
- `3_lilypond.ly`: LilyPond notation
- `3_lilypond_parallel.ly`: LilyPond notation with parallelMusic (for easier editing)
- `4_sheet_music.pdf`: Sheet music
- `4_sheet_music.midi`: Sheet music in MIDI format

To inspect MIDI quality: https://signal.vercel.app/edit

## Tools Used

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (video download)
- [piano-transcription-inference](https://github.com/qiuqiangkong/piano_transcription_inference) (audio transcription)
- [mido](https://github.com/mido/mido) (midi processing)
- [MidiToLily](https://github.com/victimofleisure/MidiToLily) (midi to lilypond conversion)
- [lilypond](https://lilypond.org/) (lilypond to sheet music)
