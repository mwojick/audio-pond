# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container.

## Files

- `flake.nix`: Defines the Nix development environment with system dependencies
- `Dockerfile`: Creates a Docker image using Nix for system dependencies and uv for Python dependencies

## Building the Docker Image

```bash
docker build -t audio-pond:latest .
```

## Running the Container

### Basic Usage

```bash
docker run -v $(pwd)/output:/app/output audio-pond:latest "https://www.youtube.com/watch?v=your-video-id"
```

This will:

- Mount the current directory's `output` folder to `/app/output` in the container
- Process the YouTube video and generate sheet music in the mounted directory

### Processing Local Files

```bash
docker run -v $(pwd)/output:/app/output audio-pond:latest --audio-file /app/output/your-audio-file.wav
```

### Other Options

```bash
docker run audio-pond:latest --help
```
