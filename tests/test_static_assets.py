import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StaticAssetTests(unittest.TestCase):
    def test_app_script_uses_cache_busting_version(self):
        html = (PROJECT_ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")

        self.assertIn('/static/app.js?v=', html)


if __name__ == "__main__":
    unittest.main()
