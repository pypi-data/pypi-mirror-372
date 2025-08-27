# Folder Vision - CLIP Image Search 🔍

> Multimodal image search engine powered by OpenAI's CLIP model

Folder Vision enables you to search through your image collections using natural language descriptions or visual similarity. Simply point it at a folder, and it automatically indexes your images for instant semantic search.

## ✨ Features

- **🔍 Text-to-Image Search**: Find images using natural language descriptions
- **🖼️ Image-to-Image Search**: Find visually similar images  
- **🌐 Web Interface**: Beautiful, responsive web UI for browsing and searching
- **⚡ Auto-Indexing**: Automatically indexes images from your current directory
- **🧠 AI-Powered**: Uses OpenAI's CLIP model for semantic understanding
- **📊 Image Clustering**: Automatically group similar images together
- **🖥️ Cross-Platform**: Works on Windows, macOS, and Linux
- **📱 Gallery View**: Browse your entire image collection with pagination
- **🎯 Similarity Search**: Find images similar to any selected image

## 🚀 Quick Start

### Install with uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install folder-vision
uv tool install folder-vision

# Navigate to a folder with images and start the server
cd /path/to/your/images
folder-vision serve
```

### Install with pip

```bash
pip install folder-vision

# Navigate to a folder with images and start the server  
cd /path/to/your/images
folder-vision serve
```

### Install with pipx

```bash
pipx install folder-vision
cd /path/to/your/images
folder-vision serve
```

## 📖 Usage

### Web Interface

1. **Start the server** in a directory containing images:

   ```bash
   cd ~/Pictures  # or any folder with images
   folder-vision serve
   ```

2. **Open your browser** to `http://localhost:8000`

3. **Search your images**:
   - Type natural language queries like "sunset over mountains" or "cat sleeping"
   - Upload an image to find visually similar ones
   - Browse the gallery view to see all indexed images
   - Explore automatic image clusters

### Command Line Interface

```bash
# Start web server (auto-indexes current directory)
folder-vision serve --port 8000

# Index a specific folder
folder-vision index /path/to/images

# Search by text
folder-vision search-text "red sports car"

# Search by image  
folder-vision search-image /path/to/query.jpg

# Get statistics
folder-vision stats

# Cluster images automatically
folder-vision cluster --method auto
```

## 🔧 Advanced Usage

### Custom Host and Port

```bash
folder-vision serve --host 0.0.0.0 --port 3000
```

### Development Mode

```bash
folder-vision serve --reload
```

### Indexing Options

```bash
# Index without saving cache
folder-vision index /path/to/images --no-cache

# Limit search depth
folder-vision index /path/to/images --max-depth 1
```

## 🛠️ Installation Options

## 🛠️ Installation Methods

### Option 1: uv (Recommended)

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install folder-vision
uv tool install folder-vision
folder-vision serve
```

### Option 2: pipx (Isolated Installation)

```bash
# Install pipx if you don't have it
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install folder-vision
pipx install folder-vision
folder-vision serve
```

### Option 3: pip + PATH fix

```bash
pip install folder-vision

# If you get "command not found", add Python scripts to PATH:
export PATH="$(python3 -m site --user-base)/bin:$PATH"
folder-vision serve
```

### Option 4: Direct module execution

```bash
pip install folder-vision
python3 -m folder_vision serve
```

## 🖥️ Platform-Specific Installation

### macOS

```bash
# Using Homebrew Python (recommended)
brew install python uv
uv tool install folder-vision

# Using system Python  
python3 -m pip install --user folder-vision
export PATH="$HOME/Library/Python/$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')/bin:$PATH"
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and uv
sudo apt update && sudo apt install python3 python3-pip curl
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install folder-vision
uv tool install folder-vision
```

### Windows

```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install folder-vision
uv tool install folder-vision

# Or use pip
pip install folder-vision
```

## ⚙️ System Requirements

- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum, 8GB+ recommended for large collections
- **Storage**: Additional space for embedding cache files
- **GPU**: Optional but recommended for faster processing (CUDA-compatible)

## 🔍 Example Use Cases

### Personal Photo Management

```bash
# Index your photo library
cd ~/Pictures
folder-vision serve

# Find vacation photos
folder-vision search-text "beach vacation sunset"

# Find similar photos to a favorite shot
folder-vision search-image ~/Pictures/favorite_sunset.jpg
```

### Digital Asset Management

```bash
# Index product images
cd /company/product_photos
folder-vision serve

# Find specific product types
folder-vision search-text "red athletic shoes"
folder-vision search-text "office furniture desk"
```

### Creative Workflows

```bash
# Index design assets
cd /projects/design_assets
folder-vision serve

# Find inspiration
folder-vision search-text "minimalist logo design"
folder-vision search-text "modern interior architecture"
```

## 🛠️ Troubleshooting

### "Command not found" after installation

**Problem**: The `folder-vision` command isn't on your PATH.

**Solutions**:

1. **Use uv** (recommended): `uv tool install folder-vision`
2. **Use pipx**: `pipx install folder-vision`
3. **Add scripts dir to PATH**:

   ```bash
   # Find your scripts directory
   python3 -c "import sysconfig; print(sysconfig.get_paths()['scripts'])"
   # Add that directory to your PATH
   ```

4. **Run via module**: `python3 -m folder_vision serve`

### Memory Issues

If you encounter memory errors with large image collections:

- Reduce batch size by processing smaller folders
- Close other applications to free up RAM
- Use a machine with more memory for very large collections

### Slow Indexing

To improve indexing performance:

- Use SSD storage for better I/O performance
- Enable GPU acceleration if available
- Process images in smaller batches

### No Images Found

Make sure you're running the command from a directory that contains images:

```bash
cd /path/to/folder/with/images
folder-vision serve
```

Supported formats: JPG, JPEG, PNG, GIF, BMP, TIFF

## 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/folder-vision/folder-vision
cd folder-vision

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Start development server
folder-vision serve --reload
```

## 📦 Building and Publishing

### Build the Package

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

### Publish to PyPI

```bash
# Install twine
pip install twine

# Upload to PyPI
twine upload dist/*
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🔗 Links

- **Homepage**: [https://github.com/folder-vision/folder-vision](https://github.com/folder-vision/folder-vision)
- **Documentation**: [README_CLIP.md](README_CLIP.md)
- **Issues**: [https://github.com/folder-vision/folder-vision/issues](https://github.com/folder-vision/folder-vision/issues)

---

Made with ❤️ by the Folder Vision Team
