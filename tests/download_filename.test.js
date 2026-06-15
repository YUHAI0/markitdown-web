const assert = require("assert");
const { markdownDownloadName } = require("../app/static/app.js");

assert.strictEqual(markdownDownloadName("report.pdf"), "report.md");
assert.strictEqual(markdownDownloadName("archive.v1.docx"), "archive.v1.md");
assert.strictEqual(markdownDownloadName("README"), "README.md");
assert.strictEqual(markdownDownloadName(".env"), ".env.md");
assert.strictEqual(markdownDownloadName(""), "converted.md");

console.log("download filename tests passed");
