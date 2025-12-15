require('dotenv').config();
const mongoose = require('mongoose');
const { exec } = require('child_process');
const util = require('util');
const slugify = require('slugify');
const Document = require('./models/Document');
const Section = require('./models/Section');

const execPromise = util.promisify(exec);

async function processWithBlocks() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Paths
        const pdfPath = '/Users/manansharma/Desktop/Study/PH_English_Software_Vulnerability_Penetration_tester_SSC_Q0912_V3.0_removed.pdf';
        const outputDir = __dirname + '/../public/uploads/test-sample';
        const pythonScript = __dirname + '/services/process_pdf_blocks.py';
        const pythonPath = __dirname + '/../venv/bin/python3';

        console.log('📄 Processing PDF with ordered blocks...');
        console.log('⏳ This may take a minute...\n');

        // Call Python script
        const { stdout, stderr } = await execPromise(
            `"${pythonPath}" "${pythonScript}" "${pdfPath}" "${outputDir}"`,
            { maxBuffer: 20 * 1024 * 1024 }
        );

        // Log any stderr output
        if (stderr) {
            console.log('Python output:', stderr);
        }

        // Extract JSON from stdout (ignore warning messages)
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

        console.log(`✓ PDF processed successfully`);
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
            // Get text and image blocks
            const textBlocks = section.blocks.filter(b => b.type === 'text');
            const imageBlocks = section.blocks.filter(b => b.type === 'image');

            // Create summary from first few text blocks
            const summaryText = textBlocks.slice(0, 10).map(b => b.content).join('\n');

            // Get preview image
            const previewImage = imageBlocks.length > 0 ? imageBlocks[0].content : null;

            return {
                documentId: document._id,
                documentSlug: 'test-sample',
                sectionSlug: slugify(section.heading, { lower: true, strict: true }) + `-${index}`,
                order: section.order,
                heading: section.heading,
                headline: section.heading.substring(0, 100),
                summary: summaryText.substring(0, 600),
                content: textBlocks.map(b => b.content).join('\n\n'),
                images: imageBlocks.map(b => b.content),
                tables: [],
                previewImage: previewImage,
                blocks: section.blocks
            };
        });

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections with ordered blocks`);

        // Statistics
        const totalBlocks = sectionDocs.reduce((sum, s) => sum + s.blocks.length, 0);
        const totalImages = sectionDocs.reduce((sum, s) => sum + s.images.length, 0);

        console.log(`\n📊 Statistics:`);
        console.log(`  Total blocks: ${totalBlocks}`);
        console.log(`  Images: ${totalImages}`);
        console.log(`  Sections with blocks: ${sectionDocs.filter(s => s.blocks.length > 0).length}`);

        console.log('\n✅ Ordered blocks data inserted successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);
        console.log('💡 Run: node backend/regenerateSummaries.js to generate AI summaries\n');

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error:', error);
        if (error.stdout) console.log('stdout:', error.stdout);
        if (error.stderr) console.log('stderr:', error.stderr);
        process.exit(1);
    }
}

processWithBlocks();
