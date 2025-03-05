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
      packages = forEachSupportedSystem ({ pkgs }:
        let
          # Base Python without packages
          python = pkgs.python311;

          audioPond = pkgs.stdenv.mkDerivation {
            name = "audio-pond";
            src = ./.;
            # Include uv for dependency management
            nativeBuildInputs = [ pkgs.python311Packages.uv ];
            buildInputs = [ python ];
            installPhase = ''
              mkdir -p $out/bin
              mkdir -p $out/lib/audio-pond

              # Copy the source code
              cp -r src $out/lib/audio-pond/
              cp -r requirements.txt $out/lib/audio-pond/
              cp -r pyproject.toml $out/lib/audio-pond/

              # Create a virtual environment with uv
              cd $out/lib/audio-pond
              ${pkgs.python311Packages.uv}/bin/uv venv .venv

              # Install dependencies using uv
              ${pkgs.python311Packages.uv}/bin/uv pip install -r requirements.txt --no-cache

              # Create a wrapper script
              cat > $out/bin/audio-pond <<EOF
              #!/bin/sh
              export PYTHONPATH=$out/lib/audio-pond:\$PYTHONPATH
              $out/lib/audio-pond/.venv/bin/python -m src.audio_pond "\$@"
              EOF

              chmod +x $out/bin/audio-pond
            '';
          };

          dockerImage = pkgs.dockerTools.buildLayeredImage {
            name = "audio-pond";
            tag = "latest";

            contents = [
              audioPond
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
          default = audioPond;
          docker = dockerImage;
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
