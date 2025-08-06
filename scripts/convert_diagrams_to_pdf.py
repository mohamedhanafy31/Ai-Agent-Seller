#!/usr/bin/env python3
"""
Mermaid Diagram to PDF Converter

This script converts Mermaid diagrams from markdown files to PDF format.
It supports multiple output formats and can handle complex diagrams.

Requirements:
- Python 3.7+
- mermaid-cli (npm install -g @mermaid-js/mermaid-cli)
- wkhtmltopdf (for HTML to PDF conversion)
"""

import os
import sys
import subprocess
import tempfile
import re
from pathlib import Path
from typing import List, Dict, Optional

class MermaidToPDFConverter:
    def __init__(self, input_file: str, output_dir: str = "output"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_mermaid_blocks(self) -> List[Dict[str, str]]:
        """Extract all Mermaid diagram blocks from the markdown file."""
        diagrams = []
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all Mermaid code blocks
        pattern = r'```mermaid\s*\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for i, match in enumerate(matches):
            diagram_code = match.group(1).strip()
            diagrams.append({
                'index': i + 1,
                'code': diagram_code,
                'name': f"diagram_{i + 1}"
            })
        
        return diagrams
    
    def create_html_template(self, diagram_code: str, title: str) -> str:
        """Create an HTML template for the Mermaid diagram."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: white;
        }}
        .diagram-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .diagram-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
        }}
        .mermaid {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px auto;
            max-width: 1200px;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="diagram-container">
        <div class="diagram-title">{title}</div>
        <div class="mermaid">
{diagram_code}
        </div>
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }},
            sequence: {{
                useMaxWidth: true,
                diagramMarginX: 50,
                diagramMarginY: 10
            }}
        }});
    </script>
</body>
</html>
"""
    
    def convert_mermaid_to_svg(self, diagram_code: str, output_path: str) -> bool:
        """Convert Mermaid diagram to SVG using mermaid-cli."""
        try:
            # Create temporary file with Mermaid code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
                f.write(diagram_code)
                temp_file = f.name
            
            # Convert to SVG using mermaid-cli
            cmd = ['mmdc', '-i', temp_file, '-o', output_path, '-f', 'svg']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            if result.returncode == 0:
                print(f"✓ Generated SVG: {output_path}")
                return True
            else:
                print(f"✗ Error generating SVG: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("✗ mermaid-cli (mmdc) not found. Please install it with: npm install -g @mermaid-js/mermaid-cli")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def convert_html_to_pdf(self, html_path: str, pdf_path: str) -> bool:
        """Convert HTML file to PDF using wkhtmltopdf."""
        try:
            cmd = [
                'wkhtmltopdf',
                '--page-size', 'A4',
                '--orientation', 'Landscape',
                '--margin-top', '10mm',
                '--margin-bottom', '10mm',
                '--margin-left', '10mm',
                '--margin-right', '10mm',
                '--enable-local-file-access',
                html_path,
                pdf_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Generated PDF: {pdf_path}")
                return True
            else:
                print(f"✗ Error generating PDF: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("✗ wkhtmltopdf not found. Please install it first.")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def convert_to_pdf(self) -> bool:
        """Convert all Mermaid diagrams to PDF."""
        print(f"Converting diagrams from: {self.input_file}")
        
        diagrams = self.extract_mermaid_blocks()
        if not diagrams:
            print("No Mermaid diagrams found in the file.")
            return False
        
        print(f"Found {len(diagrams)} diagram(s)")
        
        success_count = 0
        
        for diagram in diagrams:
            print(f"\nProcessing diagram {diagram['index']}...")
            
            # Generate SVG
            svg_path = self.output_dir / f"diagram_{diagram['index']}.svg"
            if not self.convert_mermaid_to_svg(diagram['code'], str(svg_path)):
                continue
            
            # Create HTML with the diagram
            html_content = self.create_html_template(
                diagram['code'], 
                f"Real-Time Customer Interaction Flow - Diagram {diagram['index']}"
            )
            
            html_path = self.output_dir / f"diagram_{diagram['index']}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert HTML to PDF
            pdf_path = self.output_dir / f"diagram_{diagram['index']}.pdf"
            if self.convert_html_to_pdf(str(html_path), str(pdf_path)):
                success_count += 1
        
        print(f"\n✓ Successfully converted {success_count}/{len(diagrams)} diagrams to PDF")
        print(f"Output directory: {self.output_dir.absolute()}")
        
        return success_count > 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_diagrams_to_pdf.py <input_markdown_file> [output_directory]")
        print("\nExample:")
        print("  python convert_diagrams_to_pdf.py docs/flow-diagram.md")
        print("  python convert_diagrams_to_pdf.py docs/flow-diagram.md output_pdfs")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    converter = MermaidToPDFConverter(input_file, output_dir)
    success = converter.convert_to_pdf()
    
    if success:
        print("\n🎉 Conversion completed successfully!")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 