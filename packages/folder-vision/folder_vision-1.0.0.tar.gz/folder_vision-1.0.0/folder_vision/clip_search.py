"""CLIP-based multimodal image search service."""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import logging

import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)


class CLIPImageSearch:
    """CLIP-based image search engine for semantic and visual similarity."""

    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        self.image_embeddings: Optional[torch.Tensor] = None
        self.image_paths: List[str] = []
        self.embeddings_cache_file = "image_embeddings.pkl"
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        self.cluster_labels = None
        self.last_cluster_output_dir = None
        
    def _load_and_preprocess_image(self, image_path: str) -> Optional[Image.Image]:
        """Load and preprocess an image file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            PIL Image object or None if loading fails
        """
        try:
            image = Image.open(image_path).convert('RGB')
            return image
        except Exception as e:
            logger.warning(f"Failed to load image {image_path}: {e}")
            return None
    
    def _encode_images(self, images: List[Image.Image]) -> torch.Tensor:
        """Encode a batch of images using CLIP.
        
        Args:
            images: List of PIL Image objects
            
        Returns:
            Normalized image embeddings tensor
        """
        if not images:
            return torch.empty(0, self.model.config.projection_dim)
        
        # Process images in batches to avoid memory issues
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(images), batch_size):
            batch_images = images[i:i + batch_size]
            
            with torch.no_grad():
                inputs = self.processor(images=batch_images, return_tensors="pt", padding=True)
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                image_features = self.model.get_image_features(**inputs)
                # Normalize embeddings
                image_features = F.normalize(image_features, p=2, dim=1)
                all_embeddings.append(image_features.cpu())
        
        return torch.cat(all_embeddings, dim=0) if all_embeddings else torch.empty(0, self.model.config.projection_dim)
    
    def _encode_text(self, text: str) -> torch.Tensor:
        """Encode text using CLIP.
        
        Args:
            text: Text query to encode
            
        Returns:
            Normalized text embedding tensor
        """
        with torch.no_grad():
            inputs = self.processor(text=[text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            text_features = self.model.get_text_features(**inputs)
            # Normalize embeddings
            text_features = F.normalize(text_features, p=2, dim=1)
            
        return text_features.cpu()
    
    def index_folder(self, folder_path: str, save_cache: bool = True, max_depth: int = None) -> Dict[str, Any]:
        """Index all images in a folder and its subfolders.
        
        Args:
            folder_path: Path to the folder containing images
            save_cache: Whether to save embeddings to cache file
            max_depth: Maximum depth to search (None for unlimited)
            
        Returns:
            Dictionary with indexing statistics
        """
        folder_path = Path(folder_path)
        if not folder_path.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")
        
        # Find all image files
        image_files = []
        for ext in self.supported_formats:
            if max_depth is None:
                image_files.extend(folder_path.rglob(f"*{ext}"))
                image_files.extend(folder_path.rglob(f"*{ext.upper()}"))
            else:
                # Limited depth search
                for depth in range(max_depth + 1):
                    pattern = "/".join(["*"] * depth) + f"/*{ext}" if depth > 0 else f"*{ext}"
                    image_files.extend(folder_path.glob(pattern))
                    pattern = "/".join(["*"] * depth) + f"/*{ext.upper()}" if depth > 0 else f"*{ext.upper()}"
                    image_files.extend(folder_path.glob(pattern))
        
        logger.info(f"Found {len(image_files)} image files in {folder_path}")
        
        # Load images
        images = []
        valid_paths = []
        
        for img_path in image_files:
            image = self._load_and_preprocess_image(str(img_path))
            if image is not None:
                images.append(image)
                valid_paths.append(str(img_path))
        
        logger.info(f"Successfully loaded {len(images)} images")
        
        # Generate embeddings
        if images:
            self.image_embeddings = self._encode_images(images)
            self.image_paths = valid_paths
            
            # Save cache
            if save_cache:
                self._save_embeddings_cache()
        else:
            self.image_embeddings = torch.empty(0, self.model.config.projection_dim)
            self.image_paths = []
        
        return {
            "total_files_found": len(image_files),
            "successfully_indexed": len(valid_paths),
            "failed_to_load": len(image_files) - len(valid_paths),
            "embeddings_shape": list(self.image_embeddings.shape) if self.image_embeddings is not None else [0, 0]
        }

    def clear_index(self) -> Dict[str, Any]:
        """Clear currently loaded embeddings and image paths (does not delete cache file)."""
        count = len(self.image_paths)
        self.image_embeddings = None
        self.image_paths = []
        self.cluster_labels = None
        return {"cleared_images": count}
    
    def _save_embeddings_cache(self) -> None:
        """Save embeddings and paths to cache file."""
        cache_data = {
            "embeddings": self.image_embeddings,
            "paths": self.image_paths
        }
        
        try:
            with open(self.embeddings_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            logger.info(f"Saved embeddings cache to {self.embeddings_cache_file}")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
    
    def load_embeddings_cache(self) -> bool:
        """Load embeddings and paths from cache file.
        
        Returns:
            True if cache was loaded successfully, False otherwise
        """
        if not os.path.exists(self.embeddings_cache_file):
            return False
        
        try:
            with open(self.embeddings_cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.image_embeddings = cache_data["embeddings"]
            self.image_paths = cache_data["paths"]
            
            logger.info(f"Loaded embeddings cache with {len(self.image_paths)} images")
            return True
        except Exception as e:
            logger.error(f"Failed to load embeddings cache: {e}")
            return False
    
    def search_by_text(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search images using text query.
        
        Args:
            query: Text description to search for
            top_k: Number of top results to return
            
        Returns:
            List of search results with scores and paths
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            return []
        
        # Encode text query
        text_embedding = self._encode_text(query)
        
        # Ensure proper dimensions for similarity calculation
        if text_embedding.dim() == 2:
            text_embedding = text_embedding.squeeze(0)  # Remove batch dimension if present
        
        # Compute similarities using dot product (since embeddings are normalized)
        similarities = torch.matmul(text_embedding, self.image_embeddings.T)
        
        # Ensure similarities is 1D tensor
        if similarities.dim() == 0:
            similarities = similarities.unsqueeze(0)
        
        # Get top-k results
        top_indices = torch.argsort(similarities, descending=True)[:top_k]
        
        results = []
        for i, idx in enumerate(top_indices):
            idx_val = int(idx.item())
            score_val = float(similarities[idx_val].item())
            
            results.append({
                "path": self.image_paths[idx_val],
                "score": score_val,
                "filename": os.path.basename(self.image_paths[idx_val])
            })
        
        return results
    
    def search_by_image(self, query_image_path: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search images using another image as query.
        
        Args:
            query_image_path: Path to the query image
            top_k: Number of top results to return
            
        Returns:
            List of search results with scores and paths
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            return []
        
        # Load and encode query image
        query_image = self._load_and_preprocess_image(query_image_path)
        if query_image is None:
            raise ValueError(f"Could not load query image: {query_image_path}")
        
        query_embedding = self._encode_images([query_image])
        
        # Ensure proper dimensions for similarity calculation
        if query_embedding.dim() == 2:
            query_embedding = query_embedding.squeeze(0)  # Remove batch dimension if present
        
        # Compute similarities using dot product (since embeddings are normalized)
        similarities = torch.matmul(query_embedding, self.image_embeddings.T)
        
        # Ensure similarities is 1D tensor
        if similarities.dim() == 0:
            similarities = similarities.unsqueeze(0)
        
        # Get top-k results (excluding the query image itself if it's in the dataset)
        top_indices = torch.argsort(similarities, descending=True)
        
        results = []
        for idx in top_indices:
            idx_val = int(idx.item())
            image_path = self.image_paths[idx_val]
            
            # Skip if this is the exact same file as the query
            if os.path.abspath(image_path) == os.path.abspath(query_image_path):
                continue
                
            score_val = float(similarities[idx_val].item())
            results.append({
                "path": image_path,
                "score": score_val,
                "filename": os.path.basename(image_path)
            })
            
            if len(results) >= top_k:
                break
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed images.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_images": len(self.image_paths),
            "embedding_dim": self.image_embeddings.shape[1] if self.image_embeddings is not None else 0,
            "device": str(self.device),
            "model_name": self.model.name_or_path if hasattr(self.model, 'name_or_path') else "openai/clip-vit-base-patch32",
            "cache_file_exists": os.path.exists(self.embeddings_cache_file)
        }
    
    def cluster_images(self, method: str = "auto", n_clusters: Optional[int] = None, 
                      min_cluster_size: int = 5, output_dir: str = "clusters") -> Dict[str, Any]:
        """Automatically cluster images based on visual similarity.
        
        Args:
            method: Clustering method ('kmeans', 'dbscan', 'auto')
            n_clusters: Number of clusters for KMeans (auto-determined if None)
            min_cluster_size: Minimum images per cluster
            output_dir: Directory to save cluster results
            
        Returns:
            Dictionary with clustering results and statistics
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            raise ValueError("No images indexed. Please run index_folder first.")
        
        # Convert embeddings to numpy for sklearn
        embeddings_np = self.image_embeddings.detach().cpu().numpy()
        
        logger.info(f"Starting clustering of {len(self.image_paths)} images using {method} method")
        
        # Determine optimal clustering method and parameters
        if method == "auto":
            method, n_clusters = self._determine_optimal_clustering(embeddings_np, min_cluster_size)
        
        # Perform clustering
        if method == "kmeans":
            if n_clusters is None:
                n_clusters = self._find_optimal_k(embeddings_np, min_cluster_size)
            
            clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = clusterer.fit_predict(embeddings_np)
            
        elif method == "dbscan":
            # Use DBSCAN for automatic cluster detection
            clusterer = DBSCAN(eps=0.5, min_samples=min_cluster_size, metric='cosine')
            cluster_labels = clusterer.fit_predict(embeddings_np)
            
        elif method == "hierarchical":
            # Use Hierarchical clustering
            if n_clusters is None:
                n_clusters = self._find_optimal_k(embeddings_np, min_cluster_size)
            
            clusterer = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage='ward',
                compute_distances=True
            )
            cluster_labels = clusterer.fit_predict(embeddings_np)
            
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
    # Process clustering results
        cluster_info = self._process_clustering_results(cluster_labels, method, output_dir)
        # store labels & output dir
        self.cluster_labels = cluster_labels
        self.last_cluster_output_dir = output_dir
        return cluster_info
    
    def _determine_optimal_clustering(self, embeddings: np.ndarray, min_cluster_size: int) -> Tuple[str, Optional[int]]:
        """Determine the best clustering method and parameters.
        
        Args:
            embeddings: Image embeddings array
            min_cluster_size: Minimum cluster size
            
        Returns:
            Tuple of (method, n_clusters)
        """
        n_samples = embeddings.shape[0]
        
        # For small datasets, use KMeans with fewer clusters
        if n_samples < 50:
            return "kmeans", max(2, n_samples // 10)
        
        # For medium datasets, try both methods
        if n_samples < 500:
            # Try DBSCAN first for automatic cluster detection
            dbscan = DBSCAN(eps=0.5, min_samples=min_cluster_size, metric='cosine')
            dbscan_labels = dbscan.fit_predict(embeddings)
            
            # If DBSCAN finds reasonable clusters, use it
            n_dbscan_clusters = len(set(dbscan_labels)) - (1 if -1 in dbscan_labels else 0)
            if n_dbscan_clusters >= 2 and n_dbscan_clusters <= n_samples // 5:
                return "dbscan", None
        
        # Default to KMeans with optimal k
        optimal_k = self._find_optimal_k(embeddings, min_cluster_size)
        return "kmeans", optimal_k
    
    def _find_optimal_k(self, embeddings: np.ndarray, min_cluster_size: int) -> int:
        """Find optimal number of clusters using elbow method and silhouette score.
        
        Args:
            embeddings: Image embeddings array
            min_cluster_size: Minimum cluster size
            
        Returns:
            Optimal number of clusters
        """
        n_samples = embeddings.shape[0]
        max_k = min(20, n_samples // min_cluster_size)
        min_k = 2
        
        if max_k <= min_k:
            return min_k
        
        # Calculate silhouette scores for different k values
        silhouette_scores = []
        k_range = range(min_k, max_k + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            silhouette_avg = silhouette_score(embeddings, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        # Find k with highest silhouette score
        optimal_idx = np.argmax(silhouette_scores)
        optimal_k = k_range[optimal_idx]
        
        logger.info(f"Optimal k={optimal_k} with silhouette score={silhouette_scores[optimal_idx]:.3f}")
        
        return optimal_k
    
    def _process_clustering_results(self, cluster_labels: np.ndarray, method: str, 
                                  output_dir: str) -> Dict[str, Any]:
        """Process and organize clustering results.
        
        Args:
            cluster_labels: Cluster assignments for each image
            method: Clustering method used
            output_dir: Directory to save results
            
        Returns:
            Dictionary with clustering information
        """
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Organize images by cluster
        clusters = {}
        cluster_stats = {}
        
        unique_labels = np.unique(cluster_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)  # Exclude noise cluster
        
        for label in unique_labels:
            cluster_idx = int(label)
            mask = cluster_labels == label
            cluster_images = [self.image_paths[i] for i in np.where(mask)[0]]
            
            if cluster_idx == -1:
                # Noise cluster (for DBSCAN)
                cluster_name = "noise"
            else:
                cluster_name = f"cluster_{cluster_idx:02d}"
            
            clusters[cluster_name] = {
                "images": cluster_images,
                "size": len(cluster_images),
                "representative": self._find_cluster_representative(mask)
            }
            
            cluster_stats[cluster_name] = len(cluster_images)
        
        # Generate cluster visualization
        viz_path = self._create_cluster_visualization(cluster_labels, output_path)
        
        # Save cluster assignments
        cluster_assignments = {
            path: int(label) for path, label in zip(self.image_paths, cluster_labels)
        }
        
        assignments_file = output_path / "cluster_assignments.json"
        with open(assignments_file, 'w') as f:
            json.dump(cluster_assignments, f, indent=2)
        
        # Create cluster summary
        summary = {
            "method": method,
            "total_images": len(self.image_paths),
            "n_clusters": n_clusters,
            "clusters": clusters,
            "statistics": {
                "cluster_sizes": cluster_stats,
                "avg_cluster_size": np.mean([size for name, size in cluster_stats.items() if name != "noise"]),
                "largest_cluster": max(cluster_stats.values()) if cluster_stats else 0,
                "smallest_cluster": min([size for name, size in cluster_stats.items() if name != "noise"]) if cluster_stats else 0
            },
            "files": {
                "assignments": str(assignments_file),
                "visualization": str(viz_path) if viz_path else None
            }
        }
        
        # Save summary
        summary_file = output_path / "cluster_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Clustering complete: {n_clusters} clusters found")
        logger.info(f"Results saved to {output_path}")
        
        return summary

    def get_cluster_summary(self) -> Optional[Dict[str, Any]]:
        """Return last clustering summary if available."""
        if not self.last_cluster_output_dir:
            return None
        summary_path = Path(self.last_cluster_output_dir) / "cluster_summary.json"
        if not summary_path.exists():
            return None
        try:
            with open(summary_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cluster summary: {e}")
            return None

    def get_cluster_images(self, cluster_identifier: Union[int, str]) -> List[Dict[str, Any]]:
        """Return list of image information (path and filename) belonging to a given cluster id or name."""
        if self.cluster_labels is None:
            return []
        # allow names like cluster_00
        if isinstance(cluster_identifier, str) and cluster_identifier.startswith("cluster_"):
            try:
                cluster_identifier = int(cluster_identifier.split('_')[-1])
            except ValueError:
                return []
        if not isinstance(cluster_identifier, int):
            return []
        mask = self.cluster_labels == cluster_identifier
        cluster_image_paths = [self.image_paths[i] for i in np.where(mask)[0]]
        
        # Return image information with both path and filename
        return [
            {
                "path": img_path,
                "filename": Path(img_path).name
            }
            for img_path in cluster_image_paths
        ]

    def project_embeddings(self, method: str = "pca", dim: int = 3, perplexity: int = 30, random_state: int = 42,
                            max_points: int = 5000, force: bool = False) -> Dict[str, Any]:
        """Project embeddings to lower dimensions for visualization.

        Args:
            method: 'pca' or 'tsne'
            dim: 2 or 3
            perplexity: t-SNE perplexity
            random_state: random seed
            max_points: downsample to this many points (uniform) for performance
            force: if True, ignore max_points and project all

        Returns:
            Dict containing projection coordinates and (optional) cluster labels
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            raise ValueError("No embeddings available")
        if dim not in (2, 3):
            raise ValueError("dim must be 2 or 3")
        embeddings_np = self.image_embeddings.detach().cpu().numpy()
        n = embeddings_np.shape[0]
        indices = np.arange(n)
        if not force and n > max_points:
            # uniform random sample
            rng = np.random.default_rng(random_state)
            indices = rng.choice(indices, size=max_points, replace=False)
            embeddings_np = embeddings_np[indices]
        if method == 'pca':
            pca = PCA(n_components=dim, random_state=random_state)
            coords = pca.fit_transform(embeddings_np)
        elif method == 'tsne':
            perplexity = min(perplexity, max(5, embeddings_np.shape[0] - 1))
            tsne = TSNE(n_components=dim, random_state=random_state, perplexity=perplexity, init='random')
            coords = tsne.fit_transform(embeddings_np)
        else:
            raise ValueError("Unknown projection method")
        # build response
        projected = []
        for i, emb_idx in enumerate(indices):
            item = {
                "index": int(emb_idx),
                "path": self.image_paths[emb_idx],
                "filename": os.path.basename(self.image_paths[emb_idx])
            }
            if dim == 3:
                item.update({"x": float(coords[i,0]), "y": float(coords[i,1]), "z": float(coords[i,2])})
            else:
                item.update({"x": float(coords[i,0]), "y": float(coords[i,1])})
            if self.cluster_labels is not None and emb_idx < len(self.cluster_labels):
                item["cluster"] = int(self.cluster_labels[emb_idx])
            projected.append(item)
        return {"method": method, "dim": dim, "total_points": n, "returned_points": len(projected), "points": projected}
    
    def _find_cluster_representative(self, cluster_mask: np.ndarray) -> Optional[str]:
        """Find the most representative image in a cluster.
        
        Args:
            cluster_mask: Boolean mask for cluster members
            
        Returns:
            Path to representative image
        """
        if not np.any(cluster_mask):
            return None
        
        cluster_embeddings = self.image_embeddings[cluster_mask]
        cluster_paths = [self.image_paths[i] for i in np.where(cluster_mask)[0]]
        
        # Find image closest to cluster centroid
        centroid = torch.mean(cluster_embeddings, dim=0)
        similarities = torch.cosine_similarity(cluster_embeddings, centroid.unsqueeze(0), dim=1)
        
        representative_idx = torch.argmax(similarities).item()
        return cluster_paths[representative_idx]
    
    def _create_cluster_visualization(self, cluster_labels: np.ndarray, 
                                    output_path: Path) -> Optional[str]:
        """Create visualization of clusters using dimensionality reduction.
        
        Args:
            cluster_labels: Cluster assignments
            output_path: Output directory
            
        Returns:
            Path to visualization file
        """
        try:
            embeddings_np = self.image_embeddings.detach().cpu().numpy()
            
            # Use PCA for initial dimensionality reduction if needed
            if embeddings_np.shape[1] > 50:
                pca = PCA(n_components=50)
                embeddings_reduced = pca.fit_transform(embeddings_np)
            else:
                embeddings_reduced = embeddings_np
            
            # Use t-SNE for final 2D visualization
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings_np) - 1))
            embeddings_2d = tsne.fit_transform(embeddings_reduced)
            
            # Create interactive plot with Plotly
            fig = px.scatter(
                x=embeddings_2d[:, 0], 
                y=embeddings_2d[:, 1],
                color=cluster_labels.astype(str),
                title="Image Clusters Visualization",
                labels={'x': 't-SNE 1', 'y': 't-SNE 2', 'color': 'Cluster'},
                hover_data={'filename': [os.path.basename(path) for path in self.image_paths]}
            )
            
            fig.update_layout(
                width=800, 
                height=600,
                title_x=0.5
            )
            
            # Save interactive plot
            viz_file = output_path / "cluster_visualization.html"
            fig.write_html(str(viz_file))
            
            return str(viz_file)
            
        except Exception as e:
            logger.warning(f"Failed to create visualization: {e}")
            return None
    
    def get_cluster_suggestions(self, top_k: int = 3) -> List[Dict[str, Any]]:
        """Get suggestions for natural clusters without performing full clustering.
        
        Args:
            top_k: Number of cluster suggestions to return
            
        Returns:
            List of cluster suggestions with sample images
        """
        if self.image_embeddings is None or len(self.image_paths) == 0:
            return []
        
        embeddings_np = self.image_embeddings.detach().cpu().numpy()
        
        # Use quick clustering to identify potential groups
        n_suggestions = min(top_k, len(self.image_paths) // 10)
        if n_suggestions < 2:
            return []
        
        kmeans = KMeans(n_clusters=n_suggestions, random_state=42, n_init=5)
        labels = kmeans.fit_predict(embeddings_np)
        
        suggestions = []
        for i in range(n_suggestions):
            cluster_mask = labels == i
            cluster_images = [self.image_paths[j] for j in np.where(cluster_mask)[0]]
            
            if len(cluster_images) > 2:  # Only suggest clusters with multiple images
                # Get representative images
                representatives = cluster_images[:min(3, len(cluster_images))]
                
                suggestions.append({
                    "cluster_id": i,
                    "size": len(cluster_images),
                    "representative_images": representatives,
                    "sample_filenames": [os.path.basename(path) for path in representatives]
                })
        
        # Sort by cluster size
        suggestions.sort(key=lambda x: x["size"], reverse=True)
        
        return suggestions
    
    def find_similar_images(self, image_index: int, top_k: int = 10) -> List[int]:
        """Find similar images to a given image by index.
        
        Args:
            image_index: Index of the reference image
            top_k: Number of similar images to return
            
        Returns:
            List of indices of similar images, sorted by similarity
        """
        if self.image_embeddings is None or image_index >= len(self.image_paths):
            return []
        
        # Get the embedding of the reference image
        ref_embedding = self.image_embeddings[image_index].unsqueeze(0)
        
        # Calculate similarities with all images
        similarities = F.cosine_similarity(ref_embedding, self.image_embeddings)
        
        # Get top-k similar images (excluding the reference image itself)
        _, indices = torch.topk(similarities, min(top_k + 1, len(similarities)))
        
        # Convert to list and remove the reference image if it's in the results
        similar_indices = indices.cpu().tolist()
        if image_index in similar_indices:
            similar_indices.remove(image_index)
        
        return similar_indices[:top_k]
    
    def calculate_similarity(self, image_index1: int, image_index2: int) -> float:
        """Calculate similarity between two images by their indices.
        
        Args:
            image_index1: Index of the first image
            image_index2: Index of the second image
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        if (self.image_embeddings is None or 
            image_index1 >= len(self.image_paths) or 
            image_index2 >= len(self.image_paths)):
            return 0.0
        
        embedding1 = self.image_embeddings[image_index1].unsqueeze(0)
        embedding2 = self.image_embeddings[image_index2].unsqueeze(0)
        
        similarity = F.cosine_similarity(embedding1, embedding2).item()
        return float(similarity)
    
    @property
    def indexed_images(self) -> List[str]:
        """Get list of indexed image paths."""
        return self.image_paths