import argparse
import uvicorn
from . import __version__


def build_parser():
    parser = argparse.ArgumentParser(
        prog="folder-vision", 
        description="Run the Folder Vision FastAPI server",
        epilog="Example: folder-vision --port 3000 --reload"
    )
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", 
                       help="Enable auto-reload (development mode)")
    parser.add_argument("--no-access-log", action="store_true", 
                       help="Disable access log output")
    parser.add_argument("--workers", type=int, default=1,
                       help="Number of worker processes (default: 1)")
    parser.add_argument("--version", action="store_true", 
                       help="Print version and exit")
    return parser


def main():  # entry point for console script
    parser = build_parser()
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    print(f"🚀 Starting folder-vision v{__version__}")
    print(f"📡 Server will be available at: http://{args.host}:{args.port}/")
    print(f"📋 Health check: http://{args.host}:{args.port}/health")
    print("Press CTRL+C to quit")
    
    if args.reload:
        print("🔄 Auto-reload enabled (development mode)")

    try:
        uvicorn.run(
            "folder_vision.app:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            access_log=not args.no_access_log,
            workers=args.workers if not args.reload else 1,
        )
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
