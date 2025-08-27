#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Wrapper Entry Point.
This is a wrapper that calls the womm package __main__ module.
"""

import sys
from pathlib import Path


def main():
    """Main entry point for the womm wrapper."""
    try:
        # Add the current directory to path to import womm package
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        # Import and run the __main__ module
        from womm.__main__ import main as womm_main

        womm_main()
    except ImportError as e:
        print("❌ Error: Could not import womm package")
        print("💡 Make sure you're in the works-on-my-machine directory")
        print(f"🔧 Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running WOMM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
