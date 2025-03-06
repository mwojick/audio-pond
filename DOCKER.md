# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container.

## Files

- `flake.nix`: Defines the Nix development environment with system dependencies
- `Dockerfile`: Creates a Docker image using Nix for system dependencies and uv for Python dependencies

## Building the Docker Image

```bash
docker build -t audio-pond:latest .
```

## Running Commands

```bash
# lib/wsl directory is needed when running on Windows with WSL so pytorch can find the GPU
# ~/piano_transcription_inference_data directory is needed for the piano transcription model
docker run --rm --gpus all -v /usr/lib/wsl/lib:/usr/lib/wsl/lib -v ~/piano_transcription_inference_data:/root/piano_transcription_inference_data -v $(pwd)/output:/app/output audio-pond:latest https://www.youtube.com/watch?v=your-video-id
```

The local `output` directory is mounted at `/app/output` in the container.

Run with different arguments as needed:

```bash
docker run --rm --gpus all -v /usr/lib/wsl/lib:/usr/lib/wsl/lib -v ~/piano_transcription_inference_data:/root/piano_transcription_inference_data -v $(pwd)/output:/app/output audio-pond:latest --audio-file output/1_raw_audio.wav
docker run --gpus all --rm -v $(pwd)/output:/app/output audio-pond:latest --midi-file output/2_transcription_split.midi --no-trim --no-split --key 1=g,28=c
docker run --gpus all --rm -v $(pwd)/output:/app/output audio-pond:latest --ly-file output/3_lilypond.ly
docker run --rm audio-pond:latest --help
```
