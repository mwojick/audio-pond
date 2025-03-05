{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";
  };

  outputs = { self, nixpkgs }:
    let
      # Only support x86_64-linux because of wine dependency
      supportedSystems = [ "x86_64-linux" ];
      forEachSupportedSystem = f:
        nixpkgs.lib.genAttrs supportedSystems
        (system: f { pkgs = import nixpkgs { inherit system; }; });
    in {
      packages = forEachSupportedSystem ({ pkgs }: {
        default = let
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
        in pkgs.stdenv.mkDerivation {
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

        docker = let
          audioPond = self.packages.x86_64-linux.default;
          pythonEnv = pkgs.python311.withPackages
            (ps: with ps; [ click pydub librosa torch python-dotenv mido ]);
        in pkgs.dockerTools.buildLayeredImage {
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
      });

      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
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
    };
}
