#!/bin/bash

# PDF Learning Platform - Setup Script

echo "📚 PDF Learning Platform Setup"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env and add your API keys:"
    echo "   - LLAMAPARSE_API_KEY (get from https://cloud.llamaindex.ai/)"
    echo "   - OPENAI_API_KEY (get from https://platform.openai.com/api-keys)"
    echo "   - MONGODB_URI (default: mongodb://localhost:27017/pdf-learning-platform)"
    echo ""
    echo "After adding your API keys, run this script again."
    exit 1
fi

# Check if API keys are set
source .env

if [ "$LLAMAPARSE_API_KEY" = "your_llamaparse_api_key_here" ]; then
    echo "❌ LLAMAPARSE_API_KEY not set in .env"
    echo "   Get your key from: https://cloud.llamaindex.ai/"
    exit 1
fi

if [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY not set in .env"
    echo "   Get your key from: https://platform.openai.com/api-keys"
    exit 1
fi

echo "✓ API keys configured"
echo ""

# Check if MongoDB is running (local)
if [[ $MONGODB_URI == *"localhost"* ]]; then
    echo "Checking MongoDB connection..."
    if ! nc -z localhost 27017 2>/dev/null; then
        echo "⚠️  MongoDB not running on localhost:27017"
        echo ""
        echo "Start MongoDB with one of these commands:"
        echo "  macOS:  brew services start mongodb-community"
        echo "  Linux:  sudo systemctl start mongod"
        echo ""
        echo "Or update MONGODB_URI in .env to use MongoDB Atlas"
        exit 1
    fi
    echo "✓ MongoDB is running"
else
    echo "✓ Using MongoDB Atlas"
fi

echo ""
echo "🚀 Starting server..."
echo ""

npm start
