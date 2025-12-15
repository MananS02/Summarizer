# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
cd pdf-learning-platform
npm install
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
MONGODB_URI=mongodb://localhost:27017/pdf-learning-platform
LLAMAPARSE_API_KEY=llx-xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
PORT=3000
```

### Step 3: Start MongoDB
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Or use MongoDB Atlas (cloud) - just update MONGODB_URI
```

### Step 4: Start the Server
```bash
npm start
```

### Step 5: Open Browser
Navigate to: **http://localhost:3000**

---

## 📋 What You Need

### Required API Keys

1. **LlamaParser API Key**
   - Sign up: https://cloud.llamaindex.ai/
   - Go to API Keys section
   - Create new key
   - Copy to `.env` file

2. **OpenAI API Key**
   - Sign up: https://platform.openai.com/
   - Go to API Keys
   - Create new secret key
   - Copy to `.env` file
   - Ensure you have credits ($5+ recommended)

### MongoDB Options

**Option A: Local MongoDB**
- Download: https://www.mongodb.com/try/download/community
- Install and start service
- Use: `mongodb://localhost:27017/pdf-learning-platform`

**Option B: MongoDB Atlas (Cloud)**
- Sign up: https://www.mongodb.com/cloud/atlas
- Create free cluster
- Get connection string
- Use: `mongodb+srv://username:password@cluster.mongodb.net/pdf-learning-platform`

---

## 🎯 First Upload

1. Open http://localhost:3000
2. Click "Choose PDF File"
3. Select a PDF (try a simple one first, 5-10 pages)
4. Click "Upload & Process"
5. Wait 30-60 seconds
6. You'll be redirected to the document page
7. Click any section to view full content

---

## ⚡ Tips

- **First upload**: Use a small PDF to test
- **Processing time**: Depends on PDF size and API response times
- **Costs**: OpenAI charges ~$0.001-0.01 per section
- **Sections**: Based on heading detection (# and ## in markdown)

---

## 🔧 Troubleshooting

**Can't connect to MongoDB?**
```bash
# Check if MongoDB is running
brew services list  # macOS
sudo systemctl status mongod  # Linux
```

**API key errors?**
- Double-check keys in `.env`
- Ensure no extra spaces
- Restart server after changing `.env`

**Upload fails?**
- Check server logs in terminal
- Verify API keys are valid
- Try a smaller PDF first

---

## 📁 Project Structure

```
pdf-learning-platform/
├── backend/           # Node.js + Express server
├── public/            # Frontend HTML/CSS/JS
├── package.json       # Dependencies
├── .env              # Your API keys (create this)
└── README.md         # Full documentation
```

---

**Need help?** Check the full README.md for detailed documentation.
