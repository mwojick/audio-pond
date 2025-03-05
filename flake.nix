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

      getPython = pkgs: pkgs.python312;
      getPythonPackages = pkgs: pkgs.python312Packages;
      getRuntimeDeps = pkgs: with pkgs; [ ffmpeg wine64 lilypond ];
    in {
      packages = forEachSupportedSystem ({ pkgs }:
        let
          python = getPython pkgs;
          pythonPackages = getPythonPackages pkgs;
          runtimeDeps = getRuntimeDeps pkgs;

          audioPond = pkgs.stdenv.mkDerivation {
            name = "audio-pond";
            src = ./.;
            nativeBuildInputs = [ pkgs.makeWrapper ];
            buildInputs = [ python ];

            installPhase = ''
              mkdir -p $out/bin
              mkdir -p $out/lib/audio-pond

              # Copy the source code
              cp -r src $out/lib/audio-pond/

              # Create a wrapper script
              makeWrapper ${python}/bin/python $out/bin/audio-pond \
                --set PYTHONPATH $out/lib/audio-pond:${
                  pkgs.lib.makeSearchPath
                  "lib/python${python.pythonVersion}/site-packages" (
                    # Add Python dependencies from requirements.txt
                    with pythonPackages; [
                      # Core dependencies
                      numpy
                      click
                      python-dotenv
                      pydub

                      # Librosa and its dependencies
                      librosa
                      lazy-loader
                      audioread
                      soundfile
                      pooch
                      scikit-learn
                      joblib
                      decorator
                      numba
                      scipy

                      # Other dependencies
                      torch
                      mido
                      yt-dlp
                      requests
                      piano-transcription-inference
                    ])
                } \
                --add-flags "-m src.audio_pond"

              chmod +x $out/bin/audio-pond
            '';
          };

          dockerImage = pkgs.dockerTools.buildLayeredImage {
            name = "audio-pond";
            tag = "latest";

            contents = [ audioPond ] ++ runtimeDeps
              ++ [ pkgs.bash pkgs.coreutils pkgs.cacert pkgs.stdenv.cc.cc.lib ];

            config = {
              Cmd = [ "${audioPond}/bin/audio-pond" ];
              WorkingDir = "/data";
              Volumes = { "/data" = { }; };
              Env = [
                "LD_LIBRARY_PATH=${
                  pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib ]
                }"
              ];
            };
          };
        in {
          default = audioPond;
          docker = dockerImage;
        });

      devShells = forEachSupportedSystem ({ pkgs }:
        let
          python = getPython pkgs;
          pythonPackages = getPythonPackages pkgs;
          runtimeDeps = getRuntimeDeps pkgs;
        in {
          default = pkgs.mkShell {
            venvDir = ".venv";
            packages = runtimeDeps
              ++ [ python pkgs.stdenv.cc.cc.lib pkgs.makeWrapper ]
              ++ (with pythonPackages; [ uv ruff ]);

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
