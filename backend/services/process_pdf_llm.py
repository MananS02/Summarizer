#!/usr/bin/env python3
"""
Process PDF with LLM-based heading detection and AI image classification
Uses GPT-4 to identify proper headings, then extracts content for each section
"""

import sys
import json
import os
import fitz  # PyMuPDF
from identify_headings_llm import extract_pdf_text, identify_headings_with_llm
from classify_image_enhanced import classify_and_describe_image

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

def process_pdf_with_llm_headings(pdf_path, output_dir, azure_endpoint, azure_key, deployment):
    """Process PDF using LLM-identified headings"""
    try:
        # Step 1: Extract text and identify headings with GPT-4
        print("=" * 60, file=sys.stderr)
        print("STEP 1: Identifying headings with GPT-4", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        pages_text = extract_pdf_text(pdf_path)
        headings_result = identify_headings_with_llm(pages_text, azure_endpoint, azure_key, deployment)
        
        if not headings_result:
            return {
                'success': False,
                'error': 'Failed to identify headings'
            }
        
        print(f"\n✓ Identified {len(headings_result)} headings\n", file=sys.stderr)
        
        # Step 2: Process PDF with identified headings
        print("=" * 60, file=sys.stderr)
        print("STEP 2: Extracting content for each section", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        
        doc = fitz.open(pdf_path)
        sections = []
        
        stats = {
            'total_images_found': 0,
            'images_classified_important': 0,
            'images_classified_decorative': 0,
            'images_saved': 0,
            'total_tables': 0
        }
        
        # Process each heading as a section
        for idx, heading_info in enumerate(headings_result):
            heading = heading_info['heading']
            start_page = heading_info['start_page'] - 1  # Convert to 0-indexed
            
            # Determine end page (start of next section or end of document)
            if idx < len(headings_result) - 1:
                end_page = headings_result[idx + 1]['start_page'] - 2
            else:
                end_page = len(doc) - 1
            
            print(f"\n[{idx + 1}/{len(headings_result)}] {heading}", file=sys.stderr)
            print(f"  Pages: {start_page + 1} to {end_page + 1}", file=sys.stderr)
            
            # Extract content for this section
            section_blocks = []
            current_paragraph = []
            
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                
                # Extract text blocks
                text_blocks = extract_text_blocks(page)
                
                # Extract images with AI classification
                image_list = page.get_images()
                stats['total_images_found'] += len(image_list)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Classify with AI
                        classification = classify_and_describe_image(
                            image_bytes,
                            image_ext,
                            azure_endpoint,
                            azure_key,
                            deployment,
                            context=heading
                        )
                        
                        if classification['is_important']:
                            # Flush current paragraph before image
                            if current_paragraph:
                                section_blocks.append({
                                    'type': 'text',
                                    'content': ' '.join(current_paragraph),
                                    'order': len(section_blocks)
                                })
                                current_paragraph = []
                            
                            # Save image
                            image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                            image_path = os.path.join(output_dir, image_filename)
                            
                            with open(image_path, "wb") as img_file:
                                img_file.write(image_bytes)
                            
                            stats['images_classified_important'] += 1
                            stats['images_saved'] += 1
                            
                            # Add image block
                            section_blocks.append({
                                'type': 'image',
                                'content': image_filename,
                                'order': len(section_blocks),
                                'metadata': {
                                    'ai_classified': True,
                                    'image_type': classification['image_type'],
                                    'description': classification['description'],
                                    'relevance_score': classification['relevance_score'],
                                    'tags': classification['tags']
                                }
                            })
                        else:
                            stats['images_classified_decorative'] += 1
                            
                    except Exception as e:
                        print(f"  Error processing image: {e}", file=sys.stderr)
                
                # Extract tables
                tables = page.find_tables()
                if tables and hasattr(tables, 'tables'):
                    for table_index, table in enumerate(tables.tables):
                        try:
                            # Flush current paragraph before table
                            if current_paragraph:
                                section_blocks.append({
                                    'type': 'text',
                                    'content': ' '.join(current_paragraph),
                                    'order': len(section_blocks)
                                })
                                current_paragraph = []
                            
                            bbox = table.bbox
                            table_rect = fitz.Rect(bbox)
                            pix = page.get_pixmap(clip=table_rect, matrix=fitz.Matrix(2, 2))
                            
                            table_filename = f"page_{page_num + 1}_table_{table_index + 1}.png"
                            table_path = os.path.join(output_dir, table_filename)
                            pix.save(table_path)
                            
                            stats['total_tables'] += 1
                            
                            section_blocks.append({
                                'type': 'table',
                                'content': table_filename,
                                'order': len(section_blocks),
                                'metadata': {
                                    'is_table': True,
                                    'rows': len(table.rows) if hasattr(table, 'rows') else 0,
                                    'cols': len(table.header.cells) if hasattr(table, 'header') else 0
                                }
                            })
                        except Exception as e:
                            print(f"  Error extracting table: {e}", file=sys.stderr)
                
                # Add text to paragraph buffer
                for block in text_blocks:
                    lines = block['content'].split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 3:
                            # Skip if it's the heading itself
                            if line != heading:
                                current_paragraph.append(line)
            
            # Flush final paragraph
            if current_paragraph:
                section_blocks.append({
                    'type': 'text',
                    'content': ' '.join(current_paragraph),
                    'order': len(section_blocks)
                })
            
            # Create section
            if len(section_blocks) >= 3:  # Only keep sections with meaningful content
                sections.append({
                    'order': idx,
                    'heading': heading,
                    'level': heading_info.get('level', 1),
                    'page': start_page + 1,
                    'blocks': section_blocks
                })
                print(f"  ✓ Created section with {len(section_blocks)} blocks", file=sys.stderr)
            else:
                print(f"  ✗ Skipped (too few blocks)", file=sys.stderr)
        
        doc.close()
        
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"PROCESSING COMPLETE", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        print(f"Sections created: {len(sections)}", file=sys.stderr)
        print(f"Images (important): {stats['images_classified_important']}", file=sys.stderr)
        print(f"Images (decorative): {stats['images_classified_decorative']}", file=sys.stderr)
        print(f"Tables: {stats['total_tables']}\n", file=sys.stderr)
        
        return {
            'success': True,
            'sections': sections,
            'total_sections': len(sections),
            'statistics': stats
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

if __name__ == '__main__':
    if len(sys.argv) < 6:
        result = {
            'success': False,
            'error': 'Usage: python process_pdf_llm.py <pdf_path> <output_dir> <azure_endpoint> <azure_key> <deployment>'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    azure_endpoint = sys.argv[3]
    azure_key = sys.argv[4]
    deployment = sys.argv[5]
    
    try:
        result = process_pdf_with_llm_headings(pdf_path, output_dir, azure_endpoint, azure_key, deployment)
        print(json.dumps(result, indent=2))
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
