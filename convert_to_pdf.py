#!/usr/bin/env python3
"""
Modern Markdown to PDF Converter
Converts the endpoint-usage-examples.md to a beautifully designed PDF
"""

import markdown
import pdfkit
import os
from pathlib import Path

def create_modern_html_template():
    """Create a modern HTML template with beautiful styling"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Seller Backend - Unity Integration Guide</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: #ffffff;
            font-size: 14px;
        }
        
        .container {
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Headers */
        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-align: center;
        }
        
        h2 {
            font-size: 1.8rem;
            font-weight: 600;
            color: #2d3748;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        h3 {
            font-size: 1.4rem;
            font-weight: 600;
            color: #4a5568;
            margin: 1.5rem 0 0.8rem 0;
            padding: 12px 16px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
        }
        
        h4 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            margin: 1rem 0 0.5rem 0;
        }
        
        /* Paragraphs and text */
        p {
            margin-bottom: 1rem;
            text-align: justify;
        }
        
        /* Lists */
        ul, ol {
            margin: 1rem 0;
            padding-left: 2rem;
        }
        
        li {
            margin-bottom: 0.5rem;
        }
        
        /* Code blocks */
        pre {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        
        code {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: #f7fafc;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #e53e3e;
        }
        
        pre code {
            background: none;
            padding: 0;
            color: #2d3748;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
            font-size: 0.9rem;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        
        th {
            background: #f7fafc;
            font-weight: 600;
            color: #2d3748;
        }
        
        tr:hover {
            background: #f7fafc;
        }
        
        /* Blockquotes */
        blockquote {
            border-left: 4px solid #667eea;
            background: #f7fafc;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }
        
        /* Styled divs */
        div[style*="background: linear-gradient"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            padding: 20px !important;
            border-radius: 10px !important;
            margin: 10px 0 !important;
        }
        
        div[style*="background: linear-gradient"] strong {
            color: white !important;
        }
        
        /* Details/Summary */
        details {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        summary {
            font-weight: 600;
            cursor: pointer;
            padding: 0.5rem 0;
            color: #4a5568;
        }
        
        summary:hover {
            color: #667eea;
        }
        
        /* Links */
        a {
            color: #667eea;
            text-decoration: none;
        }
        
        a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        
        /* Emojis */
        .emoji {
            font-size: 1.2em;
        }
        
        /* Page breaks */
        .page-break {
            page-break-before: always;
        }
        
        /* Print styles */
        @media print {
            body {
                font-size: 12px;
            }
            
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            h2 {
                font-size: 1.5rem;
            }
            
            h3 {
                font-size: 1.2rem;
            }
            
            pre {
                font-size: 0.8rem;
            }
        }
        
        /* Center alignment for title section */
        div[align="center"] {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        div[align="center"] h1 {
            margin-bottom: 0.5rem;
        }
        
        div[align="center"] h2 {
            font-size: 1.5rem;
            color: #667eea;
            margin-bottom: 0.5rem;
            border: none;
        }
        
        div[align="center"] em {
            font-size: 1.1rem;
            color: #718096;
            font-style: italic;
        }
        
        /* Feature list styling */
        ul li strong {
            color: #2d3748;
        }
        
        /* JSON syntax highlighting */
        .json-key {
            color: #e53e3e;
        }
        
        .json-string {
            color: #38a169;
        }
        
        .json-number {
            color: #3182ce;
        }
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
"""

def convert_markdown_to_pdf(input_file, output_file):
    """Convert markdown file to modern PDF"""
    
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'codehilite',
        'toc',
        'attr_list'
    ])
    
    html_content = md.convert(markdown_content)
    
    # Create full HTML with styling
    html_template = create_modern_html_template()
    full_html = html_template.format(content=html_content)
    
    # Write HTML file for debugging
    html_file = output_file.replace('.pdf', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    # PDF options for better quality
    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None,
        'enable-local-file-access': None,
        'print-media-type': None,
        'disable-smart-shrinking': None,
        'zoom': '0.8',
        'dpi': 300,
        'image-quality': 100,
        'image-dpi': 300,
    }
    
    try:
        # Convert HTML to PDF
        pdfkit.from_string(full_html, output_file, options=options)
        print(f"✅ Successfully created PDF: {output_file}")
        print(f"📄 HTML preview available at: {html_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating PDF: {str(e)}")
        print("💡 Make sure wkhtmltopdf is installed:")
        print("   - Windows: Download from https://wkhtmltopdf.org/downloads.html")
        print("   - macOS: brew install wkhtmltopdf")
        print("   - Ubuntu: sudo apt-get install wkhtmltopdf")
        return False

def main():
    """Main function to convert the documentation"""
    
    # File paths
    input_file = "docs/endpoint-usage-examples.md"
    output_file = "AI_Agent_Seller_Unity_Integration_Guide.pdf"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return
    
    print("🚀 Converting Markdown to Modern PDF...")
    print(f"📖 Input: {input_file}")
    print(f"📄 Output: {output_file}")
    print()
    
    # Convert to PDF
    success = convert_markdown_to_pdf(input_file, output_file)
    
    if success:
        file_size = os.path.getsize(output_file) / 1024 / 1024  # MB
        print(f"📊 File size: {file_size:.2f} MB")
        print()
        print("🎉 Conversion completed successfully!")
        print("📋 Features included:")
        print("   ✅ Modern typography with Inter font")
        print("   ✅ Syntax highlighted code blocks")
        print("   ✅ Responsive design")
        print("   ✅ Professional styling")
        print("   ✅ Optimized for printing")
    else:
        print("❌ Conversion failed. Please check the error messages above.")

if __name__ == "__main__":
    main()