# Running Audio Pond in Docker

This guide explains how to build and run Audio Pond in a Docker container using Nix.

## Prerequisites

- [Nix package manager](https://nixos.org/download.html) with flakes enabled
- Docker (optional, if you want to run the container with Docker instead of Nix)

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

### Alternative: Direct Build with Docker

If you prefer to build with Docker directly (without using Nix to generate the image):

1. Create a Dockerfile in the project root:

```bash
cat > Dockerfile << 'EOF'
FROM nixos/nix:latest

# Copy the project files
WORKDIR /app
COPY . .

# Build the application using Nix
RUN nix-env -iA nixpkgs.git && \
    mkdir -p /etc/nix && \
    echo 'experimental-features = nix-command flakes' >> /etc/nix/nix.conf && \
    nix build .#default

# Set up the runtime environment
WORKDIR /data
VOLUME /data

# Set the entrypoint
ENTRYPOINT ["/app/result/bin/audio-pond"]
EOF
```

2. Build the Docker image:

```bash
docker build -t audio-pond .
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

## Troubleshooting

### Wine Issues

If you encounter issues with Wine in the container, you might need to set the `MIDI2LILY_PATH` environment variable:

```bash
docker run -v $(pwd)/output:/data -e MIDI2LILY_PATH=/path/to/MidiToLily.exe audio-pond:latest "https://www.youtube.com/watch?v=your-video-id"
```

### Permission Issues

If you encounter permission issues with the output files, you can run the container with your user ID:

```bash
docker run -v $(pwd)/output:/data -u $(id -u):$(id -g) audio-pond:latest "https://www.youtube.com/watch?v=your-video-id"
```
