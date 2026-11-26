#!/usr/bin/env python3
"""
Documentation build script for the Markdown Decision Process project.
This script automates the process of building the documentation using Sphinx.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse

def ensure_directory(path):
    """Ensure directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)

def run_command(cmd, cwd=None):
    """Run a shell command and return the output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing command: {' '.join(cmd)}")
        print(result.stderr)
        sys.exit(1)
    return result.stdout

def build_docs(docs_dir, output_dir, builder="html"):
    """Build documentation using Sphinx."""
    # Create necessary directories
    build_dir = os.path.join(docs_dir, "_build", builder)
    ensure_directory(build_dir)
    
    # Build the documentation
    cmd = [
        "sphinx-build",
        "-b", builder,
        "-d", os.path.join(docs_dir, "_build", "doctrees"),
        docs_dir,
        build_dir
    ]
    
    run_command(cmd)
    
    # Copy built documentation to output directory if specified
    if output_dir and output_dir != build_dir:
        ensure_directory(output_dir)
        for item in os.listdir(build_dir):
            s = os.path.join(build_dir, item)
            d = os.path.join(output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
    
    print(f"\nDocumentation built successfully in {output_dir or build_dir}")
    return build_dir

def clean_docs(docs_dir):
    """Clean documentation build files."""
    build_dir = os.path.join(docs_dir, "_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"Cleaned {build_dir}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build MDP documentation")
    parser.add_argument("--clean", action="store_true", help="Clean documentation before building")
    parser.add_argument("--builder", default="html", help="Sphinx builder to use (html, latex, etc.)")
    parser.add_argument("--output", help="Output directory for documentation")
    return parser.parse_args()

def main():
    """Main function to build documentation."""
    args = parse_args()
    
    # Get the docs directory (where this script is located)
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    
    if args.clean:
        clean_docs(docs_dir)
    
    output_dir = args.output or os.path.join(docs_dir, "_build", args.builder)
    build_docs(docs_dir, output_dir, args.builder)

if __name__ == "__main__":
    main() 