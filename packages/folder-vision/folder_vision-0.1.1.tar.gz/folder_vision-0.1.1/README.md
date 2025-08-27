# folder-vision

Simple FastAPI Hello World application that works everywhere.

## Quick Install & Run

### Option 1: pipx (Recommended)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath
# Restart your terminal, then:
pipx install folder-vision
folder-vision
```

### Option 2: pip + PATH fix

```bash
pip install folder-vision
# If you get "command not found", add Python scripts to PATH:
export PATH="$(python3 -m site --user-base)/bin:$PATH"
folder-vision
```

### Option 3: Direct module execution

```bash
pip install folder-vision
python3 -m folder_vision
```

Visit <http://127.0.0.1:8000/> after any method above.

## CLI Options

```bash
folder-vision --help
folder-vision --port 9000 --reload
folder-vision --version
# Short alias also available:
fv --port 3000
```

## Cross-Platform Installation Guide

### macOS

```bash
# Using Homebrew Python (recommended)
brew install python
pipx install folder-vision

# Using system Python  
python3 -m pip install --user folder-vision
export PATH="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update && sudo apt install python3 python3-pip
python3 -m pip install --user folder-vision
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

### Windows

```powershell
# Using Python from python.org or Microsoft Store
pip install folder-vision
# If command not found, add to PATH:
# %APPDATA%\Python\Python311\Scripts (adjust Python version)

# Or use module execution:
python -m folder_vision
```

### Windows (PowerShell one-liner)

```powershell
pip install folder-vision; python -m folder_vision
```

## Troubleshooting

### "Command not found" after pip install

**Problem**: The `folder-vision` script isn't on your PATH.

**Solutions**:

1. **Use pipx** (isolates CLI tools): `pipx install folder-vision`
2. **Add scripts dir to PATH**:

   ```bash
   # Find your scripts directory
   python3 -c "import sysconfig; print(sysconfig.get_paths()['scripts'])"
   # Add that directory to your PATH
   ```

3. **Run via module**: `python3 -m folder_vision`

### Virtual Environment Issues

If installing in a venv and the command isn't found:

```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install folder-vision
folder-vision  # should work now
```

### Permission Errors

On Linux/macOS, use `--user` flag:

```bash
python3 -m pip install --user folder-vision
```

### Python Version Conflicts

Ensure Python 3.9+:

```bash
python3 --version
# If older, install newer Python or use pyenv/conda
```

## Development Setup

```bash
git clone https://github.com/folder-vision/folder-vision
cd folder-vision
python3 -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -e .[dev]
pytest
```

## Distributable Zip

To create a zip you can share:

```bash
zip -r folder-vision.zip folder_vision requirements.txt README.md
```

Recipient would unzip, create venv, install requirements, and run uvicorn as above.

### Prebuilt Zip With Virtualenv (No Pip Needed On Client)

Build (on your machine):

```bash
make dist-zip
```

This produces `dist/folder-vision.zip` containing a `.venv` directory with dependencies pre-installed. On the target machine (same OS/architecture):

```bash
unzip folder-vision.zip
cd folder-vision
source .venv/bin/activate
python -m folder_vision  # or: uvicorn folder_vision.app:app
```

Note: Virtualenvs are not portable across OS types (Linux vs macOS vs Windows) and sometimes not across differing minor Python versions / architectures (arm64 vs x86_64). Use this when environments are similar.

## Packaging as Executable (Optional)

You can use `pip install pipx` then `pipx run pyinstaller` or just install pyinstaller inside venv:

```bash
pip install pyinstaller
pyinstaller -F -n folder-vision run.py
```

Executable will be in `dist/`.

On another machine (same OS + architecture):

```bash
./dist/folder-vision
```

If you need cross-platform binaries, repeat the build on each target platform.

## Publishing to PyPI

1. Update version in `pyproject.toml`.
2. Build artifacts:

```bash
python -m build
```

1. (First time) install twine: `pip install twine`.
1. Upload:

```bash
twine upload dist/*
```

1. Test install:

```bash
pip install --no-cache-dir folder-vision==<version>
folder-vision
```

For a private/internal distribution you can instead host a simple index (e.g. via an S3 static site) and use `pip install --index-url <url> folder-vision`.
