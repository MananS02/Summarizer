const pdfParse = require('pdf-parse');
const fs = require('fs').promises;
const path = require('path');
const slugify = require('slugify');

/**
 * Simple PDF parser using pdf-parse (fallback when LlamaParser fails)
 * @param {string} filePath - Path to the PDF file
 * @param {string} documentSlug - Document slug for organizing assets
 * @returns {Promise<Array>} Array of section objects
 */
async function parseSimplePDF(filePath, documentSlug) {
    try {
        console.log('📄 Parsing PDF with simple parser...');

        // Read the PDF file
        const dataBuffer = await fs.readFile(filePath);

        // Parse PDF
        const data = await pdfParse(dataBuffer);

        console.log(`✓ Extracted ${data.numpages} pages`);

        // Split content into sections based on common patterns
        const sections = extractSectionsFromText(data.text, documentSlug);

        console.log(`✓ Created ${sections.length} sections`);

        return sections;

    } catch (error) {
        console.error('✗ Simple parser error:', error.message);
        throw new Error(`Failed to parse PDF: ${error.message}`);
    }
}

/**
 * Extract sections from plain text
 * @param {string} text - PDF text content
 * @param {string} documentSlug - Document slug
 * @returns {Array} Array of section objects
 */
function extractSectionsFromText(text, documentSlug) {
    const sections = [];

    // Split by common section patterns
    // Look for numbered sections, capitalized headings, etc.
    const lines = text.split('\n');
    let currentSection = null;
    let order = 0;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Skip empty lines
        if (!line) continue;

        // Check if line looks like a heading
        // Patterns: "1. Title", "SECTION 1:", "Chapter 1", all caps lines, etc.
        const isHeading = (
            /^(\d+\.|\d+\)|\w+\s+\d+:?)\s+[A-Z]/.test(line) || // Numbered headings
            (line.length < 100 && line === line.toUpperCase() && line.length > 5) || // All caps
            /^(SECTION|CHAPTER|PART|UNIT|MODULE)\s+\d+/i.test(line) // Common section keywords
        );

        if (isHeading) {
            // Save previous section
            if (currentSection && currentSection.content.trim()) {
                sections.push(currentSection);
                order++;
            }

            // Start new section
            const heading = line;
            const sectionSlug = slugify(heading.substring(0, 50), { lower: true, strict: true }) + `-${order}`;

            currentSection = {
                documentSlug,
                sectionSlug,
                order,
                heading,
                content: '',
                images: [],
                tables: []
            };
        } else if (currentSection) {
            // Add content to current section
            currentSection.content += line + '\n';
        } else {
            // No section yet, create an introduction section
            if (!currentSection) {
                currentSection = {
                    documentSlug,
                    sectionSlug: 'introduction',
                    order: 0,
                    heading: 'Introduction',
                    content: line + '\n',
                    images: [],
                    tables: []
                };
            }
        }
    }

    // Add last section
    if (currentSection && currentSection.content.trim()) {
        sections.push(currentSection);
    }

    // If no sections found, create one section with all content
    if (sections.length === 0) {
        sections.push({
            documentSlug,
            sectionSlug: 'content',
            order: 0,
            heading: 'Document Content',
            content: text,
            images: [],
            tables: []
        });
    }

    return sections;
}

module.exports = {
    parseSimplePDF,
    extractSectionsFromText
};
