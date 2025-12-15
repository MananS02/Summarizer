# 📚 PDF Learning Platform with AI

An intelligent PDF learning platform that uses **GPT-4** for heading detection and **GPT-4 Vision** for image classification to create structured, searchable educational content from PDF documents.

## ✨ Features

### 🤖 AI-Powered Processing
- **LLM-Based Heading Detection**: Uses GPT-4 to intelligently identify section headings and hierarchy
- **Smart Image Classification**: GPT-4 Vision analyzes and classifies images as important or decorative
- **AI-Generated Summaries**: Automatic 10-12 sentence summaries for each section
- **Rich Metadata**: AI-generated descriptions, tags, and relevance scores for images

### 📖 Content Extraction
- **Accurate Sectioning**: Matches PDF structure exactly using LLM analysis
- **Table Extraction**: Captures tables with metadata (rows, columns)
- **Image Filtering**: Keeps only educational diagrams, charts, and illustrations
- **Paragraph Formation**: Combines text into proper paragraphs

### 🎨 Modern UI
- Beautiful gradient header with grid pattern
- Card-based layouts with hover effects
- Responsive design for all screen sizes
- AI metadata display (image types, relevance scores, tags)
- Smooth animations and transitions

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Node.js + Express.js
- MongoDB + Mongoose
- Python 3.14 (PDF processing)

**AI Services:**
- Azure OpenAI GPT-4 (heading detection, summaries)
- Azure OpenAI GPT-4 Vision (image classification)

**PDF Processing:**
- PyMuPDF (fitz) - text, image, table extraction

**Frontend:**
- HTML5, CSS3, Vanilla JavaScript
- Modern design with CSS custom properties
- No frameworks - lightweight and fast

### Processing Pipeline

```
PDF → PyMuPDF → GPT-4 (Headings) → GPT-4 Vision (Images) → MongoDB → UI
```

1. **Extract Text**: PyMuPDF extracts all text from PDF
2. **Identify Headings**: GPT-4 analyzes text to find proper headings and hierarchy
3. **Extract Content**: For each section, extract text, images, and tables
4. **Classify Images**: GPT-4 Vision determines if images are important or decorative
5. **Store Data**: Save sections with blocks (text, images, tables) to MongoDB
6. **Generate Summaries**: GPT-4 creates comprehensive summaries
7. **Display**: Modern UI shows sections with AI-enhanced content

## 🚀 Quick Start

### Prerequisites

- Node.js (v18+)
- Python 3.14
- MongoDB
- Azure OpenAI API access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/MananS02/Summarizer.git
cd Summarizer
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pymupdf openai python-dotenv
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
MONGODB_URI=your_mongodb_connection_string
AZURE_OPENAI_GPT_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_GPT_KEY=your_api_key
AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4
AZURE_OPENAI_GPT_VERSION=2024-02-15-preview
PORT=3000
```

### Usage

1. **Process a PDF with LLM-based heading detection**
```bash
node backend/insertLLMData.js
```

This will:
- Use GPT-4 to identify proper headings
- Extract content for each section
- Classify images with GPT-4 Vision
- Extract tables with metadata
- Save to MongoDB

2. **Generate AI summaries**
```bash
node backend/regenerateSummariesFast.js
```

3. **Start the server**
```bash
npm start
```

4. **Open browser**
```
http://localhost:3000
```

## 📊 Statistics from Sample PDF

**Processing Results:**
- Total images found: 41
- AI-classified as important: 34 (83%)
- AI-classified as decorative: 7 (17%)
- Tables extracted: 39
- Sections created: 8
- Total blocks: 95

**Cost per PDF:**
- Heading detection: ~$0.75
- Image classification: ~$0.45
- Summaries: ~$0.10
- **Total: ~$1.30 per PDF**

## 🎯 Key Features Explained

### LLM-Based Heading Detection

Instead of using regex patterns, we use GPT-4 to:
- Analyze the full document text
- Identify true section headings
- Determine heading hierarchy (Level 1, 2, etc.)
- Provide context for each heading

**Benefits:**
- ✅ Accurate section structure matching PDF
- ✅ Handles various heading formats
- ✅ Understands document context
- ✅ No manual pattern configuration

### AI Image Classification

GPT-4 Vision analyzes each image to determine:
- **Is it important?** (diagram, chart, screenshot vs icon, logo)
- **What type?** (Venn diagram, bar chart, flowchart, etc.)
- **What does it show?** (AI-generated description)
- **How relevant?** (0-10 relevance score)
- **What topics?** (keyword tags)

**Classification Rules:**
- Diagrams, charts, Venn diagrams → IMPORTANT
- Images with text labels → IMPORTANT
- Small icons (< 50px) with no text → decorative
- When in doubt → IMPORTANT (inclusive approach)

## 📁 Project Structure

```
pdf-learning-platform/
├── backend/
│   ├── models/           # MongoDB schemas
│   ├── routes/           # Express API routes
│   ├── services/         # PDF processing scripts
│   │   ├── identify_headings_llm.py      # GPT-4 heading detection
│   │   ├── classify_image_enhanced.py    # GPT-4 Vision classifier
│   │   ├── process_pdf_llm.py            # Main PDF processor
│   │   └── summarizer.js                 # AI summary generator
│   ├── insertLLMData.js  # Process PDF with LLM
│   ├── regenerateSummariesFast.js        # Generate summaries
│   └── server.js         # Express server
├── public/
│   ├── index.html        # Main page (section list)
│   ├── topic.html        # Topic detail page
│   └── styles.css        # Modern UI styles
├── package.json
└── README.md
```

## 🔧 Configuration

### PDF Processing Options

Edit `backend/insertLLMData.js` to configure:
- PDF file path
- Output directory
- Azure OpenAI credentials

### Image Classification Tuning

Edit `backend/services/classify_image_enhanced.py` to adjust:
- Classification criteria
- Image type categories
- Relevance scoring

### Summary Generation

Edit `backend/services/summarizer.js` to customize:
- Summary length (currently 10-12 sentences)
- Temperature (creativity level)
- Max tokens (currently 500)

## 🎨 UI Customization

The UI uses CSS custom properties for easy theming. Edit `public/styles.css`:

```css
:root {
  --primary: #6366f1;        /* Primary color */
  --primary-dark: #4f46e5;   /* Hover color */
  --text-primary: #111827;   /* Main text */
  --bg-primary: #ffffff;     /* Background */
  /* ... more variables */
}
```

## 📝 API Endpoints

- `GET /api/documents/:slug` - Get document with all sections
- `GET /api/sections/:docSlug/:sectionSlug` - Get specific section with navigation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - feel free to use this project for your own purposes.

## 🙏 Acknowledgments

- Azure OpenAI for GPT-4 and GPT-4 Vision APIs
- PyMuPDF for excellent PDF processing capabilities
- MongoDB for flexible document storage

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using AI-powered document processing**
