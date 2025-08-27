import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import pkg_resources

import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from . import __version__
from .clip_search import CLIPImageSearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Folder Vision - CLIP Image Search", 
    version=__version__,
    description="Multimodal image search using CLIP (Contrastive Language-Image Pre-training)"
)

# Global search engine instance
search_engine: Optional[CLIPImageSearch] = None
indexed_folder: Optional[str] = None

# Create uploads directory for temporary files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Get package directory for static files
try:
    package_dir = Path(pkg_resources.resource_filename('folder_vision', ''))
    static_dir = package_dir / "static"
    html_dir = package_dir / "html"
except:
    # Fallback to current directory structure for development
    package_dir = Path(__file__).parent
    static_dir = package_dir / "static"
    html_dir = package_dir / "html"
    
    # If not found in package, try parent directory (development mode)
    if not static_dir.exists():
        static_dir = package_dir.parent / "static"
    if not html_dir.exists():
        html_dir = package_dir.parent / "html"

# Mount static files if they exist
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Also check for legacy locations
legacy_static = Path("static")
legacy_html = Path("html")
if legacy_static.exists() and not static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
if not html_dir.exists() and legacy_html.exists():
    html_dir = legacy_html


@app.on_event("startup")
async def startup_event():
    """Initialize the CLIP search engine on startup."""
    global search_engine, indexed_folder
    try:
        search_engine = CLIPImageSearch()
        logger.info("CLIP search engine initialized successfully")
        
        # Try to load existing cache
        if search_engine.load_embeddings_cache():
            logger.info("Loaded existing embeddings cache")
        
        # Auto-index the current working directory with max depth of 2
        current_dir = os.getcwd()
        logger.info(f"Auto-indexing current directory: {current_dir}")
        
        try:
            result = search_engine.index_folder(current_dir, max_depth=2)
            indexed_folder = current_dir
            logger.info(f"Auto-indexing complete: {result['successfully_indexed']} images indexed")
        except Exception as e:
            logger.warning(f"Auto-indexing failed: {e}")
            # Continue without auto-indexing if it fails
            
    except Exception as e:
        logger.error(f"Failed to initialize CLIP search engine: {e}")
        search_engine = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the home page."""
    html_file = html_dir / "home.html"
    if html_file.exists():
        return FileResponse(html_file)
    else:
        # Fallback to embedded HTML if file doesn't exist
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html><head><title>Folder Vision</title></head>
        <body>
        <h1>Folder Vision</h1>
        <p>HTML file not found. Please ensure html/home.html exists.</p>
        </body></html>
        """)


@app.get("/gallery", response_class=HTMLResponse)
async def gallery():
    """Serve the gallery page."""
    html_file = html_dir / "gallery.html"
    if html_file.exists():
        return FileResponse(html_file)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html><head><title>Gallery - Folder Vision</title></head>
        <body>
        <h1>Gallery</h1>
        <p>Gallery page not found.</p>
        </body></html>
        """)


@app.get("/search", response_class=HTMLResponse)
async def search_page():
    """Serve the search results page."""
    html_file = html_dir / "results.html"
    if html_file.exists():
        return FileResponse(html_file)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html><head><title>Search Results - Folder Vision</title></head>
        <body>
        <h1>Search Results</h1>
        <p>Search results page not found.</p>
        </body></html>
        """)


@app.get("/cluster", response_class=HTMLResponse)
async def cluster_page():
    """Serve the cluster page."""
    html_file = html_dir / "cluster.html"
    if html_file.exists():
        return FileResponse(html_file)
    else:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html><head><title>Cluster - Folder Vision</title></head>
        <body>
        <h1>Image Clustering</h1>
        <p>Cluster page not found.</p>
        </body></html>
        """)


@app.get("/auto-index-status")
async def get_auto_index_status():
    """Get the status of auto-indexing."""
    global search_engine, indexed_folder
    
    if search_engine is None:
        return {"status": "error", "message": "Search engine not initialized"}
    
    return {
        "status": "ready" if indexed_folder else "no_index",
        "indexed_folder": indexed_folder,
        "total_images": len(search_engine.image_paths) if search_engine.image_paths else 0,
        "current_directory": os.getcwd()
    }


@app.post("/index")
async def index_folder(request: Dict[str, str]):
    """Index all images in a folder for search."""
    global search_engine, indexed_folder
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    folder_path = request.get("folder_path")
    if not folder_path:
        raise HTTPException(status_code=400, detail="folder_path is required")
    
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
    
    max_depth = request.get("max_depth")
    if max_depth is not None:
        try:
            max_depth = int(max_depth)
        except ValueError:
            raise HTTPException(status_code=400, detail="max_depth must be an integer")
    
    try:
        result = search_engine.index_folder(folder_path, max_depth=max_depth)
        indexed_folder = folder_path
        return result
    except Exception as e:
        logger.error(f"Error indexing folder {folder_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/clear")
async def clear_index():
    """Clear in-memory index (does not delete cache file)."""
    global search_engine
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    try:
        result = search_engine.clear_index()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/text")
async def search_by_text(query: str = Query(..., description="Text query to search for"), 
                        top_k: int = Query(10, description="Number of top results to return")):
    """Search images using text query."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        results = search_engine.search_by_text(query, top_k)
        return results
    except Exception as e:
        logger.error(f"Error in text search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/image")
async def search_by_image(image: UploadFile = File(...), 
                         top_k: int = Form(10)):
    """Search images using an uploaded image as query."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    # Save uploaded image temporarily
    temp_path = UPLOAD_DIR / f"temp_{image.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await image.read()
            f.write(content)
        
        # Perform search
        results = search_engine.search_by_image(str(temp_path), top_k)
        
        # Clean up temp file
        temp_path.unlink()
        
        return results
    except Exception as e:
        # Clean up temp file on error
        if temp_path.exists():
            temp_path.unlink()
        logger.error(f"Error in image search: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/image/{image_path:path}")
async def serve_image(image_path: str):
    """Serve an image file."""
    try:
        # Decode the path
        image_path = image_path
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(image_path)
    except Exception as e:
        logger.error(f"Error serving image {image_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the search engine."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        stats = search_engine.get_stats()
        stats["indexed_folder"] = indexed_folder
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", tags=["meta"])
async def health():
    """Health check endpoint."""
    global search_engine
    
    return {
        "status": "ok", 
        "version": __version__,
        "search_engine_ready": search_engine is not None,
        "indexed_folder": indexed_folder
    }


@app.post("/cluster")
async def cluster_images(request: Dict[str, Any]):
    """Perform automatic clustering of indexed images."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    method = request.get("method", "auto")
    n_clusters = request.get("n_clusters")
    min_cluster_size = request.get("min_cluster_size", 5)
    output_dir = request.get("output_dir", "clusters")
    
    try:
        result = search_engine.cluster_images(
            method=method,
            n_clusters=n_clusters,
            min_cluster_size=min_cluster_size,
            output_dir=output_dir
        )
        return result
    except Exception as e:
        logger.error(f"Error during clustering: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cluster/summary")
async def cluster_summary():
    """Return last clustering summary if available."""
    global search_engine
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    summary = search_engine.get_cluster_summary()
    if summary is None:
        raise HTTPException(status_code=404, detail="No clustering summary available")
    return summary


@app.get("/cluster/{cluster_id}/images")
async def cluster_images_list(cluster_id: str):
    """Return images for given cluster id (e.g., 0 or cluster_00)."""
    global search_engine
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    images = search_engine.get_cluster_images(cluster_id)
    if not images:
        raise HTTPException(status_code=404, detail="Cluster not found or empty")
    return {"cluster": cluster_id, "images": images}


@app.get("/project")
async def project_embeddings(method: str = Query("pca", regex="^(pca|tsne)$"),
                             dim: int = Query(3, ge=2, le=3),
                             perplexity: int = 30,
                             max_points: int = 2000,
                             force: bool = False):
    """Return embedding projection (2D/3D) with optional cluster labels."""
    global search_engine
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    try:
        data = search_engine.project_embeddings(method=method, dim=dim, perplexity=perplexity, max_points=max_points, force=force)
        return data
    except Exception as e:
        logger.error(f"Error projecting embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/visualize/embeddings")
async def visualize_embeddings(method: str = Query("tsne", regex="^(pca|tsne)$"),
                              dim: int = Query(3, ge=2, le=3),
                              perplexity: int = Query(30, ge=5, le=50),
                              max_points: int = Query(1000, ge=100, le=5000),
                              include_clusters: bool = True):
    """Generate 3D visualization data for embeddings with or without clustering."""
    global search_engine
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        # Get projection data
        projection_data = search_engine.project_embeddings(
            method=method, 
            dim=dim, 
            perplexity=perplexity, 
            max_points=max_points
        )
        
        # Format for visualization
        visualization_data = {
            "method": method,
            "dimension": dim,
            "total_points": projection_data["total_points"],
            "displayed_points": projection_data["returned_points"],
            "points": []
        }
        
        # Group by clusters if available
        clusters = {}
        unclustered = []
        
        for point in projection_data["points"]:
            point_data = {
                "x": point["x"],
                "y": point["y"],
                "path": point["path"],
                "filename": point["filename"],
                "index": point["index"]
            }
            
            if dim == 3:
                point_data["z"] = point["z"]
            
            if include_clusters and "cluster" in point:
                cluster_id = str(point["cluster"])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(point_data)
            else:
                unclustered.append(point_data)
        
        visualization_data["clusters"] = clusters
        visualization_data["unclustered"] = unclustered
        
        return visualization_data
        
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gallery/images")
async def get_all_images():
    """Get all indexed images for gallery display."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    if not search_engine.image_paths:
        return {"images": [], "total": 0}
    
    # Get all image paths and create response
    images = []
    for i, path in enumerate(search_engine.image_paths):
        filename = os.path.basename(path)
        images.append({
            "path": path,
            "filename": filename,
            "index": i
        })
    
    return {"images": images, "total": len(images)}


@app.get("/gallery/images/similar/{image_index}")
async def get_similar_images(image_index: int, top_k: int = Query(8, description="Number of similar images to return")):
    """Get similar images to a specific image by its index."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    if not search_engine.image_paths or image_index >= len(search_engine.image_paths):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        image_path = search_engine.image_paths[image_index]
        results = search_engine.search_by_image(image_path, top_k + 1)  # +1 to exclude the original image
        
        # Filter out the original image and add index information
        similar_images = []
        for result in results:
            if result['path'] != image_path:
                # Find the index of this image in the image_paths list
                try:
                    result_index = search_engine.image_paths.index(result['path'])
                    result['index'] = result_index
                    similar_images.append(result)
                except ValueError:
                    # If image not found in paths (shouldn't happen), skip it
                    continue
                
                if len(similar_images) >= top_k:
                    break
        
        return {"similar_images": similar_images, "original_index": image_index}
    except Exception as e:
        logger.error(f"Error finding similar images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search/similar")
async def search_similar_by_path(path: str = Query(..., description="Path to the image"), 
                                top_k: int = Query(10, description="Number of similar images")):
    """Search for similar images by image path."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
        
    if not search_engine.indexed_images:
        raise HTTPException(status_code=404, detail="No images indexed")
    
    try:
        # Find the index of the image by path
        image_index = None
        for i, img_path in enumerate(search_engine.indexed_images):
            if img_path == path:
                image_index = i
                break
        
        if image_index is None:
            raise HTTPException(status_code=404, detail="Image not found in index")
        
        # Get similar images
        similar_indices = search_engine.find_similar_images(image_index, top_k=top_k + 1)  # +1 to exclude self
        
        # Filter out the original image and format results
        similar_images = []
        for idx in similar_indices:
            if idx != image_index:  # Exclude the original image
                img_path = search_engine.indexed_images[idx]
                filename = Path(img_path).name
                
                # Calculate similarity score (1 - distance)
                similarity = search_engine.calculate_similarity(image_index, idx)
                
                similar_images.append({
                    "path": img_path,
                    "filename": filename,
                    "score": float(similarity),
                    "index": idx
                })
                
                if len(similar_images) >= top_k:
                    break
        
        return similar_images
    except Exception as e:
        logger.error(f"Error finding similar images by path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cluster/suggestions")
async def get_cluster_suggestions(top_k: int = Query(5, description="Number of cluster suggestions")):
    """Get quick cluster suggestions without full clustering."""
    global search_engine
    
    if search_engine is None:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        suggestions = search_engine.get_cluster_suggestions(top_k=top_k)
        return suggestions
    except Exception as e:
        logger.error(f"Error getting cluster suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
