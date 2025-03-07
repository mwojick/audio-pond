# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container.

## Relevant Files

- `flake.nix`: Defines the Nix development environment with system dependencies such as ffmpeg, wine, lilypond, etc.
- `Dockerfile`: Creates a Docker image using Nix for system dependencies and uv for Python dependencies

## Building the Docker Image

```bash
docker build -t audio-pond:latest .
```

## Running Commands

```bash
# Use the default with a YouTube URL
docker run -it --rm --gpus all -v /usr/lib/wsl/lib:/usr/lib/wsl/lib -v ~/piano_transcription_inference_data:/root/piano_transcription_inference_data -v $(pwd)/output:/app/output audio-pond:latest https://www.youtube.com/watch?v=your-video-id
```

- `/usr/lib/wsl/lib` directory is needed when running on Windows with WSL so pytorch can find the GPU. If you don't have an Nvidia GPU, the transcription model will fallback to using the CPU.
- `~/piano_transcription_inference_data` directory is needed to cache the piano transcription model.
- The local `output` directory is mounted at `/app/output` in the container.

Run with different arguments as needed:

```bash
# Process local audio file
docker run -it --rm --gpus all -v /usr/lib/wsl/lib:/usr/lib/wsl/lib -v ~/piano_transcription_inference_data:/root/piano_transcription_inference_data -v $(pwd)/output:/app/output audio-pond:latest --audio-file output/1_raw_audio.wav

# Process local MIDI file
docker run -it --rm -v $(pwd)/output:/app/output audio-pond:latest --midi-file output/2_transcription_split.midi --no-trim --no-split --key 1=g,28=c

# Process local LilyPond file
docker run -it --rm -v $(pwd)/output:/app/output audio-pond:latest --ly-file output/3_lilypond.ly

# Show help
docker run -it --rm audio-pond:latest --help
```
