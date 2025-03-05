{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        # Python environment with all dependencies
        pythonEnv = pkgs.python311.withPackages (ps:
          with ps; [
            click
            pydub
            librosa
            torch
            python-dotenv
            mido
            # Add any other Python dependencies your project needs
          ]);

        # Application package
        audioPond = pkgs.stdenv.mkDerivation {
          name = "audio-pond";
          src = ./.;
          buildInputs = [ pythonEnv pkgs.ffmpeg pkgs.wine64 pkgs.lilypond ];
          installPhase = ''
            mkdir -p $out/bin
            mkdir -p $out/lib/audio-pond

            # Copy the source code
            cp -r src $out/lib/audio-pond/
            cp -r requirements.txt $out/lib/audio-pond/
            cp -r pyproject.toml $out/lib/audio-pond/

            # Create a wrapper script
            cat > $out/bin/audio-pond <<EOF
            #!/bin/sh
            export PYTHONPATH=$out/lib/audio-pond:\$PYTHONPATH
            exec ${pythonEnv}/bin/python -m src.audio_pond "\$@"
            EOF

            chmod +x $out/bin/audio-pond
          '';
        };

        # Docker image
        dockerImage = pkgs.dockerTools.buildLayeredImage {
          name = "audio-pond";
          tag = "latest";

          contents = [
            audioPond
            pythonEnv
            pkgs.ffmpeg
            pkgs.wine64
            pkgs.lilypond
            pkgs.bash
            pkgs.coreutils
            pkgs.cacert # For HTTPS requests
          ];

          config = {
            Cmd = [ "/bin/audio-pond" ];
            WorkingDir = "/data";
            Volumes = { "/data" = { }; };
          };
        };
      in {
        packages = {
          default = audioPond;
          docker = dockerImage;
        };

        devShells.default = pkgs.mkShell {
          venvDir = ".venv";
          packages = with pkgs;
            [ ffmpeg wine64 lilypond python311 stdenv.cc.cc.lib makeWrapper ]
            ++ (with pkgs.python311Packages; [ uv ruff ]);

          shellHook = ''
            if [ ! -d "$venvDir" ]; then
              echo "Creating new venv using uv..."
              uv venv "$venvDir"
            fi

            if [ -d "$venvDir" ] && [ ! -f "$venvDir/bin/.python-wrapped" ]; then
              echo "Wrapping Python with required libraries..."
              wrapProgram "$PWD/$venvDir/bin/python" \
                --prefix LD_LIBRARY_PATH : "${pkgs.stdenv.cc.cc.lib}/lib"
            fi

            echo "Activating venv..."
            source "$venvDir/bin/activate"
          '';
        };
      });
}
