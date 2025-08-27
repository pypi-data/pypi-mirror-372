# folder-vision

Simple FastAPI Hello World application.

## Features

- FastAPI with a single `GET /` endpoint returning a JSON greeting.
- Uvicorn for development server.
- Packaged with `requirements.txt` for easy installation.
- CLI entrypoint for running the app.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn folder_vision.app:app --reload
```

### Install via pip (after publishing)

Once the project is uploaded to PyPI:

```bash
pip install folder-vision
folder-vision  # launches the server on port 8000
```

Then open <http://127.0.0.1:8000/>

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
