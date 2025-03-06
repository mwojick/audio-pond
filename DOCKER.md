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
docker run --rm --gpus all -v $(pwd)/output:/app/output audio-pond:latest https://www.youtube.com/watch?v=your-video-id
```

The local `output` directory is mounted at `/app/output` in the container.

Run with different arguments as needed:

```bash
docker run --rm --gpus all -v $(pwd)/output:/app/output audio-pond:latest --audio-file /app/output/your-audio-file.wav
docker run --rm --gpus all -v $(pwd)/output:/app/output audio-pond:latest --help
```
