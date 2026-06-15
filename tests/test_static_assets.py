import unittest
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def css_block(css, selector):
    match = re.search(rf"(?m)^{re.escape(selector)}\s*\{{(?P<body>.*?)\n\}}", css, re.S)
    if not match:
        raise AssertionError(f"{selector} block should exist")
    return match.group("body")


def css_blocks_containing(css, selector):
    return [
        match.group("body")
        for match in re.finditer(r"(?m)^[^{]+\{\s*(?P<body>.*?)\n\}", css, re.S)
        if selector in match.group(0).split("{", 1)[0]
    ]


class StaticAssetTests(unittest.TestCase):
    def test_app_script_uses_cache_busting_version(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('/static/app.js?v=', html)

    def test_footer_links_to_markitdown_project(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("\u672c\u7ad9\u70b9\u6765\u6e90\u4e8e markitdown \u9879\u76ee", html)
        self.assertIn("https://github.com/microsoft/markitdown", html)

    def test_footer_links_to_api_document_with_agent_hint(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('href="/api.md"', html)
        self.assertIn("\u53ef\u4ee5\u628a /api.md \u53d1\u7ed9 Agent", html)
        self.assertIn("Agent", html)

    def test_google_analytics_tag_is_present(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("https://www.googletagmanager.com/gtag/js?id=G-B6SVPJRB5M", html)
        self.assertIn("gtag('config', 'G-B6SVPJRB5M');", html)

    def test_homepage_uses_chinese_document_title_and_heading(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        chinese_title = "\u6587\u6863\u8f6c Markdown"

        self.assertIn(f"<title>{chinese_title}</title>", html)
        self.assertIn('<p class="eyebrow">Document to Markdown</p>', html)
        self.assertIn(f'<h1 id="page-title">{chinese_title}</h1>', html)
        self.assertNotIn("markitdown Web", html)

    def test_result_panel_has_raw_and_preview_modes(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('id="raw-view-button"', html)
        self.assertIn('data-view="raw"', html)
        self.assertIn('id="raw-view-button" type="button" data-view="raw" aria-pressed="true"', html)
        self.assertIn('id="preview-view-button"', html)
        self.assertIn('data-view="preview"', html)
        self.assertIn('id="preview-view-button" type="button" data-view="preview" aria-pressed="false"', html)
        self.assertIn('id="markdown-output" spellcheck="false" readonly', html)
        self.assertIn('id="markdown-preview" hidden aria-live="polite"', html)
        self.assertIn("/static/vendor/marked.min.js", html)
        self.assertIn("/static/vendor/purify.min.js", html)

    def test_status_text_is_visually_hidden(self):
        css = (PROJECT_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")

        status_css = css_block(css, ".status")

        self.assertIn("position: absolute;", status_css)
        self.assertIn("clip-path: inset(50%);", status_css)

    def test_preview_scrolls_inside_fixed_result_body(self):
        css = (PROJECT_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
        workspace_css = css_block(css, ".workspace")
        output_body_css = css_block(css, ".output-body")
        output_panel_blocks = "\n".join(css_blocks_containing(css, ".output-panel"))
        markdown_preview_blocks = "\n".join(css_blocks_containing(css, ".markdown-preview"))

        self.assertIn("height: 100%;", workspace_css)
        self.assertIn("grid-template-rows: auto minmax(0, 1fr);", output_panel_blocks)
        self.assertIn("overflow: hidden;", output_panel_blocks)
        self.assertIn("overflow: hidden;", output_body_css)
        self.assertIn("contain: size layout;", output_body_css)
        self.assertIn("height: 100%;", markdown_preview_blocks)
        self.assertIn("overflow: auto;", markdown_preview_blocks)

    def test_result_panel_has_conversion_progress_bar(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        css = (PROJECT_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
        js = (PROJECT_ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="conversion-progress"', html)
        self.assertIn('role="progressbar"', html)
        self.assertIn('aria-label="\u89e3\u6790\u8fdb\u5ea6"', html)
        self.assertIn(".conversion-progress.is-active", css)
        self.assertIn("@keyframes progress-slide", css)
        self.assertIn("setProgress(true)", js)
        self.assertIn("setProgress(false)", js)

    def test_copy_button_has_toast_feedback(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
        css = (PROJECT_ROOT / "app" / "static" / "styles.css").read_text(encoding="utf-8")
        js = (PROJECT_ROOT / "app" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="copy-toast"', html)
        self.assertIn('role="status"', html)
        self.assertIn("\u5df2\u590d\u5236", html)
        self.assertIn(".copy-toast", css)
        self.assertIn(".copy-toast.is-visible", css)
        self.assertIn("showCopyToast()", js)
        self.assertIn("copyToastTimer", js)

    def test_site_icon_uses_resource_icon(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('<link rel="icon" type="image/png" href="/resources/icon.png">', html)
        self.assertTrue((PROJECT_ROOT / "resources" / "icon.png").is_file())

    def test_text_resource_files_exist(self):
        for filename in ("api.md", "llm.txt", "llm-full.txt", "robots.txt"):
            path = PROJECT_ROOT / "resources" / filename
            self.assertTrue(path.is_file(), f"{filename} should exist")

        api = (PROJECT_ROOT / "resources" / "api.md").read_text(encoding="utf-8")
        llm = (PROJECT_ROOT / "resources" / "llm.txt").read_text(encoding="utf-8")
        llm_full = (PROJECT_ROOT / "resources" / "llm-full.txt").read_text(encoding="utf-8")
        robots = (PROJECT_ROOT / "resources" / "robots.txt").read_text(encoding="utf-8")

        self.assertIn("POST /api/convert", api)
        self.assertIn("# \u6587\u6863\u8f6c Markdown", llm)
        self.assertIn("https://github.com/microsoft/markitdown", llm_full)
        self.assertIn("Allow: /api.md", robots)
        self.assertIn("Allow: /llm.txt", robots)

    def test_public_site_copy_uses_lowercase_markitdown(self):
        files = [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "app" / "static" / "index.html",
            PROJECT_ROOT / "resources" / "llm.txt",
            PROJECT_ROOT / "resources" / "llm-full.txt",
        ]

        for path in files:
            self.assertNotIn("MarkItDown", path.read_text(encoding="utf-8"), str(path))


if __name__ == "__main__":
    unittest.main()
