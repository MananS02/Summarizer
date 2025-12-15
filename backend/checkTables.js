require('dotenv').config();
const mongoose = require('mongoose');
const Section = require('./models/Section');

async function checkTables() {
    try {
        await mongoose.connect(process.env.MONGODB_URI);

        const sections = await Section.find({ documentSlug: 'test-sample' })
            .sort({ order: 1 });

        console.log(`\nTotal sections: ${sections.length}\n`);

        sections.forEach((section, i) => {
            const tableBlocks = section.blocks.filter(b => b.type === 'table');
            const imageBlocks = section.blocks.filter(b => b.type === 'image');

            console.log(`[${i + 1}] ${section.heading}`);
            console.log(`    Blocks: ${section.blocks.length} total`);
            console.log(`    Tables: ${tableBlocks.length}`);
            console.log(`    Images: ${imageBlocks.length}`);

            if (tableBlocks.length > 0) {
                console.log(`    Table files: ${tableBlocks.map(t => t.content).join(', ')}`);
            }
            console.log('');
        });

        await mongoose.connection.close();
    } catch (error) {
        console.error('Error:', error);
    }
}

checkTables();
