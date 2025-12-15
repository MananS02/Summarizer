#!/usr/bin/env python3
"""
Process PDF with intelligent image filtering using GPT-4 Vision
"""

import sys
import json
import os
import re
import fitz  # PyMuPDF
from classify_image import classify_image

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

def process_pdf_with_ai_filtering(pdf_path, output_dir, azure_endpoint, azure_key, deployment, use_ai=True):
    """
    Process PDF with AI-powered image filtering
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save images
        azure_endpoint: Azure OpenAI endpoint
        azure_key: Azure OpenAI API key
        deployment: Azure OpenAI deployment name
        use_ai: Whether to use AI filtering (default: True)
    """
    try:
        doc = fitz.open(pdf_path)
        
        # Statistics
        total_images_found = 0
        images_classified_important = 0
        images_classified_skip = 0
        images_saved = 0
        
        print(f"Processing {len(doc)} pages...", file=sys.stderr)
        print(f"AI filtering: {'enabled' if use_ai else 'disabled (size-based)'}", file=sys.stderr)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract images
            image_list = page.get_images()
            total_images_found += len(image_list)
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Decide whether to keep image
                    should_keep = False
                    
                    if use_ai:
                        # Use AI to classify
                        print(f"  Page {page_num + 1}, Image {img_index + 1}: Classifying with AI...", file=sys.stderr)
                        is_important = classify_image(image_bytes, image_ext, azure_endpoint, azure_key, deployment)
                        
                        if is_important:
                            should_keep = True
                            images_classified_important += 1
                            print(f"    ✓ Important - keeping", file=sys.stderr)
                        else:
                            images_classified_skip += 1
                            print(f"    ✗ Decorative - skipping", file=sys.stderr)
                    else:
                        # Use size-based filtering
                        if len(image_bytes) >= 5000:  # 5KB threshold
                            should_keep = True
                    
                    # Save if important
                    if should_keep:
                        image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                        image_path = os.path.join(output_dir, image_filename)
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        images_saved += 1
                        
                except Exception as e:
                    print(f"Error processing image: {e}", file=sys.stderr)
        
        doc.close()
        
        # Return statistics
        return {
            'success': True,
            'total_images_found': total_images_found,
            'images_classified_important': images_classified_important,
            'images_classified_skip': images_classified_skip,
            'images_saved': images_saved,
            'ai_filtering_used': use_ai
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
            'error': 'Usage: python process_pdf_ai.py <pdf_path> <output_dir> <azure_endpoint> <azure_key> <deployment> [use_ai]'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    azure_endpoint = sys.argv[3]
    azure_key = sys.argv[4]
    deployment = sys.argv[5]
    use_ai = sys.argv[6].lower() == 'true' if len(sys.argv) > 6 else True
    
    try:
        result = process_pdf_with_ai_filtering(
            pdf_path, 
            output_dir, 
            azure_endpoint, 
            azure_key, 
            deployment,
            use_ai
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
