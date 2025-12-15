#!/usr/bin/env python3
"""
OCR-based PDF processing with LlamaParse integration
Converts each page to image, runs OCR, extracts images, then uses LlamaParse
"""

import sys
import json
import os
import fitz  # PyMuPDF
from PIL import Image
import io
import base64

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    print("Warning: pytesseract not installed. OCR will be skipped.", file=sys.stderr)

def pdf_page_to_image(page, dpi=300):
    """Convert PDF page to PIL Image for OCR"""
    try:
        # Render page to pixmap at high DPI for better OCR
        mat = fitz.Matrix(dpi/72, dpi/72)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        
        return img
    except Exception as e:
        print(f"Error converting page to image: {e}", file=sys.stderr)
        return None

def ocr_image(image):
    """Run OCR on image using Tesseract"""
    if not HAS_TESSERACT:
        return ""
    
    try:
        # Run Tesseract OCR
        text = pytesseract.image_to_string(image, lang='eng')
        return text
    except Exception as e:
        print(f"OCR error: {e}", file=sys.stderr)
        return ""

def extract_images_from_page(page, page_num, output_dir):
    """Extract images from PDF page"""
    images = []
    
    try:
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Save image
                image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                images.append({
                    'filename': image_filename,
                    'path': image_path,
                    'size': len(image_bytes)
                })
                
            except Exception as e:
                print(f"Error extracting image {img_index} from page {page_num + 1}: {e}", file=sys.stderr)
        
        return images
    except Exception as e:
        print(f"Error extracting images from page {page_num + 1}: {e}", file=sys.stderr)
        return []

def process_pdf_with_ocr(pdf_path, output_dir):
    """
    Process PDF with OCR for each page
    
    Returns:
    {
        'pages': [
            {
                'page_num': 1,
                'ocr_text': 'extracted text',
                'pymupdf_text': 'native text',
                'images': [...],
                'has_text': bool
            }
        ]
    }
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Open PDF
        doc = fitz.open(pdf_path)
        pages_data = []
        
        print(f"Processing {len(doc)} pages with OCR...", file=sys.stderr)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            print(f"\n[{page_num + 1}/{len(doc)}] Processing page {page_num + 1}...", file=sys.stderr)
            
            # Extract native text (PyMuPDF)
            native_text = page.get_text()
            has_native_text = len(native_text.strip()) > 50
            
            # Convert page to image for OCR
            ocr_text = ""
            if HAS_TESSERACT:
                print(f"  Running OCR...", file=sys.stderr)
                page_image = pdf_page_to_image(page)
                if page_image:
                    ocr_text = ocr_image(page_image)
                    print(f"  OCR extracted {len(ocr_text)} characters", file=sys.stderr)
            
            # Extract images from page
            print(f"  Extracting images...", file=sys.stderr)
            images = extract_images_from_page(page, page_num, output_dir)
            print(f"  Found {len(images)} images", file=sys.stderr)
            
            # Determine best text source
            # If native text is good, use it; otherwise use OCR
            best_text = native_text if has_native_text else ocr_text
            
            pages_data.append({
                'page_num': page_num + 1,
                'ocr_text': ocr_text,
                'pymupdf_text': native_text,
                'best_text': best_text,
                'images': images,
                'has_native_text': has_native_text,
                'text_source': 'pymupdf' if has_native_text else 'ocr'
            })
        
        doc.close()
        
        return {
            'success': True,
            'pages': pages_data,
            'total_pages': len(pages_data),
            'ocr_enabled': HAS_TESSERACT
        }
        
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

def prepare_for_llamaparse(pages_data):
    """
    Prepare OCR'd text for LlamaParse
    Combines all page text into a single document
    """
    combined_text = ""
    
    for page in pages_data:
        combined_text += f"\n\n=== PAGE {page['page_num']} ===\n\n"
        combined_text += page['best_text']
    
    return combined_text

if __name__ == '__main__':
    if len(sys.argv) < 3:
        result = {
            'success': False,
            'error': 'Usage: python process_pdf_ocr.py <pdf_path> <output_dir>'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Process PDF with OCR
    result = process_pdf_with_ocr(pdf_path, output_dir)
    
    if result['success']:
        # Prepare text for LlamaParse
        combined_text = prepare_for_llamaparse(result['pages'])
        
        # Save combined text
        text_output_path = os.path.join(output_dir, 'ocr_text.txt')
        with open(text_output_path, 'w', encoding='utf-8') as f:
            f.write(combined_text)
        
        result['combined_text_path'] = text_output_path
        result['combined_text_length'] = len(combined_text)
    
    # Output JSON result
    print(json.dumps(result, indent=2))
