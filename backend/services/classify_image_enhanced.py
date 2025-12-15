#!/usr/bin/env python3
"""
Enhanced image classification using Azure OpenAI GPT-4 Vision
Returns detailed metadata: classification, type, description, relevance, tags
"""

import sys
import json
import base64
import os
from openai import AzureOpenAI

def encode_image_base64(image_bytes):
    """Encode image bytes to base64"""
    return base64.b64encode(image_bytes).decode('utf-8')

def classify_and_describe_image(image_bytes, image_format, azure_endpoint, azure_key, deployment, context=""):
    """
    Use GPT-4 Vision to classify and describe an image
    
    Args:
        image_bytes: Raw image bytes
        image_format: Image format (jpeg, png, etc.)
        azure_endpoint: Azure OpenAI endpoint
        azure_key: Azure OpenAI API key
        deployment: Deployment name
        context: Optional context (section heading) for better classification
    
    Returns:
        {
            "is_important": bool,
            "image_type": str,
            "description": str,
            "relevance_score": int (0-10),
            "tags": list[str]
        }
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
        
        # Create comprehensive document analysis prompt
        prompt = f"""You are a document analysis model analyzing an image from an educational/training PDF.

CONTEXT: This image appears in a section about: "{context}"

## CRITICAL INSTRUCTIONS

- **NEVER treat diagrams, charts, Venn diagrams, or other graphics as decorative.**
- Assume every non-blank graphic may contain important information (labels, relationships, counts, categories, overlaps, flows, hierarchies).
- When in doubt, **treat the visual as IMPORTANT** and describe it.

## WHAT TO ANALYZE

For this image, determine:

1. **Is it IMPORTANT for learning?**
   - YES if it contains: diagrams, charts, Venn diagrams, flowcharts, network diagrams, organizational charts, process flows, tables, screenshots, infographics, technical illustrations, maps, schematics
   - YES if it has: text labels, annotations, callouts, legends, axis labels, numeric values
   - YES if it shows: relationships, hierarchies, groupings, flows, overlaps, connections
   - NO only if: purely decorative (small icon < 50px, border, pattern) with NO text and NO structural meaning

2. **What type is it?**
   - Examples: "Venn diagram", "bar chart", "line chart", "pie chart", "network diagram", "process flow", "organizational chart", "matrix diagram", "table", "screenshot", "infographic", "technical illustration"

3. **What does it show?**
   - Extract ALL visible text (labels, titles, captions, values)
   - Describe relationships (what overlaps, what connects, what groups together)
   - Explain the structure (hierarchy, flow, categories)

## CLASSIFICATION RULES

IMPORTANT (keep these):
- Diagrams: flowcharts, Venn diagrams, network diagrams, system diagrams, ER diagrams
- Charts: bar charts, pie charts, line graphs, scatter plots, area charts
- Organizational: org charts, hierarchy diagrams, structure diagrams
- Process: workflows, process flows, swimlane diagrams, sequence diagrams
- Technical: schematics, architecture diagrams, circuit diagrams
- Data: tables, matrices, comparison charts
- Educational: concept maps, mind maps, labeled illustrations
- Screenshots: software interfaces, applications, tools
- Infographics: visual explanations with text and graphics
- ANY graphic with text labels, annotations, or callouts

DECORATIVE (skip only these):
- Small icons/logos (< 50x50 pixels) with NO text
- Pure decorative borders with NO content
- Background patterns with NO meaning
- Blank or empty shapes with NO labels

## OUTPUT FORMAT

Return ONLY valid JSON:
{{
  "is_important": true or false,
  "image_type": "specific type (e.g., 'Venn diagram', 'bar chart', 'process flow')",
  "description": "Detailed description including: what type of diagram, what text/labels are visible, what relationships or structure it shows",
  "relevance_score": 1-10,
  "tags": ["keyword1", "keyword2", "keyword3"]
}}

**BE INCLUSIVE**: If an image has ANY educational value, text labels, or shows relationships, mark it as IMPORTANT.
**DEFAULT TO IMPORTANT**: When uncertain, classify as important (better to include than exclude)."""

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
                                "url": f"data:image/{image_format};base64,{base64_image}",
                                "detail": "low"  # Use low detail to reduce cost
                            }
                        }
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.3  # Lower temperature for more consistent results
        )
        
        # Get response
        result_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            
            # Validate and set defaults
            return {
                'is_important': result.get('is_important', False),
                'image_type': result.get('image_type', 'unknown'),
                'description': result.get('description', ''),
                'relevance_score': min(10, max(0, result.get('relevance_score', 5))),
                'tags': result.get('tags', [])[:5]  # Limit to 5 tags
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}", file=sys.stderr)
            print(f"Response was: {result_text}", file=sys.stderr)
            # Return safe defaults
            return {
                'is_important': True,  # Default to keeping if parsing fails
                'image_type': 'unknown',
                'description': 'Image classification failed',
                'relevance_score': 5,
                'tags': []
            }
        
    except Exception as e:
        print(f"Error classifying image: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # Return safe defaults on error
        return {
            'is_important': True,  # Default to keeping on error
            'image_type': 'unknown',
            'description': 'Classification error',
            'relevance_score': 5,
            'tags': []
        }

if __name__ == '__main__':
    # Test with a sample image
    if len(sys.argv) < 5:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python classify_image_enhanced.py <image_path> <azure_endpoint> <azure_key> <deployment> [context]'
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    azure_endpoint = sys.argv[2]
    azure_key = sys.argv[3]
    deployment = sys.argv[4]
    context = sys.argv[5] if len(sys.argv) > 5 else ""
    
    # Read image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Get format from extension
    image_format = os.path.splitext(image_path)[1][1:]  # Remove dot
    
    # Classify
    result = classify_and_describe_image(
        image_bytes, 
        image_format, 
        azure_endpoint, 
        azure_key, 
        deployment,
        context
    )
    
    output = {
        'success': True,
        'image_path': image_path,
        'context': context,
        'classification': result
    }
    
    print(json.dumps(output, indent=2))
