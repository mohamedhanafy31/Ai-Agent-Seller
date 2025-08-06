#!/bin/bash

# Setup and Convert Mermaid Diagrams to PDF
# This script installs dependencies and converts diagrams to PDF

set -e

echo "🚀 Setting up Mermaid to PDF Converter..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python $python_version detected"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r scripts/requirements.txt

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️  Chrome/Chromium not found. The script will download ChromeDriver automatically."
    echo "   For better performance, consider installing Chrome or Chromium."
fi

# Create output directory
mkdir -p output

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Usage:"
echo "   python3 scripts/simple_pdf_converter.py docs/flow-diagram.md"
echo "   python3 scripts/simple_pdf_converter.py docs/flow-diagram.md custom_output_dir"
echo ""
echo "🎯 Converting diagrams now..."

# Convert the flow diagram
if [ -f "docs/flow-diagram.md" ]; then
    python3 scripts/simple_pdf_converter.py docs/flow-diagram.md
    echo ""
    echo "🎉 Conversion completed! Check the 'output' directory for PDF files."
else
    echo "⚠️  docs/flow-diagram.md not found. Please run the conversion manually:"
    echo "   python3 scripts/simple_pdf_converter.py <your-markdown-file>"
fi 