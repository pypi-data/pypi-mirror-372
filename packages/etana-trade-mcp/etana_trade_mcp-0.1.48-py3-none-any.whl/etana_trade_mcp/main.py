import sys
import os
import argparse
from pathlib import Path

from .server import mcp


def main():
    """Run the MCP server."""
    # The actual argument parsing is done in the server module
    # to ensure the working directory is set early
    mcp.run()



if __name__ == "__main__":
    main()
