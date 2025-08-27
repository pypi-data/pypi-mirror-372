#!/usr/bin/env python3
"""
Build and upload script for dda-py package to PyPI.

This script will:
1. Check the latest version on PyPI
2. Increment the version by 0.0.1
3. Update version in pyproject.toml
4. Clean previous build artifacts
5. Build the package (wheel and sdist)
6. Upload to PyPI using twine

Requirements:
- build package: pip install build
- twine package: pip install twine
- requests package: pip install requests
- PyPI credentials configured (via ~/.pypirc or environment variables)
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import requests


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {description} failed!")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    print(f"Success: {description} completed")
    if result.stdout:
        print(result.stdout)


def clean_build_artifacts():
    """Remove previous build artifacts."""
    artifacts = ["dist", "build", "*.egg-info"]
    
    for artifact in artifacts:
        if "*" in artifact:
            # Handle glob patterns
            import glob
            for path in glob.glob(artifact):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"Removed directory: {path}")
                elif os.path.isfile(path):
                    os.remove(path)
                    print(f"Removed file: {path}")
        else:
            if os.path.exists(artifact):
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                    print(f"Removed directory: {artifact}")
                else:
                    os.remove(artifact)
                    print(f"Removed file: {artifact}")


def get_latest_pypi_version(package_name):
    """Get the latest version of the package from PyPI."""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 404:
            print(f"Package {package_name} not found on PyPI. Starting with version 0.0.1")
            return "0.0.0"
        response.raise_for_status()
        data = response.json()
        return data["info"]["version"]
    except requests.RequestException as e:
        print(f"Error fetching version from PyPI: {e}")
        print("Continuing with local version...")
        return None


def increment_version(version):
    """Increment version by 0.0.1."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    major, minor, patch = map(int, parts)
    patch += 1
    return f"{major}.{minor}.{patch}"


def update_version_in_pyproject(new_version):
    """Update the version in pyproject.toml."""
    pyproject_path = "pyproject.toml"
    
    with open(pyproject_path, "r") as f:
        content = f.read()
    
    # Update version line
    updated_content = re.sub(
        r'^version = ".*"$',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    with open(pyproject_path, "w") as f:
        f.write(updated_content)
    
    print(f"Updated version to {new_version} in pyproject.toml")


def check_requirements():
    """Check if required packages are installed."""
    required_packages = ["build", "twine", "requests"]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Error: {package} is not installed.")
            print(f"Install it with: pip install {package}")
            sys.exit(1)
    
    print("All required packages are installed.")


def main():
    """Main function to build and upload the package."""
    print("DDA-PY Package Build and Upload Script")
    print("=====================================")
    
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Check requirements
    check_requirements()
    
    # Check and update version
    print("\nChecking version...")
    package_name = "dda-py"
    
    # Get latest version from PyPI
    latest_pypi_version = get_latest_pypi_version(package_name)
    
    if latest_pypi_version:
        print(f"Latest version on PyPI: {latest_pypi_version}")
        new_version = increment_version(latest_pypi_version)
        print(f"New version will be: {new_version}")
        
        # Update pyproject.toml with new version
        update_version_in_pyproject(new_version)
    else:
        # Read current version from pyproject.toml
        with open("pyproject.toml", "r") as f:
            content = f.read()
            match = re.search(r'^version = "(.*)"$', content, re.MULTILINE)
            if match:
                current_version = match.group(1)
                print(f"Using current version from pyproject.toml: {current_version}")
            else:
                print("Error: Could not find version in pyproject.toml")
                sys.exit(1)
    
    # Clean previous build artifacts
    print("\nCleaning previous build artifacts...")
    clean_build_artifacts()
    
    # Build the package
    run_command([sys.executable, "-m", "build"], "Building package")
    
    # Check if dist directory was created and contains files
    if not os.path.exists("dist") or not os.listdir("dist"):
        print("Error: No build artifacts found in dist/ directory")
        sys.exit(1)
    
    print("\nBuild artifacts created:")
    for file in os.listdir("dist"):
        print(f"  - {file}")
    
    # Ask for confirmation before uploading
    response = input("\nDo you want to upload to PyPI? (y/N): ").lower().strip()
    if response != 'y':
        print("Upload cancelled. Build artifacts are available in the dist/ directory.")
        return
    
    # Upload to PyPI
    run_command([sys.executable, "-m", "twine", "upload", "dist/*"], "Uploading to PyPI")
    
    print("\n✅ Package successfully built and uploaded to PyPI!")
    print("You can install it with: pip install dda-py")


if __name__ == "__main__":
    main()