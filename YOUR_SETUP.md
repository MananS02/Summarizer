# Setup Instructions - Your Configuration

## ✅ What's Already Configured

1. **Azure OpenAI** - ✓ Configured
   - Endpoint: `customerprofile12.openai.azure.com`
   - Deployment: `gpt-4.1`
   - API Key: Configured in `.env`

2. **MongoDB Atlas** - ✓ Configured
   - Connection: `cluster0.yfuwlmd.mongodb.net/Sumarize`
   - Database name: `Sumarize`

3. **Test PDF** - ✓ Ready
   - File: `test-sample.pdf` (Software Vulnerability Penetration Tester)

## ⚠️ What You Still Need

### LlamaParser API Key (Required)

This is the **ONLY** thing you need to get before running the platform.

**Steps to get it**:
1. Go to: **https://cloud.llamaindex.ai/**
2. Sign up (free account)
3. Go to **API Keys** section
4. Click **"Create API Key"**
5. Copy the key (starts with `llx-...`)

**Then update your `.env` file**:
```bash
cd /Users/manansharma/Desktop/Study/pdf-learning-platform
nano .env
```

Replace this line:
```
LLAMAPARSE_API_KEY=your_llamaparse_api_key_here
```

With your actual key:
```
LLAMAPARSE_API_KEY=llx-your-actual-key-here
```

Save and exit (Ctrl+X, then Y, then Enter)

---

## 🚀 Running the Platform

Once you have the LlamaParser API key:

```bash
cd /Users/manansharma/Desktop/Study/pdf-learning-platform

# Start the server
npm start
```

You should see:
```
✓ MongoDB connected successfully
✓ Using Azure OpenAI
🚀 PDF Learning Platform running on http://localhost:3000
```

Then open: **http://localhost:3000**

---

## 📤 Testing with Your PDF

1. Open http://localhost:3000
2. Click "Choose PDF File"
3. Select the test PDF (or upload via the web interface)
4. Click "Upload & Process"
5. Wait 1-2 minutes (the PDF will be parsed and summarized)
6. You'll be redirected to see all sections with AI summaries

---

## 💰 Cost Estimate

- **LlamaParser**: Free (1,000 pages/month)
- **Azure OpenAI**: You're using GPT-4.1, cost depends on your Azure pricing
- **MongoDB Atlas**: Free tier (M0 cluster)

For your test PDF (~30-40 pages), expect:
- Processing time: 1-2 minutes
- Azure OpenAI cost: ~$0.50-1.00 (depends on sections)

---

## 🔧 Quick Commands

```bash
# Navigate to project
cd /Users/manansharma/Desktop/Study/pdf-learning-platform

# Start server
npm start

# Check if .env is configured
cat .env

# Edit .env
nano .env
```

---

## ❓ Troubleshooting

**"MongoDB connection error"**
- Your MongoDB URI might need authentication
- Check if you need to add username:password to the connection string
- Format: `mongodb+srv://username:password@cluster0.yfuwlmd.mongodb.net/Sumarize`

**"LlamaParser API error"**
- Make sure you've added the API key to `.env`
- Restart the server after updating `.env`

**"Azure OpenAI error"**
- Your credentials are already configured
- Make sure your Azure deployment is active

---

## 📝 Next Step

**Get your LlamaParser API key from https://cloud.llamaindex.ai/ and add it to `.env`**

Then you're ready to run!
