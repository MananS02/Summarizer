# PDF Learning Platform

A minimal learning platform that converts PDFs into structured sections with AI-generated summaries using LlamaParser and MongoDB.

## Features

- 📤 **PDF Upload**: Upload any PDF document
- 🤖 **AI-Powered Summaries**: Automatic headline and summary generation for each section
- 📊 **Smart Parsing**: Extract headings, text, tables, and images using LlamaParser
- 💾 **MongoDB Storage**: Simple document and section storage
- 🎨 **Clean UI**: Minimal, responsive interface with vanilla HTML/CSS
- 🔗 **Simple URLs**: `/docs/{documentSlug}` and `/docs/{documentSlug}/{sectionSlug}`

## Tech Stack

- **Backend**: Node.js + Express
- **Database**: MongoDB
- **PDF Parsing**: LlamaParser API
- **AI Summarization**: OpenAI GPT-3.5
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)

## Prerequisites

Before you begin, ensure you have:

1. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
2. **MongoDB** - Either:
   - Local installation - [Download](https://www.mongodb.com/try/download/community)
   - MongoDB Atlas account - [Sign up](https://www.mongodb.com/cloud/atlas)
3. **LlamaParser API Key** - [Get one here](https://cloud.llamaindex.ai/)
4. **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

## Installation

### 1. Clone or Download

If you received this as a folder, navigate to it:
```bash
cd pdf-learning-platform
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
MONGODB_URI=mongodb://localhost:27017/pdf-learning-platform
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
PORT=3000
```

**For MongoDB Atlas**, use this format:
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/pdf-learning-platform
```

### 4. Start MongoDB (if using local installation)

```bash
# macOS (if installed via Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
# MongoDB should start automatically as a service
```

### 5. Start the Server

```bash
npm start
```

You should see:
```
✓ MongoDB connected successfully
🚀 PDF Learning Platform running on http://localhost:3000
📚 Upload PDFs and start learning!
```

### 6. Open in Browser

Navigate to: **http://localhost:3000**

## Usage

### 1. Upload a PDF

- Click "Choose PDF File" on the home page
- Select a PDF document
- Click "Upload & Process"
- Wait for processing (this may take 30-60 seconds depending on PDF size)

### 2. Browse Documents

- View all uploaded documents on the home page
- Click on a document to see its sections

### 3. View Sections

- Click on any section to view:
  - AI-generated headline
  - AI-generated summary
  - Full content
  - Images and tables (if any)
- Navigate between sections using Previous/Next buttons

## Project Structure

```
pdf-learning-platform/
├── backend/
│   ├── server.js              # Main Express server
│   ├── config/
│   │   └── db.js              # MongoDB connection
│   ├── models/
│   │   ├── Document.js        # Document schema
│   │   └── Section.js         # Section schema
│   ├── routes/
│   │   ├── upload.js          # PDF upload & processing
│   │   ├── documents.js       # Document listing
│   │   └── sections.js        # Section retrieval
│   ├── services/
│   │   ├── parser.js          # LlamaParser integration
│   │   └── summarizer.js      # OpenAI summarization
│   └── uploads/               # Temporary PDF storage
├── public/
│   ├── uploads/               # Extracted images/tables
│   ├── index.html             # Home page
│   ├── document.html          # Document page
│   ├── section.html           # Section page
│   └── styles.css             # Minimal styling
├── package.json
├── .env.example
└── README.md
```

## API Endpoints

### Upload PDF
```
POST /api/upload
Content-Type: multipart/form-data
Body: { pdf: <file> }

Response:
{
  "success": true,
  "documentSlug": "my-document",
  "sectionCount": 5
}
```

### List Documents
```
GET /api/documents

Response:
[
  {
    "title": "My Document",
    "slug": "my-document",
    "uploadedAt": "2024-01-01T00:00:00.000Z",
    "sectionCount": 5
  }
]
```

### Get Document with Sections
```
GET /api/documents/:slug

Response:
{
  "document": { ... },
  "sections": [
    {
      "sectionSlug": "introduction",
      "order": 0,
      "heading": "Introduction",
      "headline": "Getting Started with the Platform",
      "summary": "This section introduces..."
    }
  ]
}
```

### Get Section Content
```
GET /api/sections/:docSlug/:sectionSlug

Response:
{
  "section": {
    "heading": "Introduction",
    "headline": "Getting Started",
    "summary": "This section...",
    "content": "Full text content...",
    "images": ["image1.png"],
    "tables": ["table1.png"]
  },
  "navigation": {
    "previous": { "slug": "...", "heading": "..." },
    "next": { "slug": "...", "heading": "..." }
  }
}
```

## How It Works

1. **Upload**: User uploads a PDF file
2. **Parse**: LlamaParser extracts headings, text, images, and tables
3. **Split**: Content is split into sections based on heading hierarchy
4. **Summarize**: OpenAI generates a headline (≤12 words) and summary (1-3 sentences) for each section
5. **Store**: Document and sections are saved to MongoDB
6. **Display**: User can browse documents and sections through the web interface

## Troubleshooting

### MongoDB Connection Error

**Error**: `MongoDB connection error`

**Solution**:
- Ensure MongoDB is running: `brew services list` (macOS) or `sudo systemctl status mongod` (Linux)
- Check your `MONGODB_URI` in `.env`
- For Atlas, ensure your IP is whitelisted

### LlamaParser API Error

**Error**: `Failed to parse PDF: 401 Unauthorized`

**Solution**:
- Verify your `LLAMAPARSE_API_KEY` in `.env`
- Check your API key at https://cloud.llamaindex.ai/

### OpenAI API Error

**Error**: `Summarization error: 401 Unauthorized`

**Solution**:
- Verify your `OPENAI_API_KEY` in `.env`
- Ensure you have credits in your OpenAI account

### Upload Timeout

**Error**: `Parsing timeout - job did not complete in time`

**Solution**:
- Try a smaller PDF file
- Increase timeout in `backend/services/parser.js` (line 45: `maxAttempts`)

## Customization

### Change LLM Provider

Edit `backend/services/summarizer.js` to use a different provider (Anthropic, local models, etc.)

### Adjust Summary Length

Modify the prompt in `backend/services/summarizer.js` (lines 16-24)

### Change Styling

Edit `public/styles.css` - all styles use CSS variables for easy theming

### Modify Section Detection

Edit `backend/services/parser.js` - the `extractSections` function uses regex to detect headings

## Limitations

- **No RAG**: This is a simple content viewer, not a Q&A system
- **No Vector DB**: Sections are retrieved by slug, not semantic search
- **Local Storage**: Images/tables stored on disk, not in cloud
- **Single User**: No authentication or multi-user support

## Future Enhancements

If you want to extend this platform:

- Add user authentication
- Implement full-text search
- Add vector embeddings for semantic search
- Support more file formats (DOCX, PPTX)
- Add section editing capabilities
- Implement collaborative features

## License

MIT

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the LlamaParser docs: https://docs.llamaindex.ai/
3. Review the OpenAI docs: https://platform.openai.com/docs/

---

**Built with ❤️ for simple, effective learning**
