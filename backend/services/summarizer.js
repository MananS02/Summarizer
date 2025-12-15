const OpenAI = require('openai');

// Support both Azure OpenAI and standard OpenAI
let openai;

if (process.env.AZURE_OPENAI_GPT_ENDPOINT) {
    // Use Azure OpenAI
    openai = new OpenAI({
        apiKey: process.env.AZURE_OPENAI_GPT_KEY,
        baseURL: `${process.env.AZURE_OPENAI_GPT_ENDPOINT}/openai/deployments/${process.env.AZURE_OPENAI_GPT_DEPLOYMENT}`,
        defaultQuery: { 'api-version': process.env.AZURE_OPENAI_GPT_VERSION },
        defaultHeaders: { 'api-key': process.env.AZURE_OPENAI_GPT_KEY }
    });
    console.log('✓ Using Azure OpenAI');
} else {
    // Use standard OpenAI
    openai = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
    });
    console.log('✓ Using OpenAI');
}

/**
 * Generate headline and summary for a section using LLM
 * @param {string} sectionText - The section content to summarize
 * @param {string} heading - The section heading
 * @returns {Promise<Object>} Object with headline and summary
 */
async function generateSummary(sectionText, heading) {
    try {
        // Truncate content if too long (keep first 3000 chars)
        const truncatedText = sectionText.length > 3000
            ? sectionText.substring(0, 3000) + '...'
            : sectionText;

        const prompt = `Analyze this section and create a comprehensive summary.

TASK:
1. Create a concise headline (maximum 12 words)
2. Write a detailed summary (10-12 complete sentences)

REQUIREMENTS FOR SUMMARY:
- Cover ALL key points and concepts from the section
- Include important details, facts, and figures
- Write in complete sentences (no bullet points)
- Make it informative and educational
- Ensure the summary is COMPLETE (no cutoffs)
- Focus on the most valuable information for learners

Return ONLY valid JSON in this format:
{
  "headline": "concise headline here",
  "summary": "Complete detailed summary in 10-12 sentences covering all key points..."
}

SECTION HEADING: ${heading}

SECTION CONTENT:
${truncatedText}`;

        const response = await openai.chat.completions.create({
            model: process.env.AZURE_OPENAI_GPT_DEPLOYMENT || 'gpt-3.5-turbo',
            messages: [
                {
                    role: 'system',
                    content: 'You are an expert educational content summarizer. Create comprehensive, complete summaries that help students learn. Always respond with valid JSON. Never cut off summaries mid-sentence.'
                },
                {
                    role: 'user',
                    content: prompt
                }
            ],
            temperature: 0.5,
            max_tokens: 500,
            response_format: { type: 'json_object' }
        });

        const result = JSON.parse(response.choices[0].message.content);

        // Validate headline length
        const words = result.headline.split(' ');
        if (words.length > 12) {
            result.headline = words.slice(0, 12).join(' ') + '...';
        }

        console.log(`✓ Generated summary for: ${heading}`);

        return {
            headline: result.headline || heading,
            summary: result.summary || 'Summary not available.'
        };

    } catch (error) {
        console.error('✗ Summarization error:', error.message);

        // Fallback to heading if summarization fails
        return {
            headline: heading,
            summary: 'Summary generation failed. Please review the full content.'
        };
    }
}

/**
 * Generate summaries for multiple sections in batch
 * @param {Array} sections - Array of section objects
 * @returns {Promise<Array>} Sections with added headline and summary
 */
async function generateSummariesBatch(sections) {
    console.log(`📝 Generating summaries for ${sections.length} sections...`);

    const results = [];

    for (const section of sections) {
        const { headline, summary } = await generateSummary(section.content, section.heading);
        results.push({
            ...section,
            headline,
            summary
        });

        // Small delay to avoid rate limits
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    console.log('✓ All summaries generated');
    return results;
}

module.exports = {
    generateSummary,
    generateSummariesBatch
};
