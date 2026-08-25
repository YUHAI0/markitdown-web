import time
import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.admin_auth import (
    ADMIN_PASSWORD,
    issue_session_token,
    is_valid_session_token,
    verify_password,
)


class AdminAuthTests(unittest.TestCase):
    def test_password_matches_exact_value(self):
        self.assertTrue(verify_password(ADMIN_PASSWORD))
        self.assertTrue(verify_password("holmes@d920167"))
        self.assertFalse(verify_password("wrong"))
        self.assertFalse(verify_password(""))

    def test_issued_token_is_valid(self):
        token = issue_session_token()
        self.assertRegex(token, r"^[0-9]+\.[0-9a-f]{64}$")
        self.assertTrue(is_valid_session_token(token))

    def test_tampered_or_missing_token_is_invalid(self):
        token = issue_session_token()
        expiry, sig = token.split(".", 1)
        self.assertFalse(is_valid_session_token(None))
        self.assertFalse(is_valid_session_token(""))
        self.assertFalse(is_valid_session_token(f"{expiry}.{'0' * 64}"))
        self.assertFalse(is_valid_session_token("not-a-token"))

    def test_expired_token_is_invalid(self):
        past = str(int(time.time()) - 10)
        token = issue_session_token()
        _, sig = token.split(".", 1)
        self.assertFalse(is_valid_session_token(f"{past}.{sig}"))


if __name__ == "__main__":
    unittest.main()
