#!/usr/bin/env python3
"""
Process PDF with PyMuPDF and create ordered blocks
Fallback when LlamaParse has compatibility issues
"""

import sys
import json
import os
import re
import fitz  # PyMuPDF

def sort_by_position(items):
    """Sort items by reading order (top to bottom, left to right)"""
    return sorted(items, key=lambda item: (
        item.get('y', 0),
        item.get('x', 0)
    ))

def extract_text_blocks(page):
    """Extract text blocks with positions"""
    blocks = []
    text_dict = page.get_text("dict")
    
    for block in text_dict.get("blocks", []):
        if block.get("type") == 0:  # Text block
            bbox = block.get("bbox", [0, 0, 0, 0])
            text = ""
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text += span.get("text", "")
                text += "\n"
            
            if text.strip():
                blocks.append({
                    'type': 'text',
                    'content': text.strip(),
                    'x': bbox[0],
                    'y': bbox[1],
                    'width': bbox[2] - bbox[0],
                    'height': bbox[3] - bbox[1]
                })
    
    return blocks

def is_metadata_section(text):
    """Check if text is from metadata sections that should be skipped"""
    metadata_keywords = [
        'key learning outcomes',
        'participant handbook',
        'table of contents',
        'unit objectives',
        'at the end of this unit'
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in metadata_keywords)

def is_heading(line, allow_questions=False):
    """Check if line is a heading"""
    line = line.strip()
    if not line or len(line) < 5:
        return False
    
    # Skip metadata sections
    if is_metadata_section(line):
        return False
    
    # Pattern 1: Numbered heading like "1. Introduction" or "1.1 Overview"
    # Must have letter after number to avoid page numbers
    if re.match(r'^\d+\.?\d*\s+[A-Z]', line):
        return True
    
    # Pattern 2: All caps heading (at least 15 chars, mostly letters)
    if len(line) > 15 and line.isupper() and sum(c.isalpha() for c in line) > 10:
        return True
    
    # Pattern 3: Unit/Chapter/Module heading
    if re.match(r'^(UNIT|CHAPTER|MODULE|SECTION|TOPIC)\s+\d+', line, re.IGNORECASE):
        return True
    
    # Pattern 4: Questions (only if allowed)
    if allow_questions and line.endswith('?') and len(line) > 20:
        return True
    
    return False

def get_heading_level(line):
    """Get the level of a heading (1, 2, 3, etc.)"""
    # Numbered headings: "1." is level 1, "1.1" is level 2
    match = re.match(r'^(\d+)(\.(\d+))?\s+', line)
    if match:
        if match.group(3):  # Has sub-number like "1.1"
            return 2
        return 1
    
    # All caps headings are level 1
    if line.isupper():
        return 1
    
    return 1

def process_pdf_with_blocks(pdf_path, output_dir):
    """Process PDF and create ordered blocks"""
    try:
        doc = fitz.open(pdf_path)
        sections = []
        section_order = 0
        current_section = None
        in_metadata = True  # Start assuming we're in metadata
        page_threshold = 3  # Start looking for real content after page 3
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # After page 3, we're likely past metadata
            if page_num >= page_threshold:
                in_metadata = False
            
            # Extract text blocks with positions
            text_blocks = extract_text_blocks(page)
            
            # Extract images and tables
            image_list = page.get_images()
            image_blocks = []
            table_blocks = []
            
            # Detect tables by looking for table-like structures
            # Tables often have grid patterns or are in specific regions
            tables = page.find_tables()  # PyMuPDF table detection
            
            if tables and hasattr(tables, 'tables'):
                for table_index, table in enumerate(tables.tables):
                    try:
                        # Get table bounding box
                        bbox = table.bbox
                        
                        # Extract table region as image
                        table_rect = fitz.Rect(bbox)
                        pix = page.get_pixmap(clip=table_rect, matrix=fitz.Matrix(2, 2))  # 2x resolution
                        
                        # Save table image
                        table_filename = f"page_{page_num + 1}_table_{table_index + 1}.png"
                        table_path = os.path.join(output_dir, table_filename)
                        pix.save(table_path)
                        
                        table_blocks.append({
                            'type': 'table',
                            'content': table_filename,
                            'x': bbox[0],
                            'y': bbox[1],
                            'width': bbox[2] - bbox[0],
                            'height': bbox[3] - bbox[1],
                            'metadata': {
                                'is_table': True,
                                'rows': len(table.rows) if hasattr(table, 'rows') else 0,
                                'cols': len(table.header.cells) if hasattr(table, 'header') else 0
                            }
                        })
                    except Exception as e:
                        print(f"Error extracting table: {e}", file=sys.stderr)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Skip very small images (likely icons/decorations)
                    # These appear as black boxes and aren't useful
                    if len(image_bytes) < 5000:  # Less than 5KB
                        continue
                    
                    # Save image
                    image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # Get image position (approximate)
                    image_blocks.append({
                        'type': 'image',
                        'content': image_filename,
                        'x': 0,
                        'y': img_index * 100,
                        'width': 0,
                        'height': 0,
                        'metadata': {
                            'is_table': False,
                            'format': image_ext,
                            'size_bytes': len(image_bytes)
                        }
                    })
                except:
                    pass
            
            # Combine and sort all blocks (text, images, tables)
            all_blocks = text_blocks + image_blocks + table_blocks
            sorted_blocks = sort_by_position(all_blocks)
            
            # Process blocks to identify sections
            for block in sorted_blocks:
                if block['type'] == 'text':
                    content = block['content']
                    lines = content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Check if we're still in metadata
                        if in_metadata and is_metadata_section(line):
                            continue
                        
                        # Check if line is a heading
                        if is_heading(line, allow_questions=False):
                            # Get heading level
                            level = get_heading_level(line)
                            
                            # Only create new section for level 1 headings
                            # or if we don't have a current section
                            if level == 1 or current_section is None:
                                # Save previous section if it has content
                                if current_section and len(current_section['blocks']) > 3:
                                    sections.append(current_section)
                                    section_order += 1
                                
                                # Start new section
                                current_section = {
                                    'order': section_order,
                                    'heading': line,
                                    'page': page_num + 1,
                                    'blocks': [],
                                    'level': level
                                }
                                in_metadata = False  # We found a real heading
                        elif current_section and not in_metadata:
                            # Add text to current section
                            if line and len(line) > 3:  # Skip very short lines
                                current_section['blocks'].append({
                                    'type': 'text',
                                    'content': line,
                                    'order': len(current_section['blocks']),
                                    'bbox': {
                                        'x': block['x'],
                                        'y': block['y'],
                                        'width': block['width'],
                                        'height': block['height']
                                    }
                                })
                elif block['type'] == 'image' and current_section and not in_metadata:
                    # Add image to current section
                    current_section['blocks'].append({
                        'type': 'image',
                        'content': block['content'],
                        'order': len(current_section['blocks']),
                        'bbox': {
                            'x': block['x'],
                            'y': block['y'],
                            'width': block['width'],
                            'height': block['height']
                        },
                        'metadata': block.get('metadata', {})
                    })
                elif block['type'] == 'table' and current_section and not in_metadata:
                    # Add table to current section
                    current_section['blocks'].append({
                        'type': 'table',
                        'content': block['content'],
                        'order': len(current_section['blocks']),
                        'bbox': {
                            'x': block['x'],
                            'y': block['y'],
                            'width': block['width'],
                            'height': block['height']
                        },
                        'metadata': block.get('metadata', {})
                    })
        
        # Add last section
        if current_section and len(current_section['blocks']) > 3:
            sections.append(current_section)
        
        doc.close()
        
        # Filter meaningful sections (must have at least 5 blocks)
        meaningful_sections = [s for s in sections if len(s['blocks']) >= 5]
        
        return {
            'success': True,
            'sections': meaningful_sections[:20],
            'total_sections': len(meaningful_sections)
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        
        # Print error to stderr
        print(f"Error: {error_msg}", file=sys.stderr)
        print(traceback_str, file=sys.stderr)
        
        return {
            'success': False,
            'error': error_msg,
            'traceback': traceback_str
        }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        result = {
            'success': False,
            'error': 'Usage: python process_pdf_blocks.py <pdf_path> <output_dir>'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    try:
        result = process_pdf_with_blocks(pdf_path, output_dir)
        print(json.dumps(result, indent=2))
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
