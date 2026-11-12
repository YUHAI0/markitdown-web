import logging
import shutil
import tempfile
from pathlib import Path

from fastapi import Cookie, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown
from pydantic import BaseModel
from starlette.responses import Response

from .admin_auth import (
    ADMIN_COOKIE,
    clear_session_cookie,
    is_valid_session_token,
    set_session_cookie,
    verify_password,
)
from .conversion import ConversionError, convert_file_to_markdown, save_upload_bytes
from .stats import StatsStore, writable_stats_path


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR.parent / "public"
STATIC_DIR = PUBLIC_DIR / "static"
RESOURCE_DIR = BASE_DIR.parent / "resources"
PAGE_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=0, must-revalidate",
    "CDN-Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400",
}
TEXT_CACHE_HEADERS = {
    "Cache-Control": "public, max-age=3600",
    "CDN-Cache-Control": "public, s-maxage=86400, stale-while-revalidate=604800",
}
UPLOAD_DIR = Path(tempfile.gettempdir()) / "markitdown-web-uploads"
STATS_PATH = BASE_DIR.parent / "data" / "stats.json"
VISITOR_COOKIE = "mdw_vid"
VISITOR_COOKIE_MAX_AGE = 31536000

logger = logging.getLogger(__name__)

app = FastAPI(title="文档转 Markdown")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/resources", StaticFiles(directory=RESOURCE_DIR), name="resources")
stats_store = StatsStore(writable_stats_path(STATS_PATH))


class AdminLoginBody(BaseModel):
    password: str


def _set_visitor_cookie(response: Response, visitor_id: str) -> None:
    response.set_cookie(
        key=VISITOR_COOKIE,
        value=visitor_id,
        max_age=VISITOR_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        path="/",
    )


@app.get("/")
def index():
    return FileResponse(PUBLIC_DIR / "index.html", headers=PAGE_CACHE_HEADERS)


@app.get("/admin")
def admin_page():
    return FileResponse(PUBLIC_DIR / "admin.html", headers=PAGE_CACHE_HEADERS)


@app.get("/llm.txt")
def llm_txt():
    return FileResponse(
        RESOURCE_DIR / "llm.txt",
        media_type="text/plain; charset=utf-8",
        headers=TEXT_CACHE_HEADERS,
    )


@app.get("/llm-full.txt")
def llm_full_txt():
    return FileResponse(
        RESOURCE_DIR / "llm-full.txt",
        media_type="text/plain; charset=utf-8",
        headers=TEXT_CACHE_HEADERS,
    )


@app.get("/api.md")
def api_md():
    return FileResponse(
        RESOURCE_DIR / "api.md",
        media_type="text/plain; charset=utf-8",
        headers=TEXT_CACHE_HEADERS,
    )


@app.get("/robots.txt")
def robots_txt():
    return FileResponse(
        RESOURCE_DIR / "robots.txt",
        media_type="text/plain; charset=utf-8",
        headers=TEXT_CACHE_HEADERS,
    )


@app.post("/admin/login")
def admin_login(body: AdminLoginBody, response: Response):
    if not verify_password(body.password):
        raise HTTPException(status_code=401, detail="密码错误")
    set_session_cookie(response)
    return {"ok": True}


@app.post("/admin/logout")
def admin_logout(response: Response):
    clear_session_cookie(response)
    return {"ok": True}


def _admin_stats_payload(token: str | None) -> dict:
    if not is_valid_session_token(token):
        raise HTTPException(status_code=401, detail="未登录")
    try:
        return stats_store.read()
    except Exception:
        logger.exception("failed to read conversion stats")
        return {"unique_users": 0, "documents": 0}


@app.get("/admin/stats")
@app.get("/api/admin/stats")
def admin_stats(request: Request):
    return _admin_stats_payload(request.cookies.get(ADMIN_COOKIE))


@app.post("/api/convert")
async def convert(
    response: Response,
    file: UploadFile = File(...),
    mdw_vid: str | None = Cookie(default=None, alias=VISITOR_COOKIE),
):
    content = await file.read()
    saved_path = None

    try:
        saved_path = save_upload_bytes(file.filename or "upload", content, UPLOAD_DIR)
        markdown = convert_file_to_markdown(saved_path, MarkItDown())
    except ConversionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if saved_path and saved_path.exists():
            saved_path.unlink()
        if UPLOAD_DIR.exists() and not any(UPLOAD_DIR.iterdir()):
            shutil.rmtree(UPLOAD_DIR)

    try:
        result = stats_store.record_conversion(mdw_vid)
        if result.should_set_cookie:
            _set_visitor_cookie(response, result.visitor_id)
    except Exception:
        logger.exception("failed to record conversion stats")

    return {
        "filename": file.filename,
        "characters": len(markdown),
        "markdown": markdown,
    }
