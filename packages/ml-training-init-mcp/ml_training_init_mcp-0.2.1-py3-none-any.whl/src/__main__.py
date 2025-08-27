#!/usr/bin/env python3
"""Entry point for ML Training Init MCP Server when run as a module"""

import asyncio
import sys
from .server import main

def run():
    """Run the MCP server"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run()