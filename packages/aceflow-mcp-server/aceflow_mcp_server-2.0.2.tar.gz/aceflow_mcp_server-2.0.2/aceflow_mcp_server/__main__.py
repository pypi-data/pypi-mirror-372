"""Entry point for aceflow-mcp-server when run as a module."""
import sys
from .server import main

if __name__ == "__main__":
    sys.exit(main())