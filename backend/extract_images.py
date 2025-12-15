#!/usr/bin/env python3
"""
Extract images and tables from PDF using pdf2image and PyMuPDF
"""

import sys
import os
import json
import fitz  # PyMuPDF
from pathlib import Path

def extract_images_and_tables(pdf_path, output_dir):
    """Extract all images from PDF"""
    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        
        images = []
        page_data = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract images from page
            image_list = page.get_images()
            
            page_images = []
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                page_images.append(image_filename)
                images.append({
                    'page': page_num + 1,
                    'filename': image_filename,
                    'index': img_index
                })
            
            # Get text to identify sections
            text = page.get_text()
            
            page_data.append({
                'page': page_num + 1,
                'images': page_images,
                'text_preview': text[:200] if text else ''
            })
        
        doc.close()
        
        return {
            'success': True,
            'total_images': len(images),
            'images': images,
            'pages': page_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python extract_images.py <pdf_path> <output_dir>'
        }))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    result = extract_images_and_tables(pdf_path, output_dir)
    print(json.dumps(result, indent=2))
