require('dotenv').config();
const mongoose = require('mongoose');
const Document = require('./models/Document');
const Section = require('./models/Section');

// Sample data with longer summaries (10-12 lines)
const sampleSections = [
    {
        order: 0,
        heading: "Introduction to Software Vulnerability Testing",
        headline: "Understanding Security Assessment Fundamentals",
        summary: `Software vulnerability testing is a critical component of modern cybersecurity practices that helps organizations identify and mitigate security risks before they can be exploited by malicious actors.

This comprehensive guide explores various methodologies and techniques used by security professionals to assess the security posture of software systems. Penetration testing, often called ethical hacking, involves simulating real-world attacks to discover vulnerabilities in applications, networks, and infrastructure.

The importance of security assessments has grown exponentially as organizations increasingly rely on digital systems to store sensitive data and conduct business operations. Regular vulnerability testing helps prevent data breaches, protect customer information, and maintain compliance with industry regulations.

Security professionals use a combination of automated tools and manual testing techniques to identify weaknesses in authentication mechanisms, data encryption, access controls, and application logic. The testing process follows a structured methodology that ensures comprehensive coverage of potential attack vectors.

Understanding the fundamentals of vulnerability testing is essential for developers, security analysts, and IT professionals who are responsible for protecting organizational assets. This section provides a foundation for the more advanced topics covered in subsequent chapters.`,
        content: "Software vulnerability testing is a critical component of modern cybersecurity practices. This comprehensive guide explores various methodologies and techniques used by security professionals to identify and mitigate potential security risks in software systems.\n\nPenetration testing, often called ethical hacking, involves simulating real-world attacks to discover vulnerabilities before malicious actors can exploit them. This proactive approach helps organizations strengthen their security posture and protect sensitive data.\n\nThe testing process requires a deep understanding of attack vectors, security protocols, and system architectures. Professional testers must stay current with emerging threats and continuously update their skills to address new vulnerabilities.",
        previewImage: null
    },
    {
        order: 1,
        heading: "Common Vulnerability Types",
        headline: "Identifying Critical Security Weaknesses",
        summary: `Understanding common vulnerability types is essential for effective security testing and risk mitigation. The OWASP Top 10 provides a standardized awareness document that helps developers and security professionals focus on the most critical web application security risks.

Injection flaws, such as SQL injection and command injection, occur when untrusted data is sent to an interpreter as part of a command or query. These vulnerabilities can allow attackers to execute arbitrary commands, access unauthorized data, or compromise entire database systems.

Cross-Site Scripting (XSS) attacks enable attackers to inject malicious scripts into web pages viewed by other users. This can lead to session hijacking, credential theft, and defacement of websites. XSS vulnerabilities are particularly dangerous because they can affect multiple users simultaneously.

Broken authentication and session management vulnerabilities can allow attackers to compromise passwords, keys, or session tokens. Weak password policies, improper session timeout settings, and insecure credential storage are common causes of these vulnerabilities.

Sensitive data exposure occurs when applications fail to adequately protect sensitive information such as financial data, healthcare records, or personal identifiable information (PII). Proper encryption, both in transit and at rest, is essential for protecting sensitive data.`,
        content: "Understanding common vulnerability types is essential for effective security testing. The OWASP Top 10 provides a standardized awareness document for developers and security professionals.\n\nInjection flaws, such as SQL injection and command injection, occur when untrusted data is sent to an interpreter as part of a command or query. Cross-Site Scripting (XSS) attacks enable attackers to inject malicious scripts into web pages viewed by other users.\n\nBroken authentication and session management can allow attackers to compromise passwords, keys, or session tokens, or to exploit other implementation flaws to assume other users' identities. Security misconfiguration is another common vulnerability that occurs when security settings are not properly defined or maintained.",
        previewImage: null
    },
    {
        order: 2,
        heading: "Penetration Testing Methodology",
        headline: "Systematic Approach to Security Assessment",
        summary: `A structured penetration testing methodology ensures comprehensive coverage and consistent results across different testing engagements. The process typically follows five distinct phases that guide testers from initial reconnaissance through final reporting.

Planning and Reconnaissance is the first phase where testers define the scope of the engagement, gather intelligence about the target system, and identify potential entry points. This phase includes both passive information gathering (OSINT) and active reconnaissance techniques.

Scanning is the second phase where testers use automated tools to identify open ports, running services, and potential vulnerabilities. Network scanners, vulnerability scanners, and web application scanners help create a comprehensive picture of the target's attack surface.

Gaining Access involves attempting to exploit identified vulnerabilities to demonstrate their impact. Testers use various exploitation techniques and tools to validate vulnerabilities and determine if they can be used to compromise the system.

Maintaining Access tests whether vulnerabilities can be used to achieve persistent access to the target system. This phase simulates advanced persistent threats (APTs) and helps organizations understand the potential for long-term compromise.

Analysis and Reporting is the final phase where testers document all findings, assess risk levels, and provide detailed remediation recommendations. Clear communication of technical findings to both technical and non-technical stakeholders is crucial for effective remediation.`,
        content: "A structured penetration testing methodology ensures comprehensive coverage and consistent results. The process typically follows these phases:\n\n1. Planning and Reconnaissance: Define scope and gather intelligence\n2. Scanning: Identify open ports, services, and potential vulnerabilities\n3. Gaining Access: Attempt to exploit identified vulnerabilities\n4. Maintaining Access: Determine if the vulnerability can be used for persistent access\n5. Analysis and Reporting: Document findings and provide remediation recommendations\n\nEach phase requires specific tools and techniques, and testers must maintain detailed documentation throughout the process. The methodology can be adapted based on the type of engagement, whether it's a black box, white box, or gray box test.",
        previewImage: null
    }
];

async function updateSampleData() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Delete existing data
        await Document.deleteMany({ slug: 'test-sample' });
        await Section.deleteMany({ documentSlug: 'test-sample' });
        console.log('✓ Cleared old data');

        // Create document
        const document = new Document({
            title: 'Software Vulnerability Penetration Tester',
            slug: 'test-sample',
            sectionCount: sampleSections.length
        });
        await document.save();
        console.log('✓ Created document');

        // Create sections
        const sectionDocs = sampleSections.map(section => ({
            documentId: document._id,
            documentSlug: 'test-sample',
            sectionSlug: `section-${section.order}`,
            order: section.order,
            heading: section.heading,
            headline: section.headline,
            summary: section.summary,
            content: section.content,
            images: [],
            tables: [],
            previewImage: section.previewImage
        }));

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections with longer summaries`);

        console.log('\n✅ Sample data updated successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error updating sample data:', error);
        process.exit(1);
    }
}

updateSampleData();
