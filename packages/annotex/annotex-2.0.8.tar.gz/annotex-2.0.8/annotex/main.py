#!/usr/bin/env python3
"""
Annotex - Annotation Tool
Main entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
        
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
        
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with: pip install annotex")
        return False
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Annotex - AI-Powered Annotation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  annotex                    # Start GUI
  annotex --project file.anno   # Load project
  annotex --images /path/to/images  # Load images folder
  annotex --version          # Show version
        """
    )
    
    parser.add_argument(
        "--project", "-p",
        type=str,
        help="Load project file (.anno)"
    )
    
    parser.add_argument(
        "--images", "-i", 
        type=str,
        help="Load images from directory"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Annotex 2.0.8"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import GUI after dependency check
    try:
        import tkinter as tk
        from annotex.gui.advanced_gui import Annotex
    except ImportError as e:
        print(f"❌ Failed to import GUI components: {e}")
        print("Please reinstall Annotex: pip install --upgrade annotex")
        sys.exit(1)
    
    # Create root window
    root = tk.Tk()
    
    # Create application
    app = Annotex(root)
    
    # Handle command line arguments
    if args.project:
        project_path = Path(args.project)
        if project_path.exists():
            # Load project after GUI is ready
            root.after(100, lambda: app.load_project_file(str(project_path)))
        else:
            print(f"❌ Project file not found: {args.project}")
    
    if args.images:
        images_path = Path(args.images)
        if images_path.exists() and images_path.is_dir():
            # Load images after GUI is ready
            root.after(100, lambda: app.load_images_from_path(str(images_path)))
        else:
            print(f"❌ Images directory not found: {args.images}")
    
    if args.debug:
        app.debug_mode = True
        app.log_message("🐛 Debug mode enabled")
    
    # Start GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Annotex closed by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()