FROM nixos/nix:latest

WORKDIR /app

COPY flake.nix .
COPY flake.lock .
COPY requirements.txt .
COPY src/ src/

RUN mkdir -p /etc/nix
RUN echo "experimental-features = nix-command flakes" >/etc/nix/nix.conf

RUN nix develop -c uv pip install -r requirements.txt

ENTRYPOINT ["sh", "-c", "nix develop -c python -m src.audio_pond \"$@\"", "--"]
