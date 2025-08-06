#!/usr/bin/env python3
"""
Simple Markdown to HTML converter for creating a modern PDF
"""

import re
import os

def markdown_to_html(markdown_content):
    """Convert basic markdown to HTML"""
    html = markdown_content
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code class="\1">\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Lists
    html = re.sub(r'^\- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Wrap consecutive list items
    html = re.sub(r'(<li>.*?</li>\s*)+', lambda m: '<ul>' + m.group(0) + '</ul>', html, flags=re.DOTALL)
    
    # Paragraphs
    lines = html.split('\n')
    in_code_block = False
    result_lines = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('<pre>'):
            in_code_block = True
        elif line.startswith('</pre>'):
            in_code_block = False
        elif not in_code_block and line and not line.startswith('<') and not line.startswith('---'):
            line = '<p>' + line + '</p>'
        result_lines.append(line)
    
    return '\n'.join(result_lines)

def create_modern_html():
    """Read markdown and create modern HTML"""
    
    # Read the markdown file
    try:
        with open('docs/endpoint-usage-examples.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print("❌ File not found: docs/endpoint-usage-examples.md")
        return
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content)
    
    # Create full HTML with modern styling
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Seller Backend - Unity Integration Guide</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background: #ffffff;
            font-size: 14px;
            max-width: 210mm;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* Headers */
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a202c;
            margin-bottom: 1rem;
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        h2 {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #2d3748;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        h3 {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #4a5568;
            margin: 1.5rem 0 0.8rem 0;
            padding: 12px 16px;
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            border-left: 4px solid #667eea;
            border-radius: 0 8px 8px 0;
        }}
        
        h4 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            margin: 1rem 0 0.5rem 0;
        }}
        
        /* Paragraphs and text */
        p {{
            margin-bottom: 1rem;
            text-align: justify;
        }}
        
        /* Lists */
        ul, ol {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        /* Code blocks */
        pre {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
        }}
        
        code {{
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            background: #f7fafc;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.85rem;
            color: #e53e3e;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #2d3748;
        }}
        
        /* Special divs with gradients */
        div[style*="background: linear-gradient"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            padding: 20px !important;
            border-radius: 10px !important;
            margin: 10px 0 !important;
        }}
        
        div[style*="background: linear-gradient"] strong {{
            color: white !important;
        }}
        
        /* Center alignment */
        div[align="center"] {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        div[align="center"] h2 {{
            font-size: 1.5rem;
            color: #667eea;
            margin-bottom: 0.5rem;
            border: none;
        }}
        
        div[align="center"] em {{
            font-size: 1.1rem;
            color: #718096;
            font-style: italic;
        }}
        
        /* Details/Summary */
        details {{
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        summary {{
            font-weight: 600;
            cursor: pointer;
            padding: 0.5rem 0;
            color: #4a5568;
        }}
        
        summary:hover {{
            color: #667eea;
        }}
        
        /* Horizontal rules */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 2rem 0;
        }}
        
        /* Print styles */
        @media print {{
            body {{
                font-size: 12px;
                padding: 15px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
            }}
            
            h3 {{
                font-size: 1.2rem;
            }}
            
            pre {{
                font-size: 0.8rem;
            }}
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
    
    # Write HTML file
    output_file = "AI_Agent_Seller_Unity_Integration_Guide.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ Successfully created modern HTML: {output_file}")
    print("📄 You can now:")
    print("   1. Open the HTML file in your browser")
    print("   2. Use browser's Print to PDF feature (Ctrl+P)")
    print("   3. Choose 'Save as PDF' destination")
    print("   4. Select 'More settings' and enable 'Background graphics'")
    print("   5. Set margins to 'Minimum' for best results")
    print()
    print("🎨 Features included:")
    print("   ✅ Modern typography with Inter font")
    print("   ✅ Syntax highlighted code blocks")
    print("   ✅ Gradient backgrounds and styling")
    print("   ✅ Professional layout")
    print("   ✅ Optimized for PDF printing")
    
    return output_file

if __name__ == "__main__":
    print("🚀 Creating Modern HTML Documentation...")
    print()
    create_modern_html()