const express = require('express');
const router = express.Router();
const Section = require('../models/Section');

/**
 * GET /api/sections/:docSlug/:sectionSlug
 * Get full section content
 */
router.get('/:docSlug/:sectionSlug', async (req, res) => {
    try {
        const { docSlug, sectionSlug } = req.params;

        // Find the section
        const section = await Section.findOne({
            documentSlug: docSlug,
            sectionSlug: sectionSlug
        });

        if (!section) {
            return res.status(404).json({ error: 'Section not found' });
        }

        // Get navigation info (previous/next sections)
        const prevSection = await Section.findOne({
            documentSlug: docSlug,
            order: section.order - 1
        }).select('sectionSlug heading');

        const nextSection = await Section.findOne({
            documentSlug: docSlug,
            order: section.order + 1
        }).select('sectionSlug heading');

        res.json({
            section: {
                heading: section.heading,
                headline: section.headline,
                summary: section.summary,
                content: section.content,
                images: section.images,
                tables: section.tables,
                order: section.order,
                blocks: section.blocks || [] // NEW: ordered blocks
            },
            navigation: {
                previous: prevSection ? {
                    slug: prevSection.sectionSlug,
                    heading: prevSection.heading
                } : null,
                next: nextSection ? {
                    slug: nextSection.sectionSlug,
                    heading: nextSection.heading
                } : null
            }
        });
    } catch (error) {
        console.error('Error fetching section:', error);
        res.status(500).json({ error: 'Failed to fetch section' });
    }
});

module.exports = router;
