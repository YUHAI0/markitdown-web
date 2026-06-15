import unittest

from fastapi.testclient import TestClient

from app.main import app


class TextRoutesTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_llm_txt_is_served_at_root(self):
        response = self.client.get("/llm.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")
        self.assertIn("# \u6587\u6863\u8f6c Markdown", response.text)

    def test_llm_full_txt_is_served_at_root(self):
        response = self.client.get("/llm-full.txt")

        self.assertEqual(response.status_code, 200)
        self.assertIn("https://github.com/microsoft/markitdown", response.text)

    def test_api_md_is_served_at_root(self):
        response = self.client.get("/api.md")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/plain; charset=utf-8")
        self.assertIn("# Conversion API", response.text)
        self.assertIn("POST /api/convert", response.text)

    def test_robots_txt_is_served_at_root(self):
        response = self.client.get("/robots.txt")

        self.assertEqual(response.status_code, 200)
        self.assertIn("User-agent: *", response.text)
        self.assertIn("Allow: /llm-full.txt", response.text)


if __name__ == "__main__":
    unittest.main()
