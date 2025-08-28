#!/bin/bash

set -e

echo "Building and publishing ReadyData Python SDK..."

# Get current version from pyproject.toml
current_version=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "Current version: $current_version"

# Parse version components
IFS='.' read -r major minor patch <<< "$current_version"

# Increment patch version
new_patch=$((patch + 1))
new_version="$major.$minor.$new_patch"

echo "New version: $new_version"

# Update version in pyproject.toml using a more robust approach
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed
    sed -i '' "s/^version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
else
    # Linux sed
    sed -i "s/^version = \"$current_version\"/version = \"$new_version\"/" pyproject.toml
fi

echo "Updated version to $new_version"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade required tools
echo "Installing build tools..."
pip install --upgrade build twine

# Clean previous build artifacts
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building package..."
python -m build

# Upload to PyPI
echo "Uploading to PyPI..."
twine upload dist/*

# Deactivate virtual environment
deactivate

echo "Successfully published version $new_version"
echo "Check release at: http://pypi.org/manage/project/readydata-sdk-py/releases/"