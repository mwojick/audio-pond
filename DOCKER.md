# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container using Nix.

## Prerequisites

- [Nix package manager](https://nixos.org/download.html) with flakes enabled
- Docker (to run the container after it's built with Nix)

> **Note:** Due to the dependency on Wine for MidiToLily, the Docker image can only be built on x86_64 Linux platforms.

## Building the Docker Image

### Using Nix

1. Build the Docker image using Nix:

```bash
nix build .#docker
```

2. Load the image into Docker:

```bash
docker load < result
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

### All Options

The Docker container supports all the same options as the regular command-line interface:

```bash
docker run audio-pond:latest --help
```
