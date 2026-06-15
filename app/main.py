import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from markitdown import MarkItDown

from .conversion import ConversionError, convert_file_to_markdown, save_upload_bytes


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
RESOURCE_DIR = BASE_DIR.parent / "resources"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "markitdown-web-uploads"

app = FastAPI(title="文档转 Markdown")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/resources", StaticFiles(directory=RESOURCE_DIR), name="resources")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/llm.txt")
def llm_txt():
    return FileResponse(RESOURCE_DIR / "llm.txt", media_type="text/plain; charset=utf-8")


@app.get("/llm-full.txt")
def llm_full_txt():
    return FileResponse(RESOURCE_DIR / "llm-full.txt", media_type="text/plain; charset=utf-8")


@app.get("/api.md")
def api_md():
    return FileResponse(RESOURCE_DIR / "api.md", media_type="text/plain; charset=utf-8")


@app.get("/robots.txt")
def robots_txt():
    return FileResponse(RESOURCE_DIR / "robots.txt", media_type="text/plain; charset=utf-8")


@app.post("/api/convert")
async def convert(file: UploadFile = File(...)):
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

    return {
        "filename": file.filename,
        "characters": len(markdown),
        "markdown": markdown,
    }
