#!/bin/bash

# Build and upload script for shadows package
# This script removes previous builds, creates a new source distribution, and uploads it

set -e  # Exit on any error

echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

echo "📦 Creating source distribution..."
python -m build --sdist

echo "🔍 Checking distribution..."
twine check dist/*

echo "📤 Uploading to PyPI..."
twine upload dist/*

echo "✅ Build and upload completed successfully!"
echo "📁 Distribution files created in: dist/" 