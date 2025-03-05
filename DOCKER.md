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
docker run -v $(pwd)/output:/data audio-pond:latest "https://www.youtube.com/watch?v=your-video-id"
```

This will:

- Mount the current directory's `output` folder to `/data` in the container
- Process the YouTube video and generate sheet music in the mounted directory

### Processing Local Files

To process local audio or MIDI files, you need to mount them into the container:

```bash
docker run -v $(pwd)/output:/data -v $(pwd)/input:/input audio-pond:latest --audio-file /input/your-audio-file.wav
```

### Other Options

The Docker container supports all the same options as the regular command-line interface:

```bash
docker run audio-pond:latest --help
```
