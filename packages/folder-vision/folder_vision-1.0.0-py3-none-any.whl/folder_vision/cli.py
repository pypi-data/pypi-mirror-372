"""CLI interface for Folder Vision CLIP Image Search."""

import argparse
import sys
import os
from pathlib import Path
import json

from . import __version__
from .clip_search import CLIPImageSearch


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Folder Vision - CLIP-based multimodal image search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start web server
  fv serve --port 8000

  # Index a folder
  fv index /path/to/images

  # Search by text
  fv search-text "a red car"

  # Search by image
  fv search-image /path/to/query.jpg

  # Cluster images automatically
  fv cluster --method auto

  # Preview potential clusters
  fv cluster-preview

  # Get statistics
  fv stats
        """
    )
    
    parser.add_argument('--version', action='version', version=f'Folder Vision {__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Serve command
    serve_parser = subparsers.add_parser('serve', help='Start the web server')
    serve_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    serve_parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    serve_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    # Index command
    index_parser = subparsers.add_parser('index', help='Index images in a folder')
    index_parser.add_argument('folder_path', help='Path to folder containing images')
    index_parser.add_argument('--no-cache', action='store_true', help='Do not save embeddings cache')
    index_parser.add_argument('--max-depth', type=int, help='Maximum depth to search subdirectories (default: unlimited)')
    
    # Search text command
    text_parser = subparsers.add_parser('search-text', help='Search images using text description')
    text_parser.add_argument('query', help='Text description to search for')
    text_parser.add_argument('--top-k', type=int, default=10, help='Number of results to return (default: 10)')
    text_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    # Search image command
    image_parser = subparsers.add_parser('search-image', help='Search images using another image')
    image_parser.add_argument('image_path', help='Path to query image')
    image_parser.add_argument('--top-k', type=int, default=10, help='Number of results to return (default: 10)')
    image_parser.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    # Stats command
    subparsers.add_parser('stats', help='Show search engine statistics')
    
    # Cluster command
    cluster_parser = subparsers.add_parser('cluster', help='Automatically cluster images')
    cluster_parser.add_argument('--method', choices=['auto', 'kmeans', 'dbscan'], default='auto',
                               help='Clustering method (default: auto)')
    cluster_parser.add_argument('--clusters', type=int, help='Number of clusters for KMeans')
    cluster_parser.add_argument('--min-size', type=int, default=5, help='Minimum cluster size (default: 5)')
    cluster_parser.add_argument('--output', default='clusters', help='Output directory (default: clusters)')
    
    # Cluster suggestions command
    subparsers.add_parser('cluster-preview', help='Preview potential clusters without full analysis')
    
    # Web command (alias for serve)
    web_parser = subparsers.add_parser('web', help='Start the web interface (alias for serve)')
    web_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    web_parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    web_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle serve/web commands
    if args.command in ['serve', 'web']:
        try:
            import uvicorn
            from .app import app
            
            print(f"🚀 Starting Folder Vision web server on http://{args.host}:{args.port}")
            print("📁 Open your browser to access the CLIP image search interface")
            
            uvicorn.run(
                "folder_vision.app:app",
                host=args.host,
                port=args.port,
                reload=args.reload
            )
        except ImportError:
            print("❌ Error: uvicorn is required to run the web server")
            print("Install it with: pip install uvicorn")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        return
    
    # Initialize search engine for other commands
    try:
        print("🔧 Initializing CLIP search engine...")
        search_engine = CLIPImageSearch()
        
        # Try to load existing cache
        if search_engine.load_embeddings_cache():
            print("✅ Loaded existing embeddings cache")
        else:
            print("ℹ️  No existing cache found")
            
    except Exception as e:
        print(f"❌ Error initializing search engine: {e}")
        sys.exit(1)
    
    # Handle commands
    if args.command == 'index':
        handle_index(search_engine, args)
    elif args.command == 'search-text':
        handle_search_text(search_engine, args)
    elif args.command == 'search-image':
        handle_search_image(search_engine, args)
    elif args.command == 'stats':
        handle_stats(search_engine)
    elif args.command == 'cluster':
        handle_cluster(search_engine, args)
    elif args.command == 'cluster-preview':
        handle_cluster_preview(search_engine)


def handle_index(search_engine: CLIPImageSearch, args):
    """Handle the index command."""
    folder_path = args.folder_path
    
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder does not exist: {folder_path}")
        sys.exit(1)
    
    print(f"📁 Indexing images in: {folder_path}")
    if args.max_depth is not None:
        print(f"🔍 Maximum search depth: {args.max_depth} levels")
    print("⏳ This may take a while depending on the number of images...")
    
    try:
        result = search_engine.index_folder(folder_path, save_cache=not args.no_cache, max_depth=args.max_depth)
        
        print("\n✅ Indexing complete!")
        print(f"📊 Statistics:")
        print(f"   • Total files found: {result['total_files_found']}")
        print(f"   • Successfully indexed: {result['successfully_indexed']}")
        print(f"   • Failed to load: {result['failed_to_load']}")
        print(f"   • Embeddings shape: {result['embeddings_shape']}")
        
        if not args.no_cache:
            print("💾 Embeddings saved to cache for faster future loading")
            
    except Exception as e:
        print(f"❌ Error during indexing: {e}")
        sys.exit(1)


def handle_search_text(search_engine: CLIPImageSearch, args):
    """Handle the search-text command."""
    if search_engine.image_embeddings is None or len(search_engine.image_paths) == 0:
        print("❌ Error: No images indexed. Please run 'fv index <folder_path>' first.")
        sys.exit(1)
    
    print(f"� Searching for: '{args.query}'")
    
    try:
        results = search_engine.search_by_text(args.query, args.top_k)
        
        if not results:
            print("❌ No results found.")
            return
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"\n✅ Found {len(results)} results:")
            print("-" * 80)
            for i, result in enumerate(results, 1):
                print(f"{i:2d}. {result['filename']}")
                print(f"    Score: {result['score']:.4f}")
                print(f"    Path:  {result['path']}")
                print()
    
    except Exception as e:
        print(f"❌ Error during search: {e}")
        sys.exit(1)


def handle_search_image(search_engine: CLIPImageSearch, args):
    """Handle the search-image command."""
    if search_engine.image_embeddings is None or len(search_engine.image_paths) == 0:
        print("❌ Error: No images indexed. Please run 'fv index <folder_path>' first.")
        sys.exit(1)
    
    image_path = args.image_path
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Query image does not exist: {image_path}")
        sys.exit(1)
    
    print(f"🖼️  Searching for images similar to: {image_path}")
    
    try:
        results = search_engine.search_by_image(image_path, args.top_k)
        
        if not results:
            print("❌ No results found.")
            return
        
        if args.format == 'json':
            print(json.dumps(results, indent=2))
        else:
            print(f"\n✅ Found {len(results)} similar images:")
            print("-" * 80)
            for i, result in enumerate(results, 1):
                print(f"{i:2d}. {result['filename']}")
                print(f"    Score: {result['score']:.4f}")
                print(f"    Path:  {result['path']}")
                print()
    
    except Exception as e:
        print(f"❌ Error during search: {e}")
        sys.exit(1)


def handle_stats(search_engine: CLIPImageSearch):
    """Handle the stats command."""
    try:
        stats = search_engine.get_stats()
        
        print("📊 Search Engine Statistics:")
        print("-" * 40)
        print(f"Total images indexed: {stats['total_images']}")
        print(f"Embedding dimension: {stats['embedding_dim']}")
        print(f"Device: {stats['device']}")
        print(f"Model: {stats['model_name']}")
        print(f"Cache file exists: {stats['cache_file_exists']}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        sys.exit(1)


def handle_cluster(search_engine: CLIPImageSearch, args):
    """Handle the cluster command."""
    if search_engine.image_embeddings is None or len(search_engine.image_paths) == 0:
        print("❌ Error: No images indexed. Please run 'fv index <folder_path>' first.")
        sys.exit(1)
    
    print(f"🎯 Starting automatic clustering using {args.method} method...")
    print("⏳ This may take a while depending on the number of images...")
    
    try:
        result = search_engine.cluster_images(
            method=args.method,
            n_clusters=args.clusters,
            min_cluster_size=args.min_size,
            output_dir=args.output
        )
        
        print("\n✅ Clustering complete!")
        print(f"📊 Results:")
        print(f"   • Method: {result['method']}")
        print(f"   • Total images: {result['total_images']}")
        print(f"   • Clusters found: {result['n_clusters']}")
        print(f"   • Average cluster size: {result['statistics']['avg_cluster_size']:.1f}")
        print(f"   • Largest cluster: {result['statistics']['largest_cluster']} images")
        print(f"   • Smallest cluster: {result['statistics']['smallest_cluster']} images")
        
        print(f"\n📁 Files saved to: {args.output}/")
        print(f"   • cluster_summary.json - Complete results")
        print(f"   • cluster_assignments.json - Image assignments")
        if result['files']['visualization']:
            print(f"   • cluster_visualization.html - Interactive visualization")
        
        print("\n🎯 Cluster Details:")
        for name, cluster in result['clusters'].items():
            if name != 'noise' or cluster['size'] > 0:
                print(f"   • {name}: {cluster['size']} images")
                if cluster['representative']:
                    rep_name = os.path.basename(cluster['representative'])
                    print(f"     Representative: {rep_name}")
    
    except Exception as e:
        print(f"❌ Error during clustering: {e}")
        sys.exit(1)


def handle_cluster_preview(search_engine: CLIPImageSearch):
    """Handle the cluster-preview command."""
    if search_engine.image_embeddings is None or len(search_engine.image_paths) == 0:
        print("❌ Error: No images indexed. Please run 'fv index <folder_path>' first.")
        sys.exit(1)
    
    print("🔍 Analyzing potential clusters...")
    
    try:
        suggestions = search_engine.get_cluster_suggestions(top_k=5)
        
        if not suggestions:
            print("❌ No cluster suggestions available. Need more images or better diversity.")
            return
        
        print(f"\n✅ Found {len(suggestions)} potential clusters:")
        print("-" * 60)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. Cluster with {suggestion['size']} images")
            print(f"   Sample files:")
            for filename in suggestion['sample_filenames'][:3]:
                print(f"     • {filename}")
            print()
        
        print("💡 Tip: Run 'fv cluster' to perform full clustering analysis")
    
    except Exception as e:
        print(f"❌ Error getting cluster suggestions: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
