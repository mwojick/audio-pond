# Audio Pond

## Setup

```bash
# Make sure direnv and nix-direnv are installed before running this
direnv allow
```

### Compile and install dependencies with [uv](https://github.com/astral-sh/uv)

```bash
uv pip compile pyproject.toml -o requirements.txt && uv pip install -r requirements.txt
```
