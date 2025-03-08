FROM nixos/nix:2.26.3

# Enable flakes
RUN mkdir -p /etc/nix
RUN echo "experimental-features = nix-command flakes" >/etc/nix/nix.conf

# Install direnv and nix-direnv
RUN nix profile install nixpkgs#direnv nixpkgs#nix-direnv
RUN mkdir -p /root/.config/direnv
RUN echo 'source $HOME/.nix-profile/share/nix-direnv/direnvrc' >/root/.config/direnv/direnvrc

WORKDIR /app

COPY flake.lock flake.nix .envrc ./
RUN direnv allow

COPY requirements.txt ./
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    bash -c 'direnv exec . uv pip install -r requirements.txt'

COPY src/ src/
ENTRYPOINT ["bash", "-c", "direnv exec . python -m src.audio_pond \"$@\"", "bash"]
