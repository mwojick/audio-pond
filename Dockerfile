FROM ubuntu:24.04

# Utilities needed to install Nix and fonts for LilyPond
RUN apt-get update && apt-get install -y \
    curl \
    xz-utils \
    fontconfig

# Install Nix
RUN curl -L https://nixos.org/nix/install | sh -s -- --daemon --yes

# Enable flakes
RUN mkdir -p /etc/nix
RUN echo "experimental-features = nix-command flakes" >/etc/nix/nix.conf

# Install direnv and nix-direnv
ENV PATH="/root/.nix-profile/bin:${PATH}"
RUN nix-env -iA nixpkgs.direnv nixpkgs.nix-direnv

WORKDIR /app

COPY flake.lock flake.nix .envrc ./

RUN echo 'eval "$(direnv hook bash)"' >>~/.bashrc
RUN bash -c 'eval "$(direnv hook bash)" && direnv allow && direnv export bash > /tmp/env_vars'

COPY requirements.txt ./
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    bash -c 'source /tmp/env_vars && uv pip install -r requirements.txt'

COPY src/ src/
ENTRYPOINT ["bash", "-c", "source /tmp/env_vars && .venv/bin/python -m src.audio_pond \"$@\"", "bash"]
