require('dotenv').config();
const mongoose = require('mongoose');
const fs = require('fs').promises;
const { exec } = require('child_process');
const util = require('util');
const slugify = require('slugify');
const Document = require('./models/Document');
const Section = require('./models/Section');

const execPromise = util.promisify(exec);

async function processWithLayout() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Path to PDF and Python script
        const pdfPath = '/Users/manansharma/Desktop/Study/PH_English_Software_Vulnerability_Penetration_tester_SSC_Q0912_V3.0_removed.pdf';
        const pythonScript = __dirname + '/services/process_layout.py';
        const pythonPath = __dirname + '/../venv/bin/python3';
        const apiKey = process.env.LLAMAPARSE_API_KEY;

        console.log('📄 Processing PDF with layout extraction...');
        console.log('⏳ This may take 2-3 minutes...\n');

        // Call Python script
        const { stdout, stderr } = await execPromise(
            `"${pythonPath}" "${pythonScript}" "${pdfPath}" "${apiKey}"`,
            { maxBuffer: 20 * 1024 * 1024 } // 20MB buffer
        );

        // Log any stderr output
        if (stderr) {
            console.log('Python output:', stderr);
        }

        // Parse JSON output
        const result = JSON.parse(stdout);

        if (!result.success) {
            throw new Error(result.error || 'Unknown error from Python parser');
        }

        console.log(`✓ PDF parsed successfully`);
        console.log(`  Pages: ${result.total_pages}`);
        console.log(`  Sections: ${result.sections.length}`);

        // Delete existing data
        await Document.deleteMany({ slug: 'test-sample' });
        await Section.deleteMany({ documentSlug: 'test-sample' });
        console.log('✓ Cleared old data');

        // Create document
        const document = new Document({
            title: 'Software Vulnerability Penetration Tester',
            slug: 'test-sample',
            sectionCount: result.sections.length
        });
        await document.save();
        console.log('✓ Created document');

        // Create sections with blocks
        const sectionDocs = result.sections.map((section, index) => {
            // Generate headline and summary from first few blocks
            const textBlocks = section.blocks.filter(b => b.type === 'text');
            const summaryText = textBlocks.slice(0, 3).map(b => b.content).join('\n');

            // Get preview image (first image block)
            const imageBlocks = section.blocks.filter(b => b.type === 'image');
            const previewImage = imageBlocks.length > 0 ? imageBlocks[0].content : null;

            return {
                documentId: document._id,
                documentSlug: 'test-sample',
                sectionSlug: slugify(section.heading, { lower: true, strict: true }) + `-${index}`,
                order: section.order,
                heading: section.heading,
                headline: section.heading.substring(0, 100), // Will be updated by AI later
                summary: summaryText.substring(0, 500), // Will be updated by AI later
                content: textBlocks.map(b => b.content).join('\n\n'),
                images: imageBlocks.map(b => b.content),
                tables: section.blocks.filter(b => b.type === 'table').map(b => b.content),
                previewImage: previewImage,
                blocks: section.blocks // NEW: ordered blocks
            };
        });

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections with ordered blocks`);

        // Show statistics
        const totalBlocks = sectionDocs.reduce((sum, s) => sum + s.blocks.length, 0);
        const totalImages = sectionDocs.reduce((sum, s) => sum + s.images.length, 0);
        const totalTables = sectionDocs.reduce((sum, s) => sum + s.tables.length, 0);

        console.log(`\n📊 Statistics:`);
        console.log(`  Total blocks: ${totalBlocks}`);
        console.log(`  Images: ${totalImages}`);
        console.log(`  Tables: ${totalTables}`);

        console.log('\n✅ Layout-aware data inserted successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error processing with layout:', error);
        if (error.stdout) console.log('stdout:', error.stdout);
        if (error.stderr) console.log('stderr:', error.stderr);
        process.exit(1);
    }
}

processWithLayout();
