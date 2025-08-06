# Mermaid Diagram to PDF Converter

This directory contains scripts to convert Mermaid diagrams from markdown files to PDF format.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/setup_and_convert.sh
./scripts/setup_and_convert.sh
```

**Windows:**
```cmd
scripts\setup_and_convert.bat
```

### Option 2: Manual Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. **Convert diagrams:**
   ```bash
   python scripts/simple_pdf_converter.py docs/flow-diagram.md
   ```

## 📋 Requirements

- **Python 3.7+**
- **Chrome/Chromium browser** (optional, will be downloaded automatically)
- **Internet connection** (for downloading ChromeDriver and Mermaid library)

## 🔧 Available Scripts

### 1. Simple PDF Converter (`simple_pdf_converter.py`)
- **Easiest to use** - recommended for most users
- Uses browser automation with Selenium
- Automatically downloads ChromeDriver
- Generates high-quality PDFs with proper formatting

### 2. Advanced PDF Converter (`convert_diagrams_to_pdf.py`)
- **More features** but requires additional tools
- Uses mermaid-cli and wkhtmltopdf
- Requires manual installation of external tools
- Better for batch processing

## 📖 Usage Examples

### Convert a single file:
```bash
python scripts/simple_pdf_converter.py docs/flow-diagram.md
```

### Convert with custom output directory:
```bash
python scripts/simple_pdf_converter.py docs/flow-diagram.md my_pdfs
```

### Convert multiple files:
```bash
python scripts/simple_pdf_converter.py docs/flow-diagram.md
python scripts/simple_pdf_converter.py docs/endpoint-usage-examples.md
```

## 📁 Output

The script will create:
- **PDF files**: One for each Mermaid diagram found in the markdown file
- **HTML files**: Intermediate files (can be deleted)
- **Output directory**: Contains all generated files

### File naming:
- `diagram_1.pdf` - First diagram in the file
- `diagram_2.pdf` - Second diagram in the file
- etc.

## 🎨 PDF Features

- **Landscape orientation** for better diagram visibility
- **High resolution** with proper scaling
- **Professional formatting** with headers and footers
- **Color preservation** from original diagrams
- **A4 page size** with proper margins

## 🔍 Troubleshooting

### Common Issues:

1. **"ChromeDriver not found"**
   - The script will automatically download ChromeDriver
   - If it fails, manually install Chrome/Chromium

2. **"Python not found"**
   - Install Python 3.7+ from python.org
   - Make sure Python is in your PATH

3. **"Selenium not installed"**
   - Run: `pip install selenium webdriver-manager`

4. **"Permission denied" (Linux/Mac)**
   - Make script executable: `chmod +x scripts/setup_and_convert.sh`

5. **"Chrome not found"**
   - Install Chrome or Chromium browser
   - The script will work without it but may be slower

### Manual Chrome Installation:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install google-chrome-stable
```

**macOS:**
```bash
brew install --cask google-chrome
```

**Windows:**
Download from https://www.google.com/chrome/

## 🛠️ Advanced Usage

### Custom PDF Settings

Edit the script to modify PDF settings:
```python
print_options = {
    'landscape': True,           # Landscape orientation
    'paperWidth': 11.69,         # A4 width in inches
    'paperHeight': 8.27,         # A4 height in inches
    'marginTop': 0.4,           # Top margin in inches
    'marginBottom': 0.4,        # Bottom margin in inches
    'marginLeft': 0.4,          # Left margin in inches
    'marginRight': 0.4,         # Right margin in inches
}
```

### Batch Processing

Create a script to convert multiple files:
```bash
#!/bin/bash
for file in docs/*.md; do
    echo "Converting $file..."
    python scripts/simple_pdf_converter.py "$file"
done
```

## 📊 Supported Diagram Types

The converter supports all Mermaid diagram types:
- **Flowcharts** (graph, flowchart)
- **Sequence diagrams** (sequenceDiagram)
- **Class diagrams** (classDiagram)
- **State diagrams** (stateDiagram)
- **Entity Relationship diagrams** (erDiagram)
- **User Journey diagrams** (journey)
- **Gantt charts** (gantt)
- **Pie charts** (pie)
- **Git graphs** (gitgraph)

## 🎯 Tips for Best Results

1. **Use descriptive titles** in your diagrams
2. **Keep diagrams reasonably sized** (not too complex)
3. **Use consistent styling** across diagrams
4. **Test with simple diagrams first**
5. **Check the generated HTML files** if PDFs look wrong

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all requirements are installed
3. Try with a simple diagram first
4. Check the console output for error messages

## 🔄 Alternative Methods

### Online Converters:
- [Mermaid Live Editor](https://mermaid.live/) - Export as PNG/SVG
- [Draw.io](https://draw.io) - Import Mermaid and export as PDF

### Command Line Tools:
- **mermaid-cli**: `npm install -g @mermaid-js/mermaid-cli`
- **puppeteer**: For Node.js users
- **wkhtmltopdf**: For HTML to PDF conversion

---

**Happy diagramming! 🎨** 