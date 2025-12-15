#!/usr/bin/env python3
"""
Image classification using Azure OpenAI GPT-4 Vision
Determines if images are important for learning content
"""

import sys
import json
import base64
import os
from openai import AzureOpenAI

def encode_image_base64(image_bytes):
    """Encode image bytes to base64"""
    return base64.b64encode(image_bytes).decode('utf-8')

def classify_image(image_bytes, image_format, azure_endpoint, azure_key, deployment):
    """
    Use GPT-4 Vision to classify if image is important
    Returns: True if important, False if decorative
    """
    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=azure_key,
            api_version="2024-02-15-preview",
            azure_endpoint=azure_endpoint
        )
        
        # Encode image
        base64_image = encode_image_base64(image_bytes)
        
        # Create prompt
        prompt = """Analyze this image and determine if it's important for educational/learning content.

IMPORTANT images include:
- Diagrams, flowcharts, architecture diagrams
- Charts, graphs, data visualizations
- Screenshots showing processes or interfaces
- Illustrations explaining concepts
- Tables with data
- Technical drawings

SKIP these decorative images:
- Small icons, bullets, decorative elements
- Company logos, branding
- Page numbers, headers, footers
- Decorative borders or backgrounds
- Social media icons
- Generic stock photos

Respond with ONLY one word: "important" or "skip"
"""
        
        # Call GPT-4 Vision
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=10,
            temperature=0.1
        )
        
        # Get response
        result = response.choices[0].message.content.strip().lower()
        
        # Return True if important
        return "important" in result
        
    except Exception as e:
        print(f"Error classifying image: {e}", file=sys.stderr)
        # Default to including image if classification fails
        return True

if __name__ == '__main__':
    # Test with a sample image
    if len(sys.argv) < 5:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python classify_image.py <image_path> <azure_endpoint> <azure_key> <deployment>'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    azure_endpoint = sys.argv[2]
    azure_key = sys.argv[3]
    deployment = sys.argv[4]
    
    # Read image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Get format from extension
    image_format = os.path.splitext(image_path)[1][1:]  # Remove dot
    
    # Classify
    is_important = classify_image(image_bytes, image_format, azure_endpoint, azure_key, deployment)
    
    result = {
        'success': True,
        'image_path': image_path,
        'is_important': is_important,
        'decision': 'include' if is_important else 'skip'
    }
    
    print(json.dumps(result, indent=2))
