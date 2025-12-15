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

// Health check endpoint
app.get('/health', async (req, res) => {
    try {
        const mongoose = require('mongoose');
        const dbStatus = mongoose.connection.readyState === 1 ? 'connected' : 'disconnected';

        res.json({
            status: 'ok',
            timestamp: new Date().toISOString(),
            uptime: process.uptime(),
            mongodb: dbStatus,
            environment: process.env.NODE_ENV || 'development'
        });
    } catch (error) {
        res.status(503).json({
            status: 'error',
            message: error.message
        });
    }
});

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

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: `Route ${req.url} not found`
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);

    const statusCode = err.statusCode || 500;
    const message = process.env.NODE_ENV === 'production'
        ? 'Internal server error'
        : err.message;

    res.status(statusCode).json({
        error: 'Server Error',
        message: message,
        ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
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
