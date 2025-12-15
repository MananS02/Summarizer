#!/usr/bin/env python3
"""
Process PDF: Extract text, headings, images and create sections
"""

import sys
import json
import os
import re
import fitz  # PyMuPDF

def process_pdf(pdf_path, output_dir):
    """Process PDF and extract sections with images"""
    try:
        doc = fitz.open(pdf_path)
        sections = []
        current_section = None
        section_order = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            lines = text.split('\n')
            
            # Extract images from this page
            page_images = []
            image_list = page.get_images()
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
            
            # Process lines to find headings and content
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line is a heading (all caps, or numbered heading)
                is_heading = False
                
                # Pattern 1: All caps line (at least 10 chars, mostly letters)
                if len(line) > 10 and line.isupper() and sum(c.isalpha() for c in line) > 5:
                    is_heading = True
                
                # Pattern 2: Numbered heading like "1.1 Introduction"
                if re.match(r'^\d+\.?\d*\s+[A-Z]', line):
                    is_heading = True
                
                # Pattern 3: Unit/Chapter heading
                if re.match(r'^(UNIT|CHAPTER|MODULE|SECTION)\s+\d+', line, re.IGNORECASE):
                    is_heading = True
                
                if is_heading:
                    # Save previous section
                    if current_section and current_section['content'].strip():
                        sections.append(current_section)
                        section_order += 1
                    
                    # Start new section
                    current_section = {
                        'order': section_order,
                        'heading': line,
                        'content': '',
                        'images': page_images.copy() if page_images else [],
                        'tables': [],
                        'page': page_num + 1
                    }
                elif current_section:
                    # Add content to current section
                    current_section['content'] += line + '\n'
                    
                    # Add images from this page to current section if not already added
                    for img in page_images:
                        if img not in current_section['images']:
                            current_section['images'].append(img)
        
        # Add last section
        if current_section and current_section['content'].strip():
            sections.append(current_section)
        
        doc.close()
        
        # Filter sections - keep only meaningful ones
        meaningful_sections = []
        for section in sections:
            # Skip very short sections or page numbers
            if len(section['content']) > 100:
                meaningful_sections.append(section)
        
        return {
            'success': True,
            'sections': meaningful_sections[:20],  # Limit to first 20 sections
            'total_sections': len(meaningful_sections)
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
            'error': 'Usage: python process_pdf.py <pdf_path> <output_dir>'
        }))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    result = process_pdf(pdf_path, output_dir)
    print(json.dumps(result, indent=2))
