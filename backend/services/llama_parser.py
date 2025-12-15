#!/usr/bin/env python3
"""
LlamaParser PDF Processing Script
Parses a PDF file using LlamaParser and outputs JSON with sections
"""

import sys
import json
import os
from llama_cloud_services import LlamaParse

def parse_pdf(pdf_path, api_key):
    """Parse PDF using LlamaParser"""
    try:
        # Initialize parser
        parser = LlamaParse(
            api_key=api_key,
            num_workers=1,
            verbose=True,
            language="en",
            result_type="markdown"
        )
        
        # Parse the PDF
        print(f"Parsing {pdf_path}...", file=sys.stderr)
        result = parser.parse(pdf_path)
        
        # Extract sections from markdown
        sections = []
        order = 0
        
        for page in result.pages:
            markdown = page.md
            
            # Split by headings
            lines = markdown.split('\n')
            current_section = None
            
            for line in lines:
                # Check if line is a heading (# or ##)
                if line.startswith('# ') or line.startswith('## '):
                    # Save previous section
                    if current_section and current_section['content'].strip():
                        sections.append(current_section)
                        order += 1
                    
                    # Start new section
                    heading = line.lstrip('#').strip()
                    current_section = {
                        'order': order,
                        'heading': heading,
                        'content': '',
                        'images': [],
                        'tables': []
                    }
                elif current_section:
                    current_section['content'] += line + '\n'
            
            # Add last section from page
            if current_section and current_section['content'].strip():
                sections.append(current_section)
                order += 1
        
        # If no sections found, create one with all content
        if not sections:
            all_content = '\n'.join([page.md for page in result.pages])
            sections.append({
                'order': 0,
                'heading': 'Document Content',
                'content': all_content,
                'images': [],
                'tables': []
            })
        
        # Output JSON
        output = {
            'success': True,
            'sections': sections,
            'page_count': len(result.pages)
        }
        
        print(json.dumps(output))
        return 0
        
    except Exception as e:
        error_output = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_output))
        return 1

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python llama_parser.py <pdf_path> <api_key>'
        }))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2]
    
    sys.exit(parse_pdf(pdf_path, api_key))
