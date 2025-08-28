#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Main CLI Entry Point.
This is the main entry point for the womm package.
Supports both direct execution and module execution.
"""

import sys
from pathlib import Path


def main():
    """Main entry point for the womm package."""
    try:
        # Import and run the CLI directly
        from .cli import womm

        womm()
    except ImportError as e:
        print("❌ Error: Could not import womm package")
        print("💡 Make sure the womm package is properly installed")
        print(f"🔧 Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running WOMM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
