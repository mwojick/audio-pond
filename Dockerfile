FROM ubuntu:22.04

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    xz-utils \
    build-essential \
    pkg-config \
    sudo \
    fontconfig
RUN rm -rf /var/lib/apt/lists/*

# Install Nix
RUN curl -L https://nixos.org/nix/install | sh -s -- --daemon --yes

# Configure Nix
RUN mkdir -p /etc/nix
RUN echo "experimental-features = nix-command flakes" >/etc/nix/nix.conf

# Install direnv and nix-direnv
ENV PATH="/root/.nix-profile/bin:${PATH}"
RUN . /root/.nix-profile/etc/profile.d/nix.sh
RUN nix-env -iA nixpkgs.direnv nixpkgs.nix-direnv

WORKDIR /app

COPY flake.lock .
COPY flake.nix .
COPY .envrc .

# Set up direnv and load the environment
RUN echo 'eval "$(direnv hook bash)"' >>~/.bashrc
RUN . /root/.nix-profile/etc/profile.d/nix.sh && direnv allow .
# This runs a bash shell that loads direnv, then executes the commands
RUN . /root/.nix-profile/etc/profile.d/nix.sh
RUN bash -c 'eval "$(direnv hook bash)" && direnv allow . && direnv export bash > /tmp/env_vars'

# Use the environment variables for subsequent commands
COPY requirements.txt .
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    bash -c 'source /tmp/env_vars && uv pip install -r requirements.txt'

COPY src/ src/
ENTRYPOINT ["bash", "-c", "source /tmp/env_vars && .venv/bin/python -m src.audio_pond \"$@\"", "bash"]
