require('dotenv').config();
const mongoose = require('mongoose');
const { exec } = require('child_process');
const util = require('util');
const slugify = require('slugify');
const Document = require('./models/Document');
const Section = require('./models/Section');

const execPromise = util.promisify(exec);

async function processWithAI() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Paths and configuration
        const pdfPath = '/Users/manansharma/Desktop/Study/PH_English_Software_Vulnerability_Penetration_tester_SSC_Q0912_V3.0_removed.pdf';
        const outputDir = __dirname + '/../public/uploads/test-sample';
        const pythonScript = __dirname + '/services/process_pdf_with_ai.py';
        const pythonPath = __dirname + '/../venv/bin/python3';

        // Azure OpenAI configuration
        const azureEndpoint = process.env.AZURE_OPENAI_GPT_ENDPOINT;
        const azureKey = process.env.AZURE_OPENAI_GPT_KEY;
        const deployment = process.env.AZURE_OPENAI_GPT_DEPLOYMENT;

        console.log('📄 Processing PDF with AI-powered image classification...');
        console.log('🤖 Using GPT-4 Vision for intelligent image filtering');
        console.log('⏳ This may take 3-5 minutes (AI classifying each image)...\n');

        // Call Python script with AI
        const { stdout, stderr } = await execPromise(
            `"${pythonPath}" "${pythonScript}" "${pdfPath}" "${outputDir}" "${azureEndpoint}" "${azureKey}" "${deployment}"`,
            { maxBuffer: 20 * 1024 * 1024 }
        );

        if (stderr) {
            console.log('Python output:', stderr);
        }

        // Extract JSON from stdout
        let jsonStr = stdout;
        const jsonStart = stdout.indexOf('{');
        if (jsonStart > 0) {
            jsonStr = stdout.substring(jsonStart);
        }

        // Parse JSON output
        const result = JSON.parse(jsonStr);

        if (!result.success) {
            throw new Error(result.error || 'Unknown error');
        }

        console.log(`\n✓ PDF processed successfully with AI`);
        console.log(`  Sections: ${result.sections.length}`);
        if (result.statistics) {
            console.log(`\n📊 AI Classification Statistics:`);
            console.log(`  Total images found: ${result.statistics.total_images_found}`);
            console.log(`  Classified as important: ${result.statistics.images_classified_important}`);
            console.log(`  Classified as decorative: ${result.statistics.images_classified_decorative}`);
            console.log(`  Images saved: ${result.statistics.images_saved}`);
            console.log(`  Tables extracted: ${result.statistics.total_tables}`);
        }

        // Delete existing data
        await Document.deleteMany({ slug: 'test-sample' });
        await Section.deleteMany({ documentSlug: 'test-sample' });
        console.log('\n✓ Cleared old data');

        // Create document
        const document = new Document({
            title: 'Software Vulnerability Penetration Tester',
            slug: 'test-sample',
            sectionCount: result.sections.length
        });
        await document.save();
        console.log('✓ Created document');

        // Create sections with AI-enhanced blocks
        const sectionDocs = result.sections.map((section, index) => {
            // Get text and image blocks
            const textBlocks = section.blocks.filter(b => b.type === 'text');
            const imageBlocks = section.blocks.filter(b => b.type === 'image');
            const tableBlocks = section.blocks.filter(b => b.type === 'table');

            // Get preview image (first AI-classified important image)
            const previewImage = imageBlocks.length > 0 ? imageBlocks[0].content : null;

            return {
                documentId: document._id,
                documentSlug: 'test-sample',
                sectionSlug: slugify(section.heading, { lower: true, strict: true }) + `-${index}`,
                order: section.order,
                heading: section.heading,
                headline: section.heading.substring(0, 100),
                summary: 'AI summary will be generated...', // Placeholder - regenerateSummaries.js will create proper summary
                content: textBlocks.map(b => b.content).join('\n\n'),
                images: imageBlocks.map(b => b.content),
                tables: tableBlocks.map(b => b.content),
                previewImage: previewImage,
                blocks: section.blocks  // Includes AI metadata
            };
        });

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections with AI-enhanced blocks`);

        // Statistics
        const totalBlocks = sectionDocs.reduce((sum, s) => sum + s.blocks.length, 0);
        const totalImages = sectionDocs.reduce((sum, s) => sum + s.images.length, 0);
        const totalTables = sectionDocs.reduce((sum, s) => sum + s.tables.length, 0);

        // Count AI-classified images
        const aiImages = sectionDocs.reduce((sum, s) => {
            return sum + s.blocks.filter(b => b.type === 'image' && b.metadata?.ai_classified).length;
        }, 0);

        console.log(`\n📊 Final Statistics:`);
        console.log(`  Total blocks: ${totalBlocks}`);
        console.log(`  AI-classified images: ${aiImages}`);
        console.log(`  Tables: ${totalTables}`);
        console.log(`  Sections with blocks: ${sectionDocs.filter(s => s.blocks.length > 0).length}`);

        console.log('\n✅ AI-enhanced data inserted successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/`);
        console.log('💡 Run: node backend/regenerateSummaries.js to generate AI summaries\n');

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error:', error);
        if (error.stdout) console.log('stdout:', error.stdout);
        if (error.stderr) console.log('stderr:', error.stderr);
        process.exit(1);
    }
}

processWithAI();
