#!/usr/bin/env python3
"""
Process PDF with AI-powered image classification
Uses GPT-4 Vision to intelligently filter and describe images
"""

import sys
import json
import os
import re
import fitz  # PyMuPDF
from classify_image_enhanced import classify_and_describe_image

# Import helper functions from original script
def sort_by_position(items):
    """Sort items by reading order (top to bottom, left to right)"""
    return sorted(items, key=lambda item: (
        item.get('y', 0),
        item.get('x', 0)
    ))

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
    
    if is_metadata_section(line):
        return False
    
    if re.match(r'^\d+\.?\d*\s+[A-Z]', line):
        return True
    
    if len(line) > 15 and line.isupper() and sum(c.isalpha() for c in line) > 10:
        return True
    
    if re.match(r'^(UNIT|CHAPTER|MODULE|SECTION|TOPIC)\s+\d+', line, re.IGNORECASE):
        return True
    
    if allow_questions and line.endswith('?') and len(line) > 20:
        return True
    
    return False

def get_heading_level(line):
    """Get the level of a heading (1, 2, 3, etc.)"""
    match = re.match(r'^(\d+)(\.(\d+))?\s+', line)
    if match:
        if match.group(3):
            return 2
        return 1
    
    if line.isupper():
        return 1
    
    return 1

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

def process_pdf_with_ai(pdf_path, output_dir, azure_endpoint, azure_key, deployment):
    """Process PDF with AI-powered image classification"""
    try:
        doc = fitz.open(pdf_path)
        sections = []
        section_order = 0
        current_section = None
        in_metadata = True
        page_threshold = 3
        
        # Statistics
        stats = {
            'total_images_found': 0,
            'images_classified_important': 0,
            'images_classified_decorative': 0,
            'images_saved': 0,
            'total_tables': 0
        }
        
        print(f"Processing {len(doc)} pages with AI classification...", file=sys.stderr)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            if page_num >= page_threshold:
                in_metadata = False
            
            # Extract text blocks
            text_blocks = extract_text_blocks(page)
            
            # Extract and classify images with AI
            image_list = page.get_images()
            image_blocks = []
            stats['total_images_found'] += len(image_list)
            
            # Get current section context for better classification
            section_context = current_section['heading'] if current_section else ""
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    print(f"  Page {page_num + 1}, Image {img_index + 1}: Classifying with AI...", file=sys.stderr)
                    
                    # Classify with AI
                    classification = classify_and_describe_image(
                        image_bytes,
                        image_ext,
                        azure_endpoint,
                        azure_key,
                        deployment,
                        context=section_context
                    )
                    
                    if classification['is_important']:
                        # Save important image
                        image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                        image_path = os.path.join(output_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        stats['images_classified_important'] += 1
                        stats['images_saved'] += 1
                        
                        print(f"    ✓ {classification['image_type']} (score: {classification['relevance_score']}/10) - keeping", file=sys.stderr)
                        
                        # Add to blocks with AI metadata
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
                                'size_bytes': len(image_bytes),
                                'ai_classified': True,
                                'image_type': classification['image_type'],
                                'description': classification['description'],
                                'relevance_score': classification['relevance_score'],
                                'tags': classification['tags']
                            }
                        })
                    else:
                        stats['images_classified_decorative'] += 1
                        print(f"    ✗ Decorative - skipping", file=sys.stderr)
                        
                except Exception as e:
                    print(f"Error processing image: {e}", file=sys.stderr)
            
            # Extract tables
            table_blocks = []
            tables = page.find_tables()
            
            if tables and hasattr(tables, 'tables'):
                for table_index, table in enumerate(tables.tables):
                    try:
                        bbox = table.bbox
                        table_rect = fitz.Rect(bbox)
                        pix = page.get_pixmap(clip=table_rect, matrix=fitz.Matrix(2, 2))
                        
                        table_filename = f"page_{page_num + 1}_table_{table_index + 1}.png"
                        table_path = os.path.join(output_dir, table_filename)
                        pix.save(table_path)
                        
                        stats['total_tables'] += 1
                        
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
            
            # Combine and sort all blocks
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
                        
                        if in_metadata and is_metadata_section(line):
                            continue
                        
                        if is_heading(line, allow_questions=False):
                            level = get_heading_level(line)
                            
                            if level == 1 or current_section is None:
                                if current_section and len(current_section['blocks']) > 3:
                                    sections.append(current_section)
                                    section_order += 1
                                
                                current_section = {
                                    'order': section_order,
                                    'heading': line,
                                    'page': page_num + 1,
                                    'blocks': [],
                                    'level': level,
                                    'current_paragraph': []  # Buffer for combining lines
                                }
                                in_metadata = False
                        elif current_section and not in_metadata:
                            if line and len(line) > 3:
                                # Add line to current paragraph buffer
                                current_section['current_paragraph'].append(line)
                
                elif block['type'] == 'image' and current_section and not in_metadata:
                    # Flush current paragraph before adding image
                    if current_section.get('current_paragraph'):
                        paragraph_text = ' '.join(current_section['current_paragraph'])
                        current_section['blocks'].append({
                            'type': 'text',
                            'content': paragraph_text,
                            'order': len(current_section['blocks']),
                            'bbox': {
                                'x': 0,
                                'y': 0,
                                'width': 0,
                                'height': 0
                            }
                        })
                        current_section['current_paragraph'] = []
                    
                    # Add image
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
                    # Flush current paragraph before adding table
                    if current_section.get('current_paragraph'):
                        paragraph_text = ' '.join(current_section['current_paragraph'])
                        current_section['blocks'].append({
                            'type': 'text',
                            'content': paragraph_text,
                            'order': len(current_section['blocks']),
                            'bbox': {
                                'x': 0,
                                'y': 0,
                                'width': 0,
                                'height': 0
                            }
                        })
                        current_section['current_paragraph'] = []
                    
                    # Add table
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
        
        # Flush any remaining paragraph in the last section
        if current_section and current_section.get('current_paragraph'):
            paragraph_text = ' '.join(current_section['current_paragraph'])
            current_section['blocks'].append({
                'type': 'text',
                'content': paragraph_text,
                'order': len(current_section['blocks']),
                'bbox': {
                    'x': 0,
                    'y': 0,
                    'width': 0,
                    'height': 0
                }
            })
            del current_section['current_paragraph']
        
        # Add last section
        if current_section and len(current_section['blocks']) > 3:
            # Clean up current_paragraph field if it exists
            if 'current_paragraph' in current_section:
                del current_section['current_paragraph']
            sections.append(current_section)
        
        doc.close()
        
        # Filter meaningful sections
        meaningful_sections = [s for s in sections if len(s['blocks']) >= 5]
        
        print(f"\n📊 AI Classification Statistics:", file=sys.stderr)
        print(f"  Total images found: {stats['total_images_found']}", file=sys.stderr)
        print(f"  Classified as important: {stats['images_classified_important']}", file=sys.stderr)
        print(f"  Classified as decorative: {stats['images_classified_decorative']}", file=sys.stderr)
        print(f"  Images saved: {stats['images_saved']}", file=sys.stderr)
        print(f"  Tables extracted: {stats['total_tables']}\n", file=sys.stderr)
        
        return {
            'success': True,
            'sections': meaningful_sections[:20],
            'total_sections': len(meaningful_sections),
            'statistics': stats
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        
        print(f"Error: {error_msg}", file=sys.stderr)
        print(traceback_str, file=sys.stderr)
        
        return {
            'success': False,
            'error': error_msg,
            'traceback': traceback_str
        }

if __name__ == '__main__':
    if len(sys.argv) < 6:
        result = {
            'success': False,
            'error': 'Usage: python process_pdf_with_ai.py <pdf_path> <output_dir> <azure_endpoint> <azure_key> <deployment>'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    azure_endpoint = sys.argv[3]
    azure_key = sys.argv[4]
    deployment = sys.argv[5]
    
    try:
        result = process_pdf_with_ai(pdf_path, output_dir, azure_endpoint, azure_key, deployment)
        print(json.dumps(result, indent=2))
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
