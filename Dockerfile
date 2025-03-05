FROM nixos/nix:latest

# Copy the project files
WORKDIR /app
COPY . .

# Build the application using Nix
RUN nix-env -iA nixpkgs.git && mkdir -p /etc/nix && echo 'experimental-features = nix-command flakes' >>/etc/nix/nix.conf && nix build .#default

# Set up the runtime environment
WORKDIR /data
VOLUME /data

# Set the entrypoint
ENTRYPOINT ["/app/result/bin/audio-pond"]
