const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true
    },
    slug: {
        type: String,
        required: true,
        unique: true
    },
    uploadedAt: {
        type: Date,
        default: Date.now
    },
    sectionCount: {
        type: Number,
        default: 0
    }
});

module.exports = mongoose.model('Document', documentSchema);
