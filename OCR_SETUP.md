# OCR-Based PDF Processing Setup

## Prerequisites

### Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Python Dependencies

```bash
source venv/bin/activate
pip install pytesseract Pillow
```

## Usage

### 1. Process PDF with OCR

```bash
python3 backend/services/process_pdf_ocr.py \
  "/path/to/your.pdf" \
  "./public/uploads/ocr-output"
```

### 2. Output

The script will:
- Convert each PDF page to a high-resolution image (300 DPI)
- Run Tesseract OCR on each page
- Extract images from each page
- Compare OCR text vs native PDF text
- Use the best text source (native or OCR)
- Save combined text to `ocr_text.txt`

### 3. Integration with LlamaParse

The OCR'd text can be sent to LlamaParse for better parsing:

```javascript
const fs = require('fs');
const ocrText = fs.readFileSync('./public/uploads/ocr-output/ocr_text.txt', 'utf-8');

// Send to LlamaParse
// ... LlamaParse processing
```

## When to Use OCR

**Use OCR when:**
- PDF is scanned (images of pages)
- Text is embedded as images
- Native text extraction gives poor results
- PDF has complex layouts

**Skip OCR when:**
- PDF has good native text
- Processing speed is critical
- Text quality is already high

## Performance

- **OCR Speed**: ~2-5 seconds per page
- **Accuracy**: 95-99% for clear text
- **DPI**: 300 recommended (higher = slower but more accurate)

## Troubleshooting

### Tesseract not found

```bash
# Check if installed
tesseract --version

# macOS: Add to PATH
export PATH="/usr/local/bin:$PATH"
```

### Poor OCR quality

- Increase DPI (edit `dpi=300` to `dpi=600`)
- Ensure PDF pages are clear and high-resolution
- Try different Tesseract language packs

### Memory issues

- Process pages in batches
- Reduce DPI
- Use smaller PDF files

## Example Output

```json
{
  "success": true,
  "pages": [
    {
      "page_num": 1,
      "ocr_text": "Extracted via OCR...",
      "pymupdf_text": "Native PDF text...",
      "best_text": "Native PDF text...",
      "images": [
        {
          "filename": "page_1_img_1.png",
          "path": "./public/uploads/ocr-output/page_1_img_1.png",
          "size": 12345
        }
      ],
      "has_native_text": true,
      "text_source": "pymupdf"
    }
  ],
  "total_pages": 10,
  "ocr_enabled": true,
  "combined_text_path": "./public/uploads/ocr-output/ocr_text.txt",
  "combined_text_length": 50000
}
```

## Advanced Configuration

### Custom Tesseract Config

Edit `process_pdf_ocr.py`:

```python
# Add custom config
custom_config = r'--oem 3 --psm 6'
text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
```

### Multi-language OCR

```python
# Install language packs first
# brew install tesseract-lang

text = pytesseract.image_to_string(image, lang='eng+fra+deu')
```

### Preprocessing for Better OCR

```python
from PIL import ImageEnhance, ImageFilter

# Enhance contrast
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(2.0)

# Sharpen
image = image.filter(ImageFilter.SHARPEN)

# Then run OCR
text = pytesseract.image_to_string(image)
```
