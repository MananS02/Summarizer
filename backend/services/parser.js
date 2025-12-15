const { exec } = require('child_process');
const util = require('util');
const path = require('path');
const slugify = require('slugify');

const execPromise = util.promisify(exec);

/**
 * Parse PDF using Python LlamaParser script
 * @param {string} filePath - Path to the PDF file
 * @param {string} documentSlug - Document slug for organizing assets
 * @returns {Promise<Array>} Array of section objects
 */
async function parsePDF(filePath, documentSlug) {
    try {
        console.log('📄 Parsing PDF with LlamaParser (Python)...');

        const pythonScript = path.join(__dirname, 'llama_parser.py');
        const pythonPath = path.join(__dirname, '../../venv/bin/python3');
        const apiKey = process.env.LLAMAPARSE_API_KEY;

        // Call Python script with virtual environment Python
        const { stdout, stderr } = await execPromise(
            `"${pythonPath}" "${pythonScript}" "${filePath}" "${apiKey}"`,
            { maxBuffer: 10 * 1024 * 1024 } // 10MB buffer
        );

        // Log any stderr output (verbose logging from LlamaParser)
        if (stderr) {
            console.log(stderr);
        }

        // Parse JSON output
        const result = JSON.parse(stdout);

        if (!result.success) {
            throw new Error(result.error || 'Unknown error from Python parser');
        }

        console.log(`✓ PDF parsed successfully (${result.page_count} pages)`);

        // Add documentSlug and sectionSlug to each section
        const sections = result.sections.map(section => ({
            ...section,
            documentSlug,
            sectionSlug: slugify(section.heading, { lower: true, strict: true }) + `-${section.order}`
        }));

        console.log(`✓ Extracted ${sections.length} sections`);

        return sections;

    } catch (error) {
        console.error('✗ LlamaParser error:', error.message);
        throw new Error(`Failed to parse PDF: ${error.message}`);
    }
}

/**
 * Dummy function for compatibility
 */
async function extractSections(markdown, documentSlug) {
    return [];
}

/**
 * Dummy function for compatibility
 */
async function saveAssets(assets, documentSlug) {
    // Not implemented for Python parser
}

module.exports = {
    parsePDF,
    extractSections,
    saveAssets
};
