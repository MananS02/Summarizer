#!/usr/bin/env python3
"""
Process PDF with LlamaParse layout extraction
Creates ordered blocks for text, tables, and images
"""

import sys
import json
import os
from llama_cloud_services import LlamaParse

def sort_by_position(items):
    """Sort layout items by reading order (top to bottom, left to right)"""
    return sorted(items, key=lambda item: (
        item.get('bbox', {}).get('y', 0),
        item.get('bbox', {}).get('x', 0)
    ))

def create_block(item, order):
    """Create a block from a layout item"""
    label = item.get('label', 'text')
    
    block = {
        'order': order,
        'bbox': item.get('bbox', {})
    }
    
    if label == 'table':
        block['type'] = 'table'
        # LlamaParse returns HTML table
        block['content'] = item.get('html', item.get('text', ''))
    elif label == 'figure' or label == 'image':
        block['type'] = 'image'
        # Image name from LlamaParse
        block['content'] = item.get('image_name', '')
    else:
        block['type'] = 'text'
        block['content'] = item.get('text', '')
    
    return block

def process_layout_items(pages, sections):
    """Process layout items and assign to sections in reading order"""
    
    for section in sections:
        blocks = []
        order = 0
        
        # Get pages for this section (based on page range)
        start_page = section.get('page', 1) - 1  # 0-indexed
        end_page = start_page + 1  # For now, assume 1 page per section
        
        for page_num in range(start_page, min(end_page, len(pages))):
            if page_num >= len(pages):
                break
                
            page = pages[page_num]
            
            # Get layout items from page
            layout_items = page.get('layout', [])
            
            if not layout_items:
                # Fallback: use text if no layout
                text = page.get('text', '')
                if text:
                    blocks.append({
                        'type': 'text',
                        'content': text,
                        'order': order,
                        'bbox': {}
                    })
                    order += 1
                continue
            
            # Sort items by position
            sorted_items = sort_by_position(layout_items)
            
            # Create blocks
            for item in sorted_items:
                block = create_block(item, order)
                if block['content']:  # Only add non-empty blocks
                    blocks.append(block)
                    order += 1
        
        section['blocks'] = blocks
    
    return sections

def parse_pdf_with_layout(pdf_path, api_key):
    """Parse PDF using LlamaParse with layout extraction"""
    try:
        # Initialize parser with layout extraction
        parser = LlamaParse(
            api_key=api_key,
            result_type="json",  # Get JSON with layout info
            extract_layout=True,  # Enable layout extraction
            output_tables_as_HTML=True,  # Get HTML tables
            num_workers=1,
            verbose=True,
            language="en"
        )
        
        # Parse the PDF
        print(f"Parsing {pdf_path} with layout extraction...", file=sys.stderr)
        result = parser.parse(pdf_path)
        
        # Extract pages and sections
        pages = []
        sections = []
        section_order = 0
        
        for page_num, page in enumerate(result.pages):
            page_data = {
                'page_num': page_num + 1,
                'text': page.text if hasattr(page, 'text') else '',
                'md': page.md if hasattr(page, 'md') else '',
                'layout': []
            }
            
            # Get layout items if available
            if hasattr(page, 'layout') and page.layout:
                for item in page.layout:
                    layout_item = {
                        'label': getattr(item, 'label', 'text'),
                        'text': getattr(item, 'text', ''),
                        'html': getattr(item, 'html', ''),
                        'image_name': getattr(item, 'image_name', ''),
                        'bbox': {
                            'x': getattr(item.bbox, 'x', 0) if hasattr(item, 'bbox') else 0,
                            'y': getattr(item.bbox, 'y', 0) if hasattr(item, 'bbox') else 0,
                            'width': getattr(item.bbox, 'width', 0) if hasattr(item, 'bbox') else 0,
                            'height': getattr(item.bbox, 'height', 0) if hasattr(item, 'bbox') else 0
                        }
                    }
                    page_data['layout'].append(layout_item)
            
            pages.append(page_data)
            
            # Identify sections from headings
            text = page_data['text']
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a heading
                is_heading = False
                
                # All caps heading
                if len(line) > 10 and line.isupper() and sum(c.isalpha() for c in line) > 5:
                    is_heading = True
                
                # Numbered heading
                if line and line[0].isdigit() and '.' in line[:10]:
                    is_heading = True
                
                if is_heading:
                    sections.append({
                        'order': section_order,
                        'heading': line,
                        'page': page_num + 1,
                        'blocks': []
                    })
                    section_order += 1
        
        # Process layout items for each section
        sections = process_layout_items(pages, sections)
        
        return {
            'success': True,
            'sections': sections[:20],  # Limit to 20 sections
            'total_sections': len(sections),
            'total_pages': len(pages)
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python process_layout.py <pdf_path> <api_key>'
        }))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    api_key = sys.argv[2]
    
    result = parse_pdf_with_layout(pdf_path, api_key)
    print(json.dumps(result, indent=2))
