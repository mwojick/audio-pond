# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container.

## Files

- `flake.nix`: Defines the Nix development environment with system dependencies
- `Dockerfile`: Creates a Docker image using Nix for system dependencies and uv for Python dependencies

## Building the Docker Image

```bash
docker build -t audio-pond:latest .
```

## Creating a Container

```bash
docker create --name audio-pond-container -v $(pwd)/output:/app/output audio-pond:latest
```

The local `output` directory is mounted at `/app/output` in the container.

## Running Commands with the Container

```bash
docker start -a audio-pond-container https://www.youtube.com/watch?v=your-video-id
```

Run with different arguments as needed:

```bash
docker start -a audio-pond-container --audio-file /app/output/your-audio-file.wav
```

If you need to update the image, remove the container and create a new one:

```bash
docker rm audio-pond-container
# Then create a new container as shown above
```
