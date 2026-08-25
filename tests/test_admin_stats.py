import unittest
from pathlib import Path
import shutil

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP_ROOT = PROJECT_ROOT / ".tmp-tests"

from app.stats import StatsStore
from app import main as main_mod


class AdminStatsHttpTests(unittest.TestCase):
    def setUp(self):
        TEST_TEMP_ROOT.mkdir(exist_ok=True)
        self.test_dir = TEST_TEMP_ROOT / self._testMethodName
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir(parents=True)
        self.store = StatsStore(self.test_dir / "stats.json")
        self._original_store = main_mod.stats_store
        main_mod.stats_store = self.store
        self.client = TestClient(main_mod.app)

    def tearDown(self):
        main_mod.stats_store = self._original_store

    def _convert(self, name="note.txt", content=b"hello markdown", cookies=None):
        return self.client.post(
            "/api/convert",
            files={"file": (name, content, "text/plain")},
            cookies=cookies or {},
        )

    def test_successful_convert_without_cookie_increments_both_and_sets_vid(self):
        response = self._convert()
        self.assertEqual(response.status_code, 200)
        self.assertIn("mdw_vid", response.cookies)
        self.assertEqual(self.store.read(), {"unique_users": 1, "documents": 1})

    def test_same_visitor_cookie_increments_documents_only(self):
        first = self._convert()
        vid = first.cookies["mdw_vid"]
        second = self._convert(cookies={"mdw_vid": vid})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(self.store.read(), {"unique_users": 1, "documents": 2})

    def test_failed_convert_does_not_count(self):
        response = self.client.post(
            "/api/convert",
            files={"file": ("virus.exe", b"xx", "application/octet-stream")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.store.read(), {"unique_users": 0, "documents": 0})

    def test_wrong_password_is_401_without_admin_cookie(self):
        response = self.client.post("/admin/login", json={"password": "nope"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "密码错误")
        self.assertNotIn("mdw_admin", response.cookies)

    def test_login_then_stats_returns_counts(self):
        self._convert()
        login = self.client.post("/admin/login", json={"password": "holmes@d920167"})
        self.assertEqual(login.status_code, 200)
        self.assertIn("mdw_admin", login.cookies)
        stats = self.client.get("/api/admin/stats")
        self.assertEqual(stats.status_code, 200)
        self.assertEqual(stats.json(), {"unique_users": 1, "documents": 1})

    def test_stats_without_session_is_401(self):
        response = self.client.get("/api/admin/stats")
        self.assertEqual(response.status_code, 401)

    def test_stats_write_failure_does_not_fail_convert(self):
        class BrokenStore:
            def record_conversion(self, visitor_id):
                raise OSError("disk full")

        main_mod.stats_store = BrokenStore()
        response = self._convert()
        self.assertEqual(response.status_code, 200)
        self.assertIn("markdown", response.json())


if __name__ == "__main__":
    unittest.main()
