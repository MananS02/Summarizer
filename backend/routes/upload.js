const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs').promises;
const slugify = require('slugify');
const Document = require('../models/Document');
const Section = require('../models/Section');
const { parsePDF } = require('../services/parser');
const { generateSummariesBatch } = require('../services/summarizer');

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const uploadDir = path.join(__dirname, '../uploads');
        await fs.mkdir(uploadDir, { recursive: true });
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + '-' + file.originalname);
    }
});

const upload = multer({
    storage,
    fileFilter: (req, file, cb) => {
        if (file.mimetype === 'application/pdf') {
            cb(null, true);
        } else {
            cb(new Error('Only PDF files are allowed'));
        }
    },
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB limit
    }
});

/**
 * POST /api/upload
 * Upload and process a PDF file
 */
router.post('/', upload.single('pdf'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No PDF file uploaded' });
        }

        console.log(`\n📤 Processing upload: ${req.file.originalname}`);

        // Generate document slug
        const title = path.parse(req.file.originalname).name;
        let slug = slugify(title, { lower: true, strict: true });

        // Ensure unique slug
        let existingDoc = await Document.findOne({ slug });
        let counter = 1;
        while (existingDoc) {
            slug = `${slugify(title, { lower: true, strict: true })}-${counter}`;
            existingDoc = await Document.findOne({ slug });
            counter++;
        }

        // Parse PDF with LlamaParser
        const sections = await parsePDF(req.file.path, slug);

        if (sections.length === 0) {
            // Clean up uploaded file
            await fs.unlink(req.file.path);
            return res.status(400).json({ error: 'No sections found in PDF' });
        }

        // Generate summaries for all sections
        const sectionsWithSummaries = await generateSummariesBatch(sections);

        // Create document in database
        const document = new Document({
            title,
            slug,
            sectionCount: sectionsWithSummaries.length
        });
        await document.save();

        // Save all sections to database
        const sectionDocs = sectionsWithSummaries.map(section => ({
            documentId: document._id,
            documentSlug: slug,
            sectionSlug: section.sectionSlug,
            order: section.order,
            heading: section.heading,
            headline: section.headline,
            summary: section.summary,
            content: section.content,
            images: section.images,
            tables: section.tables
        }));

        await Section.insertMany(sectionDocs);

        // Clean up uploaded PDF file
        await fs.unlink(req.file.path);

        console.log(`✓ Document processed successfully: ${slug}\n`);

        res.json({
            success: true,
            documentSlug: slug,
            sectionCount: sectionsWithSummaries.length,
            message: 'PDF processed successfully'
        });

    } catch (error) {
        console.error('✗ Upload error:', error);

        // Clean up file if it exists
        if (req.file) {
            try {
                await fs.unlink(req.file.path);
            } catch (e) {
                // Ignore cleanup errors
            }
        }

        res.status(500).json({
            error: 'Failed to process PDF',
            message: error.message
        });
    }
});

module.exports = router;
