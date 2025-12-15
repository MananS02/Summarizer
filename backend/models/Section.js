const mongoose = require('mongoose');

const sectionSchema = new mongoose.Schema({
    documentId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Document',
        required: true
    },
    documentSlug: {
        type: String,
        required: true,
        index: true
    },
    sectionSlug: {
        type: String,
        required: true
    },
    order: {
        type: Number,
        required: true
    },
    heading: {
        type: String,
        required: true
    },
    headline: {
        type: String,
        default: ''
    },
    summary: {
        type: String,
        default: ''
    },
    content: {
        type: String,
        default: ''
    },
    images: {
        type: [String],
        default: []
    },
    tables: {
        type: [String],
        default: []
    },
    previewImage: {
        type: String,
        default: null
    },
    blocks: [{
        type: {
            type: String,
            enum: ['text', 'table', 'image'],
            required: true
        },
        content: {
            type: String,
            required: true
        },
        order: {
            type: Number,
            required: true
        },
        bbox: {
            x: Number,
            y: Number,
            width: Number,
            height: Number
        },
        metadata: {
            type: mongoose.Schema.Types.Mixed,
            default: {}
        }
    }]
});

// Compound index for efficient querying
sectionSchema.index({ documentSlug: 1, order: 1 });
sectionSchema.index({ documentSlug: 1, sectionSlug: 1 });

module.exports = mongoose.model('Section', sectionSchema);
