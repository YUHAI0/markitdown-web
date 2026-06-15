import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
TEST_TEMP_ROOT = PROJECT_ROOT / ".tmp-tests"

from app.conversion import (
    MAX_UPLOAD_BYTES,
    ConversionError,
    convert_file_to_markdown,
    is_allowed_filename,
    save_upload_bytes,
    secure_upload_name,
)


class FakeResult:
    def __init__(self, text_content):
        self.text_content = text_content


class FakeMarkItDown:
    def __init__(self, result, has_convert_local=False):
        self.result = result
        self.seen_path = None
        if has_convert_local:
            self.convert_local = self._convert_local

    def convert(self, path):
        self.seen_path = path
        return self.result

    def _convert_local(self, path):
        self.seen_path = path
        return self.result


class ConversionTests(unittest.TestCase):
    def setUp(self):
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        self.test_dir = TEST_TEMP_ROOT / self._testMethodName
        self.test_dir.mkdir(exist_ok=True)

    def test_accepts_common_markitdown_file_extensions(self):
        self.assertTrue(is_allowed_filename("report.pdf"))
        self.assertTrue(is_allowed_filename("notes.docx"))
        self.assertTrue(is_allowed_filename("slides.pptx"))
        self.assertTrue(is_allowed_filename("table.xlsx"))
        self.assertTrue(is_allowed_filename("page.html"))
        self.assertTrue(is_allowed_filename("data.json"))
        self.assertTrue(is_allowed_filename("archive.zip"))

    def test_rejects_unknown_or_missing_extension(self):
        self.assertFalse(is_allowed_filename("program.exe"))
        self.assertFalse(is_allowed_filename("README"))

    def test_secure_upload_name_strips_path_parts(self):
        self.assertEqual(secure_upload_name("../secret.pdf"), "secret.pdf")
        self.assertEqual(secure_upload_name(r"C:\tmp\report.docx"), "report.docx")

    def test_save_upload_bytes_rejects_oversized_content(self):
        with self.assertRaises(ConversionError) as raised:
            save_upload_bytes("large.pdf", b"x" * (MAX_UPLOAD_BYTES + 1), self.test_dir)

        self.assertIn("50MB", str(raised.exception))

    def test_convert_file_to_markdown_uses_text_content_attribute(self):
        path = self.test_dir / "sample.txt"
        path.write_text("hello", encoding="utf-8")
        markitdown = FakeMarkItDown(FakeResult("# Converted"), has_convert_local=True)

        markdown = convert_file_to_markdown(path, markitdown)

        self.assertEqual(markdown, "# Converted")
        self.assertEqual(markitdown.seen_path, path)

    def test_convert_file_to_markdown_rejects_empty_result(self):
        path = self.test_dir / "sample.txt"
        path.write_text("", encoding="utf-8")
        markitdown = FakeMarkItDown(FakeResult(""))

        with self.assertRaises(ConversionError) as raised:
            convert_file_to_markdown(path, markitdown)

        self.assertIn("没有提取到 Markdown 内容", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
