#!/usr/bin/env python3
"""
Quick server startup script
Makes it easy to run the web server with proper configuration
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path


def run_web_server(host="0.0.0.0", port=8000, reload=False):
    """Run the FastAPI web server"""
    cmd = [
        sys.executable, "-m", "uvicorn",
        "server.main:app",
        "--host", host,
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    print(f"Starting web server on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print("\nAPI Documentation:")
    print(f"  - Swagger UI: http://localhost:{port}/api/docs")
    print(f"  - ReDoc: http://localhost:{port}/api/redoc")
    print(f"  - Dashboard: http://localhost:{port}/")
    print()
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nShutting down server...")


def generate_sample_data():
    """Generate sample data"""
    print("Generating sample data...")
    subprocess.run([sys.executable, "create_sample_data.py"])
    print("Sample data generated!")


def run_full_pipeline(max_stocks=10):
    """Run full data pipeline"""
    print(f"Running full pipeline with {max_stocks} stocks...")
    subprocess.run([
        sys.executable, "app.py",
        "--max-stocks", str(max_stocks)
    ])
    print("Pipeline complete!")


def init_database():
    """Initialize database"""
    print("Initializing database...")
    from server.database import init_db
    init_db()
    print("Database initialized!")


def main():
    parser = argparse.ArgumentParser(
        description="Market Research Visualization - Server Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_server.py                    # Start server on port 8000
  python run_server.py --port 8080       # Start on different port
  python run_server.py --reload          # Start with hot reload (dev mode)
  python run_server.py --generate        # Generate sample data first
  python run_server.py --pipeline 20     # Generate data for 20 stocks then start
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable hot reload for development"
    )
    
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate sample data before starting server"
    )
    
    parser.add_argument(
        "--pipeline",
        type=int,
        metavar="N",
        help="Run full pipeline for N stocks before starting server"
    )
    
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database tables"
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Initialize database if requested
    if args.init_db:
        init_database()
    
    # Generate data if requested
    if args.generate:
        generate_sample_data()
    
    # Run pipeline if requested
    if args.pipeline:
        run_full_pipeline(args.pipeline)
    
    # Start server
    run_web_server(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()

