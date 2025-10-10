#!/usr/bin/env python3
"""
Validex Script Launcher
Main entry point for all Validex operations
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import and run the main validex manager
if __name__ == "__main__":
    from scripts.main.validex_manager import main
    sys.exit(main())
