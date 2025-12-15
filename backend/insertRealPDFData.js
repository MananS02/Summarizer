require('dotenv').config();
const mongoose = require('mongoose');
const fs = require('fs').promises;
const slugify = require('slugify');
const Document = require('./models/Document');
const Section = require('./models/Section');

async function insertRealPDFData() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Read the processed PDF data
        const jsonData = await fs.readFile('/tmp/pdf_sections.json', 'utf8');
        const pdfData = JSON.parse(jsonData);

        if (!pdfData.success) {
            throw new Error(pdfData.error || 'Failed to process PDF');
        }

        console.log(`Found ${pdfData.sections.length} sections`);

        // Delete existing data
        await Document.deleteMany({ slug: 'test-sample' });
        await Section.deleteMany({ documentSlug: 'test-sample' });
        console.log('✓ Cleared old data');

        // Create document
        const document = new Document({
            title: 'Software Vulnerability Penetration Tester',
            slug: 'test-sample',
            sectionCount: pdfData.sections.length
        });
        await document.save();
        console.log('✓ Created document');

        // Create sections with real data
        const sectionDocs = pdfData.sections.map((section, index) => {
            // Create summary from first 10-12 lines of content
            const contentLines = section.content.split('\n').filter(line => line.trim());
            const summaryLines = contentLines.slice(0, 12);
            const summary = summaryLines.join('\n');

            // Generate headline from heading (max 12 words)
            const headingWords = section.heading.split(' ');
            const headline = headingWords.slice(0, 12).join(' ');

            // Set preview image (first image if available)
            const previewImage = section.images && section.images.length > 0 ? section.images[0] : null;

            return {
                documentId: document._id,
                documentSlug: 'test-sample',
                sectionSlug: slugify(section.heading, { lower: true, strict: true }) + `-${index}`,
                order: section.order,
                heading: section.heading,
                headline: headline,
                summary: summary,
                content: section.content,
                images: section.images || [],
                tables: section.tables || [],
                previewImage: previewImage
            };
        });

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections with real PDF data`);

        // Show summary
        const sectionsWithImages = sectionDocs.filter(s => s.images.length > 0);
        console.log(`✓ ${sectionsWithImages.length} sections have images`);
        console.log(`✓ Total images: ${sectionDocs.reduce((sum, s) => sum + s.images.length, 0)}`);

        console.log('\n✅ Real PDF data inserted successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error inserting real PDF data:', error);
        process.exit(1);
    }
}

insertRealPDFData();
