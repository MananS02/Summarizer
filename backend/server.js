require('dotenv').config();
const express = require('express');
const path = require('path');
const connectDB = require('./config/db');
const autoProcessPDF = require('./autoProcess');

// Import routes
const documentsRoute = require('./routes/documents');
const sectionsRoute = require('./routes/sections');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (frontend + uploaded assets)
app.use(express.static(path.join(__dirname, '../public')));

// API Routes
app.use('/api/documents', documentsRoute);
app.use('/api/sections', sectionsRoute);

// Frontend routes (SPA-style routing)
app.get('/topic/:sectionSlug', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/topic.html'));
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message
    });
});

// Start server
async function startServer() {
    try {
        // Connect to MongoDB first
        await connectDB();

        // Auto-process PDF if not already done
        await autoProcessPDF();

        // Start Express server
        app.listen(PORT, () => {
            console.log(`\n🚀 PDF Learning Platform running on http://localhost:${PORT}`);
            console.log(`📚 View topic summaries at http://localhost:${PORT}\n`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer();
