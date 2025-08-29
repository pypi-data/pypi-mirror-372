"""Command line interface for Taman system monitor."""

import sys
import argparse
import uvicorn
from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION, DEFAULT_HOST, DEFAULT_PORT


def print_help():
    """Print help information about Taman system monitor."""
    help_text = f"""
{APP_NAME} - Real-time process tracking and resource usage

USAGE:
    taman [OPTIONS]

OPTIONS:
    --help, -h      Show this help message and exit
    --version, -v   Show version information
    --host HOST     Set the host address (default: {DEFAULT_HOST})
    --port PORT     Set the port number (default: {DEFAULT_PORT})

DESCRIPTION:
    Taman is a FastAPI-based system monitoring tool that provides:
    - Real-time CPU and memory usage tracking
    - Process monitoring with detailed information
    - WebSocket streaming for live updates
    - REST API endpoints for system data

API ENDPOINTS:
    GET /process         - Get current processes list
    GET /process/stream  - Stream real-time process data
    GET /kill/{{pid}}      - Terminate a process by PID

EXAMPLES:
    taman                           # Start server on default host:port
    taman --host 0.0.0.0 --port 9000  # Custom host and port
    
Visit http://{DEFAULT_HOST}:{DEFAULT_PORT}/docs for interactive API documentation.
    """
    print(help_text)


def print_version():
    """Print version information."""
    print(f"{APP_NAME} v{APP_VERSION}")


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - {APP_DESCRIPTION}",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument(
        '--help', '-h',
        action='store_true',
        help='Show this help message and exit'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version information'
    )
    
    parser.add_argument(
        '--host',
        default=DEFAULT_HOST,
        help=f'Host address to bind to (default: {DEFAULT_HOST})'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_PORT,
        help=f'Port number to bind to (default: {DEFAULT_PORT})'
    )
    
    return parser


def start_server(host=DEFAULT_HOST, port=DEFAULT_PORT):
    """Start the Taman API server."""
    print(f"Starting {APP_NAME} on {host}:{port}")
    print(f"API docs available at: http://{host}:{port}/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "taman.api:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle help and version
    if args.help:
        print_help()
        sys.exit(0)
    
    if args.version:
        print_version()
        sys.exit(0)
    
    # Start the server
    start_server(host=args.host, port=args.port)
