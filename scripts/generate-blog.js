const fs = require('fs');
const path = require('path');

const contentDir = path.join(__dirname, '../content');
const blogDir = path.join(__dirname, '../blog');
const templatePath = path.join(blogDir, 'template.html');

const template = fs.readFileSync(templatePath, 'utf-8');

function parseFrontmatter(content) {
    const match = content.match(/^---\r?\n([\s\S]+?)\r?\n---\r?\n([\s\S]*)$/);
    if (!match) return { data: {}, content };
    
    const data = {};
    match[1].split('\n').forEach(line => {
        const [key, ...value] = line.split(':');
        if (key && value) data[key.trim()] = value.join(':').trim();
    });
    
    return { data, body: match[2] };
}

// Minimal Markdown to HTML converter (for demo purposes)
function simpleMarkdown(md) {
    return md
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^> "(.*)"/gim, '<blockquote>$1</blockquote>')
        .replace(/^\d\. (.*$)/gim, '<li>$1</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^/, '<p>')
        .replace(/$/, '</p>');
}

const files = fs.readdirSync(contentDir).filter(f => f.endsWith('.md'));

files.forEach(file => {
    const filePath = path.join(contentDir, file);
    const rawContent = fs.readFileSync(filePath, 'utf-8');
    const { data, body } = parseFrontmatter(rawContent);
    
    const htmlContent = simpleMarkdown(body);
    const slug = file.replace('.md', '');
    
    let output = template
        .replace(/{{TITLE}}/g, data.title || 'Insight')
        .replace(/{{DESCRIPTION}}/g, data.excerpt || '')
        .replace(/{{DATE}}/g, data.date || '')
        .replace(/{{CATEGORY}}/g, data.category || 'Insight')
        .replace(/{{IMAGE}}/g, data.image || '')
        .replace(/{{CONTENT}}/g, htmlContent)
        .replace(/{{CANONICAL_URL}}/g, `https://anantawealth.com/blog/${slug}.html`);
    
    fs.writeFileSync(path.join(blogDir, `${slug}.html`), output);
    console.log(`Generated: ${slug}.html`);
});
