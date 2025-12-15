#!/usr/bin/env python3
"""
Identify headings and section structure using GPT-4
Replaces regex-based heading detection with intelligent LLM analysis
"""

import sys
import json
import os
import fitz  # PyMuPDF
from openai import AzureOpenAI

def extract_pdf_text(pdf_path, max_pages=None):
    """Extract text from PDF, page by page"""
    try:
        doc = fitz.open(pdf_path)
        pages_text = []
        
        num_pages = min(len(doc), max_pages) if max_pages else len(doc)
        
        for page_num in range(num_pages):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                pages_text.append({
                    'page': page_num + 1,
                    'text': text
                })
        
        doc.close()
        return pages_text
        
    except Exception as e:
        print(f"Error extracting PDF text: {e}", file=sys.stderr)
        return []

def identify_headings_with_llm(pages_text, azure_endpoint, azure_key, deployment):
    """
    Use GPT-4 to identify headings and section structure
    
    Returns:
    [
        {
            "heading": "3. Various sub-sectors within the IT-BPM industry",
            "level": 1,
            "start_page": 5,
            "context": "first 150 chars of content..."
        }
    ]
    """
    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=azure_key,
            api_version="2024-02-15-preview",
            azure_endpoint=azure_endpoint
        )
        
        # Combine text from all pages
        full_text = ""
        for page_data in pages_text:
            full_text += f"\n\n=== PAGE {page_data['page']} ===\n\n"
            full_text += page_data['text']
        
        # Create prompt for GPT-4
        prompt = f"""Analyze this PDF document and identify ALL section headings with their hierarchy.

TASK:
1. Find all true section headings (main topics/chapters)
2. Determine heading hierarchy:
   - Level 1: Major sections/chapters (e.g., "3. Various sub-sectors within the IT-BPM industry")
   - Level 2: Subsections within a major section (e.g., "Key Sub-sectors and Growth")
3. Identify the page number where each heading appears
4. Extract first 150 characters of content after the heading for context

RULES FOR IDENTIFYING HEADINGS:
✓ Include: Section titles, chapter headings, major topic headings
✓ Include: Numbered sections (e.g., "1. Introduction", "2.1 Overview")
✓ Include: Important subsection headings
✗ Skip: Page numbers, headers, footers
✗ Skip: "Table of Contents", "Key Learning Outcomes", metadata
✗ Skip: Figure captions, table titles
✗ Skip: Regular paragraph text

HEADING CHARACTERISTICS:
- Usually at the start of a new topic/section
- Often numbered or in title case
- Followed by explanatory content
- Structurally distinct from body text

PDF DOCUMENT TEXT:
{full_text[:15000]}

Return ONLY a valid JSON array (no markdown, no explanation):
[
  {{
    "heading": "exact heading text as it appears",
    "level": 1,
    "start_page": 5,
    "context": "first 150 chars of content after heading"
  }}
]

Be thorough - include ALL meaningful section headings."""

        print("Sending PDF text to GPT-4 for heading analysis...", file=sys.stderr)
        
        # Call GPT-4
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing document structure and identifying section headings. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=2000,
            temperature=0.1  # Low temperature for consistent results
        )
        
        # Get response
        result_text = response.choices[0].message.content.strip()
        
        print(f"GPT-4 response received ({len(result_text)} chars)", file=sys.stderr)
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            result_text = result_text.strip()
            
            headings = json.loads(result_text)
            
            print(f"✓ Identified {len(headings)} headings", file=sys.stderr)
            
            # Validate structure
            if not isinstance(headings, list):
                raise ValueError("Response is not a list")
            
            for i, h in enumerate(headings):
                if not all(k in h for k in ['heading', 'level', 'start_page']):
                    print(f"Warning: Heading {i} missing required fields", file=sys.stderr)
            
            return headings
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            print(f"Response was: {result_text[:500]}", file=sys.stderr)
            return []
        
    except Exception as e:
        print(f"Error calling GPT-4: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []

def main():
    if len(sys.argv) < 5:
        result = {
            'success': False,
            'error': 'Usage: python identify_headings_llm.py <pdf_path> <azure_endpoint> <azure_key> <deployment> [max_pages]'
        }
        print(json.dumps(result))
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    azure_endpoint = sys.argv[2]
    azure_key = sys.argv[3]
    deployment = sys.argv[4]
    max_pages = int(sys.argv[5]) if len(sys.argv) > 5 else None
    
    try:
        # Extract text from PDF
        print(f"Extracting text from PDF...", file=sys.stderr)
        pages_text = extract_pdf_text(pdf_path, max_pages)
        
        if not pages_text:
            result = {
                'success': False,
                'error': 'No text extracted from PDF'
            }
            print(json.dumps(result))
            sys.exit(1)
        
        print(f"✓ Extracted text from {len(pages_text)} pages", file=sys.stderr)
        
        # Identify headings with GPT-4
        headings = identify_headings_with_llm(
            pages_text,
            azure_endpoint,
            azure_key,
            deployment
        )
        
        if not headings:
            result = {
                'success': False,
                'error': 'No headings identified'
            }
            print(json.dumps(result))
            sys.exit(1)
        
        # Return results
        result = {
            'success': True,
            'headings': headings,
            'total_headings': len(headings),
            'pages_analyzed': len(pages_text)
        }
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(result))
        sys.exit(1)

if __name__ == '__main__':
    main()
