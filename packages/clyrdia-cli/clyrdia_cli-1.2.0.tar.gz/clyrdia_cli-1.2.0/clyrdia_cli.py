#!/usr/bin/env python3
"""
Clyrdia CLI - Standalone entry point
This ensures the CLI command is properly installed to PATH
"""

import sys
from clyrdia.cli_modular import app

def main():
    """Main entry point for the CLI"""
    return app()

if __name__ == "__main__":
    sys.exit(main())
