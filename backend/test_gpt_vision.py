#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI GPT-4 Vision is working
Tests with a sample image from the PDF uploads
"""

import sys
import os

# Add parent directory to path to import classify_image_enhanced
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

from classify_image_enhanced import classify_and_describe_image
import json

def test_gpt_vision():
    """Test GPT-4 Vision with a sample image"""
    
    print("=" * 60)
    print("GPT-4 Vision Test")
    print("=" * 60)
    
    # Configuration from environment
    import dotenv
    dotenv.load_dotenv()
    
    azure_endpoint = os.getenv('AZURE_OPENAI_GPT_ENDPOINT')
    azure_key = os.getenv('AZURE_OPENAI_GPT_KEY')
    deployment = os.getenv('AZURE_OPENAI_GPT_DEPLOYMENT')
    
    # Check configuration
    print("\n1. Checking Azure OpenAI Configuration...")
    if not azure_endpoint:
        print("   ❌ AZURE_OPENAI_GPT_ENDPOINT not set")
        return False
    if not azure_key:
        print("   ❌ AZURE_OPENAI_GPT_KEY not set")
        return False
    if not deployment:
        print("   ❌ AZURE_OPENAI_GPT_DEPLOYMENT not set")
        return False
    
    print(f"   ✓ Endpoint: {azure_endpoint}")
    print(f"   ✓ Deployment: {deployment}")
    print(f"   ✓ API Key: {'*' * 20}{azure_key[-4:]}")
    
    # Find a test image
    print("\n2. Finding test image...")
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'public', 'uploads', 'test-sample')
    
    if not os.path.exists(uploads_dir):
        print(f"   ❌ Uploads directory not found: {uploads_dir}")
        return False
    
    # Find first JPEG or PNG image
    test_image = None
    for filename in os.listdir(uploads_dir):
        if filename.endswith(('.jpeg', '.jpg', '.png')):
            test_image = os.path.join(uploads_dir, filename)
            break
    
    if not test_image:
        print(f"   ❌ No test images found in {uploads_dir}")
        return False
    
    print(f"   ✓ Using test image: {os.path.basename(test_image)}")
    
    # Read image
    print("\n3. Reading image file...")
    try:
        with open(test_image, 'rb') as f:
            image_bytes = f.read()
        
        image_size_kb = len(image_bytes) / 1024
        print(f"   ✓ Image size: {image_size_kb:.1f} KB")
        
        # Get format
        image_format = os.path.splitext(test_image)[1][1:]
        print(f"   ✓ Image format: {image_format}")
        
    except Exception as e:
        print(f"   ❌ Error reading image: {e}")
        return False
    
    # Test GPT-4 Vision classification
    print("\n4. Testing GPT-4 Vision API...")
    print("   (This may take 5-10 seconds...)")
    
    try:
        result = classify_and_describe_image(
            image_bytes,
            image_format,
            azure_endpoint,
            azure_key,
            deployment,
            context="Test image from PDF Learning Platform"
        )
        
        print("\n   ✓ API call successful!")
        
        # Display results
        print("\n5. Classification Results:")
        print("   " + "-" * 56)
        print(f"   Important:        {'✓ YES' if result['is_important'] else '✗ NO'}")
        print(f"   Image Type:       {result['image_type']}")
        print(f"   Relevance Score:  {result['relevance_score']}/10")
        print(f"   Description:      {result['description'][:80]}...")
        print(f"   Tags:             {', '.join(result['tags'])}")
        print("   " + "-" * 56)
        
        # Full JSON output
        print("\n6. Full JSON Response:")
        print(json.dumps(result, indent=2))
        
        print("\n" + "=" * 60)
        print("✅ GPT-4 Vision is working correctly!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ API call failed: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("❌ GPT-4 Vision test failed")
        print("=" * 60)
        
        return False

if __name__ == '__main__':
    success = test_gpt_vision()
    sys.exit(0 if success else 1)
