const express = require('express');
const router = express.Router();
const Document = require('../models/Document');
const Section = require('../models/Section');

/**
 * GET /api/documents
 * Get all documents
 */
router.get('/', async (req, res) => {
    try {
        const documents = await Document.find()
            .sort({ uploadedAt: -1 })
            .select('title slug uploadedAt sectionCount');

        res.json(documents);
    } catch (error) {
        console.error('Error fetching documents:', error);
        res.status(500).json({ error: 'Failed to fetch documents' });
    }
});

/**
 * GET /api/documents/:slug
 * Get a specific document with all section summaries
 */
router.get('/:slug', async (req, res) => {
    try {
        const { slug } = req.params;

        // Find document
        const document = await Document.findOne({ slug });
        if (!document) {
            return res.status(404).json({ error: 'Document not found' });
        }

        // Find all sections for this document
        const sections = await Section.find({ documentSlug: slug })
            .sort({ order: 1 })
            .select('sectionSlug order heading headline summary');

        res.json({
            document: {
                title: document.title,
                slug: document.slug,
                uploadedAt: document.uploadedAt,
                sectionCount: document.sectionCount
            },
            sections
        });
    } catch (error) {
        console.error('Error fetching document:', error);
        res.status(500).json({ error: 'Failed to fetch document' });
    }
});

/**
 * DELETE /api/documents/:slug
 * Delete a document and all its sections
 */
router.delete('/:slug', async (req, res) => {
    try {
        const { slug } = req.params;

        const document = await Document.findOne({ slug });
        if (!document) {
            return res.status(404).json({ error: 'Document not found' });
        }

        // Delete all sections
        await Section.deleteMany({ documentSlug: slug });

        // Delete document
        await Document.deleteOne({ slug });

        res.json({ success: true, message: 'Document deleted successfully' });
    } catch (error) {
        console.error('Error deleting document:', error);
        res.status(500).json({ error: 'Failed to delete document' });
    }
});

module.exports = router;
