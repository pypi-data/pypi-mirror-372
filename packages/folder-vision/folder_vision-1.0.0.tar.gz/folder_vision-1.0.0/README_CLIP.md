# Folder Vision - CLIP Image Search 🔍

A powerful multimodal image search engine built with OpenAI's CLIP (Contrastive Language-Image Pre-training) model. Search through your image collections using natural language descriptions or find similar images using other images as queries.

## Features ✨

- **🔍 Text-to-Image Search**: Find images using natural language descriptions
- **🖼️ Image-to-Image Search**: Find similar images using another image as a query
- **🌐 Web Interface**: Beautiful, intuitive web UI for easy searching
- **⚡ CLI Interface**: Command-line tools for batch processing and automation
- **💾 Smart Caching**: Automatic embedding caching for fast subsequent searches
- **🚀 FastAPI Backend**: Modern, high-performance web API
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices

## Quick Start 🚀

### Installation

```bash
# Clone or download the repository
cd folder-vision

# Install dependencies
pip install -e .
```

### Web Interface

Start the web server:

```bash
fv serve --port 8000
```

Then open your browser to `http://localhost:8000` and enjoy the visual interface!

### Command Line Usage

Index your images:

```bash
fv index /path/to/your/images
```

Search with text:

```bash
fv search-text "a red car in the city"
```

Search with an image:

```bash
fv search-image /path/to/query_image.jpg
```

## How It Works 🧠

Folder Vision uses OpenAI's CLIP model to understand both images and text in the same semantic space. This allows for:

1. **Image Indexing**: Convert all your images into high-dimensional vector embeddings
2. **Text Understanding**: Convert your search queries into comparable vectors
3. **Similarity Matching**: Find the most similar images using cosine similarity
4. **Fast Retrieval**: Use cached embeddings for instant search results

## Web Interface Features 🌐

The web interface provides:

- **📁 Folder Indexing**: Point to any folder and index all images automatically
- **🔤 Text Search**: Type natural language descriptions to find matching images
- **🖼️ Visual Search**: Upload an image to find similar ones in your collection
- **📊 Statistics**: View indexing statistics and model information
- **🎨 Visual Results**: See thumbnail previews with similarity scores
- **📱 Responsive Design**: Works perfectly on all devices

## CLI Commands 💻

### Serve Web Interface
```bash
# Start web server (default: http://0.0.0.0:8000)
fv serve

# Custom host and port
fv serve --host localhost --port 3000

# Development mode with auto-reload
fv serve --reload
```

### Index Images
```bash
# Index all images in a folder
fv index /path/to/images

# Index without saving cache
fv index /path/to/images --no-cache
```

### Search Commands
```bash
# Text search (natural language)
fv search-text "sunset over mountains"
fv search-text "a cat sleeping on a couch" --top-k 5

# Image search (visual similarity)
fv search-image /path/to/query.jpg
fv search-image query.png --top-k 20

# JSON output for scripting
fv search-text "dogs playing" --format json
```

### Statistics
```bash
# View search engine statistics
fv stats
```

## API Endpoints 🔌

The FastAPI backend provides these endpoints:

- `GET /` - Web interface
- `POST /index` - Index a folder
- `GET /search/text` - Search by text query
- `POST /search/image` - Search by image upload
- `GET /image/{path}` - Serve image files
- `GET /stats` - Get statistics
- `GET /health` - Health check

## Supported Image Formats 📸

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- GIF (.gif)
- TIFF (.tiff)
- WebP (.webp)

## Performance & Optimization ⚡

- **GPU Support**: Automatically uses GPU if available (CUDA)
- **Batch Processing**: Efficient batch encoding of images
- **Smart Caching**: Embeddings are cached to disk for instant reloading
- **Memory Management**: Processes large collections without memory issues
- **Concurrent Processing**: Handles multiple search requests simultaneously

## Example Use Cases 💡

### Personal Photo Management
```bash
# Index your photo library
fv index ~/Pictures

# Find vacation photos
fv search-text "beach vacation sunset"

# Find similar photos to a favorite shot
fv search-image ~/Pictures/favorite_sunset.jpg
```

### Digital Asset Management
```bash
# Index product images
fv index /company/product_photos

# Find specific product types
fv search-text "red athletic shoes"
fv search-text "office furniture desk"
```

### Creative Workflows
```bash
# Index design assets
fv index /projects/design_assets

# Find inspiration
fv search-text "minimalist logo design"
fv search-text "modern interior architecture"
```

## System Requirements 🖥️

- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum, 8GB+ recommended for large collections
- **Storage**: Additional space for embedding cache files
- **GPU**: Optional but recommended for faster processing (CUDA-compatible)

## Model Information 🤖

- **Base Model**: OpenAI CLIP ViT-B/32
- **Embedding Dimension**: 512
- **Input Resolution**: 224x224 pixels
- **Vocabulary**: 49,408 tokens

## Advanced Configuration ⚙️

### Environment Variables

```bash
# Set custom cache directory
export CLIP_CACHE_DIR=/path/to/cache

# Disable GPU usage
export CUDA_VISIBLE_DEVICES=""
```

### Custom Model

You can use different CLIP models by modifying the code:

```python
# In clip_search.py
search_engine = CLIPImageSearch(model_name="openai/clip-vit-large-patch14")
```

## Troubleshooting 🔧

### Common Issues

**"No images indexed" error**:
- Make sure to run `fv index <folder_path>` first
- Check that the folder contains supported image formats

**Slow indexing**:
- Enable GPU acceleration if available
- Process smaller batches of images
- Use SSD storage for better I/O performance

**Memory errors**:
- Reduce batch size in the code
- Process images in smaller folders
- Increase system RAM

**Web interface not loading**:
- Check if port is already in use
- Try a different port: `fv serve --port 8080`
- Check firewall settings

## Development 👩‍💻

### Project Structure
```
folder-vision/
├── folder_vision/
│   ├── __init__.py
│   ├── app.py           # FastAPI web application
│   ├── cli.py           # Command-line interface
│   └── clip_search.py   # CLIP search engine
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- **OpenAI** for the incredible CLIP model
- **Hugging Face** for the transformers library
- **FastAPI** for the excellent web framework
- **PyTorch** for the deep learning foundation

## Support 💬

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing issues on GitHub
3. Create a new issue with detailed information
4. Include system information and error messages

---

**Made with ❤️ by the Folder Vision Team**

Start exploring your images in a whole new way! 🚀