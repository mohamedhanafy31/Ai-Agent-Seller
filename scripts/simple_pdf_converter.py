#!/usr/bin/env python3
"""
Simple Mermaid to PDF Converter

This script converts Mermaid diagrams to PDF using browser automation.
It's simpler to use and doesn't require external tools like mermaid-cli.

Requirements:
- Python 3.7+
- selenium
- webdriver-manager
"""

import os
import sys
import re
import time
from pathlib import Path
from typing import List, Dict

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install them with: pip install selenium webdriver-manager")
    sys.exit(1)

class SimpleMermaidToPDFConverter:
    def __init__(self, input_file: str, output_dir: str = "output"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver for PDF generation."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Enable PDF printing
        chrome_options.add_experimental_option(
            "prefs", {
                "download.default_directory": str(self.output_dir.absolute()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
        )
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
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
    
    def create_html_page(self, diagram_code: str, title: str) -> str:
        """Create a complete HTML page with the Mermaid diagram."""
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
            margin: 0;
            padding: 20px;
            background-color: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .subtitle {{
            font-size: 16px;
            color: #666;
        }}
        .diagram-container {{
            text-align: center;
            margin: 20px auto;
            max-width: 1400px;
        }}
        .mermaid {{
            background-color: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 30px;
            margin: 20px auto;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="header">
        <div class="title">Real-Time Customer Interaction Flow</div>
        <div class="subtitle">{title}</div>
    </div>
    
    <div class="diagram-container">
        <div class="mermaid">
{diagram_code}
        </div>
    </div>
    
    <div class="footer">
        Generated on {time.strftime('%Y-%m-%d %H:%M:%S')} | AI Agent Seller Backend Documentation
    </div>
    
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            sequence: {{
                useMaxWidth: true,
                diagramMarginX: 50,
                diagramMarginY: 10,
                actorMargin: 50
            }},
            graph: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
        
        // Wait for diagram to render before printing
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                window.print();
            }}, 2000);
        }});
    </script>
</body>
</html>
"""
    
    def convert_diagram_to_pdf(self, diagram: Dict[str, str]) -> bool:
        """Convert a single Mermaid diagram to PDF."""
        try:
            # Create HTML file
            html_content = self.create_html_page(
                diagram['code'],
                f"Diagram {diagram['index']} - {self.get_diagram_title(diagram['code'])}"
            )
            
            html_path = self.output_dir / f"diagram_{diagram['index']}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Load HTML in browser
            self.driver.get(f"file://{html_path.absolute()}")
            
            # Wait for Mermaid to render
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mermaid"))
            )
            
            # Additional wait for diagram to fully render
            time.sleep(3)
            
            # Print to PDF
            pdf_path = self.output_dir / f"diagram_{diagram['index']}.pdf"
            
            # Use Chrome's print-to-PDF functionality
            print_options = {
                'landscape': True,
                'displayHeaderFooter': False,
                'printBackground': True,
                'preferCSSPageSize': True,
                'paperWidth': 11.69,  # A4 width in inches
                'paperHeight': 8.27,  # A4 height in inches
                'marginTop': 0.4,
                'marginBottom': 0.4,
                'marginLeft': 0.4,
                'marginRight': 0.4,
                'pageRanges': ''
            }
            
            result = self.driver.execute_cdp_cmd('Page.printToPDF', print_options)
            
            if result and 'data' in result:
                import base64
                pdf_data = base64.b64decode(result['data'])
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_data)
                
                print(f"✓ Generated PDF: {pdf_path}")
                return True
            else:
                print(f"✗ Failed to generate PDF for diagram {diagram['index']}")
                return False
                
        except Exception as e:
            print(f"✗ Error converting diagram {diagram['index']}: {e}")
            return False
    
    def get_diagram_title(self, diagram_code: str) -> str:
        """Extract a meaningful title from the diagram code."""
        lines = diagram_code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('graph') or line.startswith('flowchart') or line.startswith('sequenceDiagram'):
                if 'TB' in line or 'TD' in line:
                    return "System Flow"
                elif 'LR' in line:
                    return "Data Flow"
                else:
                    return "Sequence Diagram"
        return "Flow Diagram"
    
    def convert_to_pdf(self) -> bool:
        """Convert all Mermaid diagrams to PDF."""
        print(f"Converting diagrams from: {self.input_file}")
        
        diagrams = self.extract_mermaid_blocks()
        if not diagrams:
            print("No Mermaid diagrams found in the file.")
            return False
        
        print(f"Found {len(diagrams)} diagram(s)")
        
        try:
            self.setup_driver()
            success_count = 0
            
            for diagram in diagrams:
                print(f"\nProcessing diagram {diagram['index']}...")
                if self.convert_diagram_to_pdf(diagram):
                    success_count += 1
            
            print(f"\n✓ Successfully converted {success_count}/{len(diagrams)} diagrams to PDF")
            print(f"Output directory: {self.output_dir.absolute()}")
            
            return success_count > 0
            
        finally:
            if self.driver:
                self.driver.quit()

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_pdf_converter.py <input_markdown_file> [output_directory]")
        print("\nExample:")
        print("  python simple_pdf_converter.py docs/flow-diagram.md")
        print("  python simple_pdf_converter.py docs/flow-diagram.md output_pdfs")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    converter = SimpleMermaidToPDFConverter(input_file, output_dir)
    success = converter.convert_to_pdf()
    
    if success:
        print("\n🎉 Conversion completed successfully!")
    else:
        print("\n❌ Conversion failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 