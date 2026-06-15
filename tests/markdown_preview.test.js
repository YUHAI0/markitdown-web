const assert = require("assert");
const { renderMarkdownPreview } = require("../app/static/app.js");

const html = renderMarkdownPreview("# Title\n\n<script>alert('xss')</script>\n\n**Bold**");

assert.match(html, /<h1[^>]*>Title<\/h1>/);
assert.match(html, /<strong>Bold<\/strong>/);
assert.doesNotMatch(html, /<script/i);
assert.doesNotMatch(html, /alert\('xss'\)/);

console.log("markdown preview tests passed");
