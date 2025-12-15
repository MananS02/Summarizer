require('dotenv').config();
const mongoose = require('mongoose');
const Section = require('./models/Section');

async function checkSummaries() {
    try {
        await mongoose.connect(process.env.MONGODB_URI);

        const sections = await Section.find({ documentSlug: 'test-sample' })
            .sort({ order: 1 })
            .limit(3);

        sections.forEach((section, i) => {
            console.log(`\n=== Section ${i + 1}: ${section.heading} ===`);
            console.log(`Headline: ${section.headline}`);
            console.log(`Summary length: ${section.summary.length} chars`);
            console.log(`Summary lines: ${section.summary.split('\n').filter(l => l.trim()).length}`);
            console.log(`Summary preview: ${section.summary.substring(0, 200)}...`);
        });

        await mongoose.connection.close();
    } catch (error) {
        console.error('Error:', error);
    }
}

checkSummaries();
