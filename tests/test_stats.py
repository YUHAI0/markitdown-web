import json
import unittest
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = PROJECT_ROOT / ".tmp-tests"

from app.stats import StatsStore, parse_visitor_id


class StatsStoreTests(unittest.TestCase):
    def setUp(self):
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        self.test_dir = TEST_TEMP_ROOT / self._testMethodName
        self.test_dir.mkdir(exist_ok=True)
        self.store = StatsStore(self.test_dir / "stats.json")

    def test_parse_visitor_id_accepts_uuid_only(self):
        valid = str(uuid4())
        self.assertEqual(parse_visitor_id(valid), valid)
        self.assertIsNone(parse_visitor_id(None))
        self.assertIsNone(parse_visitor_id(""))
        self.assertIsNone(parse_visitor_id("not-a-uuid"))

    def test_missing_file_reads_as_zero(self):
        self.assertEqual(self.store.read(), {"unique_users": 0, "documents": 0})

    def test_corrupt_file_reads_as_zero(self):
        self.store.path.write_text("{nope", encoding="utf-8")
        self.assertEqual(self.store.read(), {"unique_users": 0, "documents": 0})

    def test_new_visitor_increments_both(self):
        first = self.store.record_conversion(None)
        self.assertTrue(first.should_set_cookie)
        self.assertIsNotNone(parse_visitor_id(first.visitor_id))
        self.assertEqual(first.unique_users, 1)
        self.assertEqual(first.documents, 1)
        self.assertEqual(self.store.read(), {"unique_users": 1, "documents": 1})

    def test_same_visitor_increments_documents_only(self):
        first = self.store.record_conversion(None)
        second = self.store.record_conversion(first.visitor_id)
        self.assertFalse(second.should_set_cookie)
        self.assertEqual(second.visitor_id, first.visitor_id)
        self.assertEqual(second.unique_users, 1)
        self.assertEqual(second.documents, 2)

    def test_invalid_visitor_id_counts_as_new_person(self):
        self.store.record_conversion(None)
        again = self.store.record_conversion("not-a-uuid")
        self.assertTrue(again.should_set_cookie)
        self.assertEqual(again.unique_users, 2)
        self.assertEqual(again.documents, 2)

    def test_record_persists_json(self):
        self.store.record_conversion(None)
        payload = json.loads(self.store.path.read_text(encoding="utf-8"))
        self.assertEqual(payload, {"unique_users": 1, "documents": 1})


if __name__ == "__main__":
    unittest.main()
