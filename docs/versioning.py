#!/usr/bin/env python3
"""
Versioned documentation deployment script for the Markdown Decision Process project.
This script handles the creation and management of version-specific documentation.
"""

import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
import argparse
import json
from datetime import datetime

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

def get_package_version():
    """Get the current package version from pyproject.toml."""
    with open("pyproject.toml", "r") as f:
        content = f.read()
    
    # Extract version using regex
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return "unknown"

def get_git_tags():
    """Get all git tags ordered by version."""
    try:
        tags = run_command(["git", "tag", "--sort=-v:refname"]).strip().split("\n")
        return [tag for tag in tags if tag]
    except Exception as e:
        print(f"Error getting git tags: {e}")
        return []

def create_version_json(versions_dir, current_version, versions):
    """Create a versions.json file for the documentation."""
    versions_info = {
        "current": current_version,
        "versions": versions,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(versions_dir, "versions.json"), "w") as f:
        json.dump(versions_info, f, indent=2)

def build_version_docs(version, output_dir):
    """Build documentation for a specific version."""
    print(f"\nBuilding documentation for version {version}")
    
    # Create temporary directory for this version
    temp_dir = os.path.join(output_dir, "_temp", version)
    ensure_directory(temp_dir)
    
    # Get the specified version
    if version == "latest":
        # Use current code
        pass
    else:
        # Checkout the specific version
        run_command(["git", "checkout", version])
    
    try:
        # Build documentation for this version
        from build_docs import build_docs
        docs_dir = os.path.join(os.getcwd(), "docs")
        version_output = os.path.join(output_dir, version)
        ensure_directory(version_output)
        
        build_docs(docs_dir, version_output)
        
        print(f"Documentation for version {version} built at {version_output}")
    finally:
        # Return to original branch
        if version != "latest":
            run_command(["git", "checkout", "-"])

def create_redirect_index(output_dir, current_version):
    """Create redirect index.html to current version."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Redirecting to latest documentation</title>
        <meta http-equiv="refresh" content="0; URL=./{current_version}/index.html">
        <link rel="canonical" href="./{current_version}/index.html">
    </head>
    <body>
        <p>Redirecting to <a href="./{current_version}/index.html">latest documentation</a>...</p>
        <script>
            window.location.href = "./{current_version}/index.html";
        </script>
    </body>
    </html>
    """
    
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html)

def create_version_selector(output_dir, versions):
    """Create a JavaScript file for version selection."""
    js = """
    document.addEventListener('DOMContentLoaded', function() {
        // Fetch versions.json
        fetch('../versions.json')
            .then(response => response.json())
            .then(data => {
                // Create version selector
                const header = document.querySelector('.wy-side-nav-search');
                if (header) {
                    const select = document.createElement('select');
                    select.id = 'version-selector';
                    select.style.marginBottom = '10px';
                    select.style.width = '90%';
                    
                    // Add onChange event
                    select.addEventListener('change', function() {
                        window.location.href = '../' + this.value + '/index.html';
                    });
                    
                    // Add options
                    const currentVersion = data.current;
                    data.versions.forEach(version => {
                        const option = document.createElement('option');
                        option.value = version;
                        option.text = version === currentVersion ? version + ' (current)' : version;
                        option.selected = version === window.VERSION;
                        select.appendChild(option);
                    });
                    
                    // Create label
                    const label = document.createElement('div');
                    label.textContent = 'Version:';
                    label.style.color = 'white';
                    label.style.marginBottom = '5px';
                    
                    // Add to DOM
                    header.appendChild(label);
                    header.appendChild(select);
                }
            })
            .catch(error => console.error('Error loading version data:', error));
    });
    """
    
    # Ensure _static directory exists in each version
    for version in versions:
        static_dir = os.path.join(output_dir, version, "_static")
        ensure_directory(static_dir)
        
        # Add version.js file
        with open(os.path.join(static_dir, "version.js"), "w") as f:
            f.write(f"window.VERSION = '{version}';\n")
            f.write(js)
        
        # Add version selector to conf.py
        conf_file = os.path.join(output_dir, version, "_static", "js", "theme.js")
        if os.path.exists(os.path.dirname(conf_file)):
            with open(conf_file, "a") as f:
                f.write('\ndocument.write("<script src=\\"/_static/version.js\\"></script>");')

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build versioned documentation")
    parser.add_argument("--output", default="docs/versioned", help="Output directory for versioned docs")
    parser.add_argument("--versions", nargs="+", help="Specific versions to build")
    parser.add_argument("--max-versions", type=int, default=5, help="Maximum number of versions to build")
    parser.add_argument("--current", help="Current version to use (defaults to package version)")
    return parser.parse_args()

def main():
    """Main function to build versioned documentation."""
    args = parse_args()
    
    # Set up output directory
    output_dir = os.path.abspath(args.output)
    ensure_directory(output_dir)
    
    # Get current version
    current_version = args.current or get_package_version()
    print(f"Current version: {current_version}")
    
    # Get versions to build
    if args.versions:
        versions = args.versions
    else:
        # Always include 'latest'
        versions = ["latest"]
        
        # Add tagged versions
        tags = get_git_tags()
        if tags:
            # Limit to max_versions
            versions.extend(tags[:args.max_versions-1])
    
    print(f"Building versions: {', '.join(versions)}")
    
    # Build each version
    for version in versions:
        build_version_docs(version, output_dir)
    
    # Create versions.json
    create_version_json(output_dir, current_version, versions)
    
    # Create redirect index
    create_redirect_index(output_dir, current_version)
    
    # Create version selector
    create_version_selector(output_dir, versions)
    
    print(f"\nVersioned documentation built successfully in {output_dir}")
    print(f"Available versions: {', '.join(versions)}")

if __name__ == "__main__":
    main() 