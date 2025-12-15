require('dotenv').config();
const mongoose = require('mongoose');
const { generateSummary } = require('./services/summarizer');
const Section = require('./models/Section');

async function regenerateSummariesFast() {
    try {
        console.log('\n' + '='.repeat(60));
        console.log('REGENERATING AI SUMMARIES');
        console.log('='.repeat(60) + '\n');

        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Get all sections
        const sections = await Section.find({ documentSlug: 'test-sample' }).sort({ order: 1 });
        console.log(`✓ Found ${sections.length} sections\n`);

        if (sections.length === 0) {
            console.log('❌ No sections found. Run insertLLMData.js first.');
            process.exit(1);
        }

        // Generate summaries for each section
        let completed = 0;
        const startTime = Date.now();

        for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            const sectionNum = i + 1;

            console.log(`[${sectionNum}/${sections.length}] ${section.heading}`);
            console.log(`  Generating summary...`);

            try {
                const { headline, summary } = await generateSummary(section.content, section.heading);

                // Update section
                section.headline = headline;
                section.summary = summary;
                await section.save();

                completed++;
                const wordCount = summary.split(' ').length;
                console.log(`  ✓ Complete (${wordCount} words)\n`);

            } catch (error) {
                console.log(`  ✗ Failed: ${error.message}\n`);
            }

            // Small delay to avoid rate limiting (reduced to 500ms)
            if (i < sections.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }

        const duration = ((Date.now() - startTime) / 1000).toFixed(1);

        console.log('='.repeat(60));
        console.log(`✅ COMPLETE: ${completed}/${sections.length} summaries generated`);
        console.log(`⏱️  Time: ${duration}s`);
        console.log('='.repeat(60));
        console.log(`\n🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('\n❌ Error:', error.message);
        process.exit(1);
    }
}

regenerateSummariesFast();
