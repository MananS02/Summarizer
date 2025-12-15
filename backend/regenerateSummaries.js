require('dotenv').config();
const mongoose = require('mongoose');
const OpenAI = require('openai');
const Section = require('./models/Section');

// Initialize OpenAI client (Azure or standard)
let openai;
if (process.env.AZURE_OPENAI_GPT_ENDPOINT) {
    console.log('✓ Using Azure OpenAI');
    openai = new OpenAI({
        apiKey: process.env.AZURE_OPENAI_GPT_KEY,
        baseURL: `${process.env.AZURE_OPENAI_GPT_ENDPOINT}/openai/deployments/${process.env.AZURE_OPENAI_GPT_DEPLOYMENT}`,
        defaultQuery: { 'api-version': process.env.AZURE_OPENAI_GPT_VERSION },
        defaultHeaders: { 'api-key': process.env.AZURE_OPENAI_GPT_KEY },
    });
} else {
    openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
}

async function generateSummary(heading, content) {
    try {
        // Truncate content to avoid token limits
        const truncatedContent = content.substring(0, 3000);

        const prompt = `Create a professional, well-formatted summary for this section.

SECTION HEADING: ${heading}

SECTION CONTENT:
${truncatedContent}

Generate:
1. A concise headline (max 12 words) that captures the main topic
2. A detailed summary with the following requirements:
   - Write 10-12 separate lines (use \\n for line breaks)
   - Each line should be a complete sentence or thought
   - Cover the key concepts and main points
   - Make it readable and well-structured
   - Avoid raw question/answer format
   - Focus on explaining the topic clearly
   
IMPORTANT: Format the summary with actual line breaks (\\n) between sentences.

Return ONLY valid JSON in this exact format:
{ "headline": "your headline here", "summary": "line 1\\nline 2\\nline 3\\n...\\nline 10-12" }`;

        const response = await openai.chat.completions.create({
            model: process.env.AZURE_OPENAI_GPT_DEPLOYMENT || 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'system',
                    content: 'You are a technical writer creating clear, professional summaries for educational content. Always return valid JSON.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: 0.7,
            max_tokens: 500
        });

        const result = response.choices[0].message.content.trim();

        // Try to parse JSON
        let parsed;
        try {
            // Remove markdown code blocks if present
            const cleaned = result.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
            parsed = JSON.parse(cleaned);
        } catch (e) {
            console.error('Failed to parse JSON:', result);
            throw new Error('Invalid JSON response from AI');
        }

        return {
            headline: parsed.headline || heading,
            summary: parsed.summary || content.substring(0, 500)
        };

    } catch (error) {
        console.error(`Error generating summary for "${heading}":`, error.message);
        return {
            headline: heading,
            summary: content.substring(0, 500)
        };
    }
}

async function regenerateSummaries() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Get all sections
        const sections = await Section.find({ documentSlug: 'test-sample' }).sort({ order: 1 });
        console.log(`Found ${sections.length} sections`);

        // Generate summaries for each section
        for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            console.log(`\n[${i + 1}/${sections.length}] Processing: ${section.heading}`);

            const { headline, summary } = await generateSummary(section.heading, section.content);

            // Update section
            section.headline = headline;
            section.summary = summary;
            await section.save();

            console.log(`✓ Generated summary (${summary.split('\n').length} lines)`);

            // Small delay to avoid rate limiting
            if (i < sections.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }

        console.log('\n✅ All summaries regenerated successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error regenerating summaries:', error);
        process.exit(1);
    }
}

regenerateSummaries();
