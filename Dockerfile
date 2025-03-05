FROM nixos/nix:latest

WORKDIR /app

# Copy your flake and source code
COPY flake.nix .
COPY src/ /app/src/
COPY requirements.txt .

# Enable Nix flakes
RUN mkdir -p /etc/nix
RUN echo "experimental-features = nix-command flakes" >/etc/nix/nix.conf

# Install Python dependencies during build
RUN nix develop -c uv pip install -r requirements.txt

# Create a volume for data
VOLUME /data
WORKDIR /data

ENTRYPOINT [ "nix develop -c python -m src.audio_pond $@" ]
