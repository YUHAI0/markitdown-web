from __future__ import annotations

import hashlib
import hmac
import time

from starlette.responses import Response

ADMIN_PASSWORD = "holmes@d920167"
ADMIN_COOKIE = "mdw_admin"
ADMIN_COOKIE_MAX_AGE = 7 * 24 * 3600
_SECRET = hmac.new(b"mdw-admin", ADMIN_PASSWORD.encode("utf-8"), hashlib.sha256).digest()


def verify_password(password: str) -> bool:
    return hmac.compare_digest(password, ADMIN_PASSWORD)


def _sign(expiry: str) -> str:
    return hmac.new(_SECRET, expiry.encode("utf-8"), hashlib.sha256).hexdigest()


def issue_session_token() -> str:
    expiry = str(int(time.time()) + ADMIN_COOKIE_MAX_AGE)
    return f"{expiry}.{_sign(expiry)}"


def is_valid_session_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    expiry, _, signature = token.partition(".")
    if not expiry.isdigit() or len(signature) != 64:
        return False
    if int(expiry) < int(time.time()):
        return False
    expected = _sign(expiry)
    return hmac.compare_digest(signature, expected)


def set_session_cookie(response: Response) -> None:
    response.set_cookie(
        key=ADMIN_COOKIE,
        value=issue_session_token(),
        max_age=ADMIN_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(ADMIN_COOKIE, path="/")
