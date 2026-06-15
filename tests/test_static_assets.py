import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
