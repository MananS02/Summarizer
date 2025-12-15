# Image Meta-Tagging System Architecture

## 🎯 Complete Workflow

```
PDF Processing → Heading Detection → Image Extraction → AI Meta-Tagging → MongoDB Storage → Accurate Retrieval
```

## 📊 Detailed Flow

### 1. **Heading-Wise Extraction**

```python
# For each section heading (e.g., "IT Services Sub Sector")
for heading_info in headings_result:
    heading = "IT Services Sub Sector"  # Current section
    
    # Extract images from pages in this section
    for page_num in range(start_page, end_page + 1):
        images = page.get_images()
```

### 2. **AI Meta-Tagging with Context**

```python
# Pass image + heading context to GPT-4 Vision
classification = classify_and_describe_image(
    image_bytes,
    image_ext,
    azure_endpoint,
    azure_key,
    deployment,
    context=heading  # ← Heading provides context!
)
```

**GPT-4 Vision receives:**
- Image bytes
- Section heading: "IT Services Sub Sector"
- Prompt: "This image appears in a section about: IT Services Sub Sector"

**GPT-4 Vision returns:**
```json
{
  "is_important": true,
  "image_type": "Venn diagram",
  "description": "A Venn diagram showing three overlapping circles: User Organizations, IT Services Organizations, and Consulting Organizations, illustrating the relationships in the Information/Cyber Security sector",
  "relevance_score": 9,
  "tags": ["cyber security", "organizations", "IT services", "consulting"]
}
```

### 3. **MongoDB Storage Structure**

```javascript
{
  "_id": ObjectId("..."),
  "documentSlug": "test-sample",
  "sectionSlug": "it-services-sub-sector-1",
  "heading": "IT Services Sub Sector",
  "blocks": [
    {
      "type": "text",
      "content": "The IT services sector comprises...",
      "order": 0
    },
    {
      "type": "image",
      "content": "page_12_img_1.jpeg",  // Filename
      "order": 1,
      "metadata": {
        "ai_classified": true,
        "image_type": "Venn diagram",
        "description": "A Venn diagram showing three overlapping circles...",
        "relevance_score": 9,
        "tags": ["cyber security", "organizations", "IT services", "consulting"],
        "section_context": "IT Services Sub Sector"  // ← Heading context stored!
      }
    },
    {
      "type": "table",
      "content": "page_12_table_1.png",
      "order": 2,
      "metadata": {
        "is_table": true,
        "rows": 5,
        "cols": 3
      }
    }
  ]
}
```

### 4. **Accurate Retrieval**

When retrieving images, you can:

**A. Search by tags:**
```javascript
db.sections.find({
  "blocks.metadata.tags": "cyber security"
})
```

**B. Filter by image type:**
```javascript
db.sections.find({
  "blocks.metadata.image_type": "Venn diagram"
})
```

**C. Filter by relevance:**
```javascript
db.sections.find({
  "blocks.metadata.relevance_score": { $gte: 8 }
})
```

**D. Search by description:**
```javascript
db.sections.find({
  "blocks.metadata.description": { $regex: "organizations", $options: "i" }
})
```

## 🎨 Enhanced Metadata Schema

### Current Metadata (Already Implemented)
```json
{
  "ai_classified": true,
  "image_type": "Venn diagram",
  "description": "Detailed AI-generated description",
  "relevance_score": 9,
  "tags": ["keyword1", "keyword2", "keyword3"]
}
```

### Enhanced Metadata (Proposed)
```json
{
  "ai_classified": true,
  "image_type": "Venn diagram",
  "description": "Detailed AI-generated description",
  "relevance_score": 9,
  "tags": ["keyword1", "keyword2", "keyword3"],
  
  // NEW: Additional context
  "section_heading": "IT Services Sub Sector",
  "section_order": 7,
  "page_number": 12,
  
  // NEW: Visual characteristics
  "has_text_labels": true,
  "color_scheme": "multi-color",
  "complexity": "medium",
  
  // NEW: Relationships
  "shows_relationships": true,
  "relationship_type": "overlap",
  "entities": ["User Organizations", "IT Services Organizations", "Consulting Organizations"],
  
  // NEW: Educational value
  "learning_objective": "Understanding organizational types in cyber security",
  "difficulty_level": "intermediate",
  
  // NEW: Usage tracking
  "created_at": "2025-12-15T18:00:00Z",
  "ai_model": "gpt-4-vision",
  "confidence": 0.95
}
```

## 🔍 Retrieval Examples

### Example 1: Find all diagrams about cyber security
```javascript
db.sections.aggregate([
  { $unwind: "$blocks" },
  { $match: {
    "blocks.type": "image",
    "blocks.metadata.tags": "cyber security",
    "blocks.metadata.image_type": { $regex: "diagram" }
  }},
  { $project: {
    heading: 1,
    image: "$blocks.content",
    description: "$blocks.metadata.description",
    relevance: "$blocks.metadata.relevance_score"
  }}
])
```

### Example 2: Find high-quality educational images
```javascript
db.sections.find({
  "blocks.metadata.relevance_score": { $gte: 8 },
  "blocks.metadata.ai_classified": true
}).sort({ "blocks.metadata.relevance_score": -1 })
```

### Example 3: Find images showing relationships
```javascript
db.sections.find({
  "blocks.metadata.shows_relationships": true,
  "blocks.metadata.relationship_type": "overlap"
})
```

## 📈 Benefits of This Approach

### 1. **Context-Aware Classification**
- Images are classified with knowledge of their section
- More accurate descriptions and tags
- Better relevance scoring

### 2. **Rich Metadata**
- Multiple search dimensions (type, tags, relevance, description)
- Structured data for filtering and sorting
- Educational context preserved

### 3. **Accurate Retrieval**
- Find images by semantic meaning, not just filename
- Filter by quality (relevance score)
- Search by visual characteristics

### 4. **Scalability**
- MongoDB indexes on metadata fields
- Fast queries even with thousands of images
- Flexible schema for future enhancements

## 🚀 Usage in Application

### Frontend Display
```javascript
// Fetch section with images
const section = await fetch(`/api/sections/test-sample/${sectionSlug}`);

// Display images with AI metadata
section.blocks.forEach(block => {
  if (block.type === 'image') {
    console.log(`Type: ${block.metadata.image_type}`);
    console.log(`Description: ${block.metadata.description}`);
    console.log(`Tags: ${block.metadata.tags.join(', ')}`);
    console.log(`Relevance: ${block.metadata.relevance_score}/10`);
  }
});
```

### Search API
```javascript
// Search for images by tag
app.get('/api/images/search', async (req, res) => {
  const { tag, type, minRelevance } = req.query;
  
  const results = await Section.aggregate([
    { $unwind: '$blocks' },
    { $match: {
      'blocks.type': 'image',
      'blocks.metadata.tags': tag,
      'blocks.metadata.image_type': type,
      'blocks.metadata.relevance_score': { $gte: parseInt(minRelevance) }
    }}
  ]);
  
  res.json(results);
});
```

## ✅ Current Status

**Already Implemented:**
- ✅ Heading-wise image extraction
- ✅ GPT-4 Vision meta-tagging with context
- ✅ Rich metadata storage in MongoDB
- ✅ Accurate retrieval via metadata

**Ready to Use:**
- ✅ Process PDF: `node backend/insertLLMData.js`
- ✅ View metadata in UI
- ✅ Search by tags, type, relevance

**Future Enhancements:**
- 🔄 Add search API endpoint
- 🔄 Implement image gallery view
- 🔄 Add metadata-based filtering in UI
- 🔄 Track usage analytics
