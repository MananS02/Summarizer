const path = require('path');
require('dotenv').config();

// Import database connection and models
const connectDB = require('./config/db');
const Document = require('./models/Document');

/**
 * Check if data exists in MongoDB
 */
async function autoProcessPDF() {
    try {
        // Connect to MongoDB
        await connectDB();

        // Check if data already exists
        const existingDoc = await Document.findOne({ slug: 'test-sample' });
        if (existingDoc) {
            console.log('✓ Data already exists in MongoDB');
            console.log(`📚 View at: http://localhost:${process.env.PORT || 3000}/`);
            return;
        }

        console.log('\n⚠️  No data found in MongoDB');
        console.log('   Run: node backend/insertSampleData.js');
        console.log('   to insert sample data\n');

    } catch (error) {
        console.error('❌ Error:', error.message);
        // Don't throw - allow server to start anyway
    }
}

module.exports = autoProcessPDF;
