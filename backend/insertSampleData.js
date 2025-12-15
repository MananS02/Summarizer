require('dotenv').config();
const mongoose = require('mongoose');
const Document = require('./models/Document');
const Section = require('./models/Section');

// Sample data for demonstration
const sampleSections = [
    {
        order: 0,
        heading: "Introduction to Software Vulnerability Testing",
        headline: "Understanding Security Assessment Fundamentals",
        summary: "This section introduces the core concepts of software vulnerability testing and penetration testing methodologies. It covers the importance of security assessments in modern software development.",
        content: "Software vulnerability testing is a critical component of modern cybersecurity practices. This comprehensive guide explores various methodologies and techniques used by security professionals to identify and mitigate potential security risks in software systems.\n\nPenetration testing, often called ethical hacking, involves simulating real-world attacks to discover vulnerabilities before malicious actors can exploit them. This proactive approach helps organizations strengthen their security posture and protect sensitive data."
    },
    {
        order: 1,
        heading: "Common Vulnerability Types",
        headline: "Identifying Critical Security Weaknesses",
        summary: "Explores the most common types of vulnerabilities found in software applications, including injection flaws, broken authentication, and sensitive data exposure.",
        content: "Understanding common vulnerability types is essential for effective security testing. The OWASP Top 10 provides a standardized awareness document for developers and security professionals.\n\nInjection flaws, such as SQL injection and command injection, occur when untrusted data is sent to an interpreter as part of a command or query. Cross-Site Scripting (XSS) attacks enable attackers to inject malicious scripts into web pages viewed by other users.\n\nBroken authentication and session management can allow attackers to compromise passwords, keys, or session tokens, or to exploit other implementation flaws to assume other users' identities."
    },
    {
        order: 2,
        heading: "Penetration Testing Methodology",
        headline: "Systematic Approach to Security Assessment",
        summary: "Details the step-by-step process of conducting penetration tests, from reconnaissance and scanning to exploitation and reporting.",
        content: "A structured penetration testing methodology ensures comprehensive coverage and consistent results. The process typically follows these phases:\n\n1. Planning and Reconnaissance: Define scope and gather intelligence\n2. Scanning: Identify open ports, services, and potential vulnerabilities\n3. Gaining Access: Attempt to exploit identified vulnerabilities\n4. Maintaining Access: Determine if the vulnerability can be used for persistent access\n5. Analysis and Reporting: Document findings and provide remediation recommendations\n\nEach phase requires specific tools and techniques, and testers must maintain detailed documentation throughout the process."
    },
    {
        order: 3,
        heading: "Tools and Techniques",
        headline: "Essential Security Testing Tools",
        summary: "Overview of popular penetration testing tools including Metasploit, Burp Suite, Nmap, and Wireshark, along with their primary use cases.",
        content: "Professional penetration testers rely on a variety of specialized tools:\n\nMetasploit Framework: A comprehensive platform for developing and executing exploit code against remote targets.\n\nBurp Suite: An integrated platform for performing security testing of web applications, including scanning, crawling, and exploitation features.\n\nNmap: A network discovery and security auditing tool used for port scanning and service detection.\n\nWireshark: A network protocol analyzer for capturing and analyzing network traffic.\n\nKali Linux: A Debian-based Linux distribution designed for digital forensics and penetration testing, pre-loaded with hundreds of security tools."
    },
    {
        order: 4,
        heading: "Web Application Security",
        headline: "Protecting Modern Web Applications",
        summary: "Focuses on web-specific vulnerabilities and testing techniques, including OWASP Top 10 risks and secure coding practices.",
        content: "Web applications face unique security challenges due to their accessibility and complexity. Common web vulnerabilities include:\n\nSQL Injection: Manipulating database queries through user input\nCross-Site Scripting (XSS): Injecting malicious scripts into trusted websites\nCross-Site Request Forgery (CSRF): Forcing users to execute unwanted actions\nInsecure Direct Object References: Exposing internal implementation objects\nSecurity Misconfiguration: Improper security settings and default configurations\n\nSecure coding practices, input validation, output encoding, and proper authentication mechanisms are essential for preventing these vulnerabilities."
    },
    {
        order: 5,
        heading: "Network Security Testing",
        headline: "Assessing Network Infrastructure Security",
        summary: "Covers network-level security testing including port scanning, service enumeration, and network protocol analysis.",
        content: "Network security testing evaluates the security of network infrastructure and services. Key activities include:\n\nPort Scanning: Identifying open ports and running services\nService Enumeration: Determining versions and configurations of network services\nVulnerability Scanning: Automated detection of known vulnerabilities\nWireless Security Testing: Assessing Wi-Fi security and encryption\nFirewall Testing: Evaluating firewall rules and configurations\n\nNetwork segmentation, proper firewall configuration, and regular security updates are critical for maintaining network security."
    },
    {
        order: 6,
        heading: "Mobile Application Security",
        headline: "Securing iOS and Android Applications",
        summary: "Addresses mobile-specific security concerns including insecure data storage, weak cryptography, and platform-specific vulnerabilities.",
        content: "Mobile applications introduce unique security challenges:\n\nInsecure Data Storage: Sensitive data stored without proper encryption\nInsecure Communication: Unencrypted data transmission\nInsufficient Cryptography: Weak or broken cryptographic implementations\nInsecure Authentication: Weak password policies and session management\nCode Tampering: Reverse engineering and modification of application code\n\nMobile security testing requires specialized tools like MobSF, Frida, and platform-specific debuggers. Both static and dynamic analysis techniques are necessary for comprehensive assessment."
    },
    {
        order: 7,
        heading: "Reporting and Remediation",
        headline: "Communicating Findings Effectively",
        summary: "Guidelines for creating comprehensive penetration testing reports and working with development teams on vulnerability remediation.",
        content: "Effective reporting is crucial for translating technical findings into actionable recommendations:\n\nExecutive Summary: High-level overview for management\nTechnical Details: Detailed vulnerability descriptions with proof-of-concept\nRisk Assessment: CVSS scores and business impact analysis\nRemediation Recommendations: Specific steps to fix identified issues\nRetesting Results: Verification of fixes\n\nCollaboration with development teams ensures vulnerabilities are properly addressed. Follow-up testing verifies that remediation efforts were successful and didn't introduce new issues."
    }
];

async function insertSampleData() {
    try {
        // Connect to MongoDB
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('✓ Connected to MongoDB');

        // Check if data already exists
        const existingDoc = await Document.findOne({ slug: 'test-sample' });
        if (existingDoc) {
            console.log('✓ Sample data already exists');
            await mongoose.connection.close();
            return;
        }

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
            tables: []
        }));

        await Section.insertMany(sectionDocs);
        console.log(`✓ Created ${sectionDocs.length} sections`);

        console.log('\n✅ Sample data inserted successfully!');
        console.log(`🌐 View at: http://localhost:${process.env.PORT || 3000}/\n`);

        await mongoose.connection.close();

    } catch (error) {
        console.error('❌ Error inserting sample data:', error);
        process.exit(1);
    }
}

insertSampleData();
