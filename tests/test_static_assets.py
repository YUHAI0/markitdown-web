import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StaticAssetTests(unittest.TestCase):
    def test_app_script_uses_cache_busting_version(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('/static/app.js?v=', html)

    def test_footer_links_to_markitdown_project(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("本站点来源于 MarkItDown 项目", html)
        self.assertIn("https://github.com/microsoft/markitdown", html)

    def test_google_analytics_tag_is_present(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn("https://www.googletagmanager.com/gtag/js?id=G-B6SVPJRB5M", html)
        self.assertIn("gtag('config', 'G-B6SVPJRB5M');", html)


if __name__ == "__main__":
    unittest.main()
