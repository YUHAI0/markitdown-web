from pathlib import Path, PureWindowsPath
from uuid import uuid4


MAX_UPLOAD_BYTES = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".csv",
    ".doc",
    ".docx",
    ".epub",
    ".gif",
    ".htm",
    ".html",
    ".jpeg",
    ".jpg",
    ".json",
    ".m4a",
    ".md",
    ".mp3",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".tiff",
    ".txt",
    ".wav",
    ".xls",
    ".xlsx",
    ".xml",
    ".zip",
}


class ConversionError(Exception):
    pass


def secure_upload_name(filename: str) -> str:
    normalized = filename.replace("\\", "/")
    name = Path(PureWindowsPath(normalized).name).name
    return name or "upload.bin"


def is_allowed_filename(filename: str) -> bool:
    suffix = Path(secure_upload_name(filename)).suffix.lower()
    return suffix in ALLOWED_EXTENSIONS


def save_upload_bytes(filename: str, content: bytes, upload_dir: Path) -> Path:
    if len(content) > MAX_UPLOAD_BYTES:
        raise ConversionError("文件不能超过 50MB。")

    safe_name = secure_upload_name(filename)
    if not is_allowed_filename(safe_name):
        raise ConversionError("暂不支持这个文件类型。请上传 PDF、Office、HTML、图片、音频、CSV、JSON、XML、ZIP 或文本文件。")

    upload_dir.mkdir(parents=True, exist_ok=True)
    target = upload_dir / f"{uuid4().hex}-{safe_name}"
    target.write_bytes(content)
    return target


def convert_file_to_markdown(path: Path, markitdown) -> str:
    try:
        convert = getattr(markitdown, "convert_local", markitdown.convert)
        result = convert(path)
    except Exception as exc:
        raise ConversionError(f"转换失败：{exc}") from exc

    markdown = getattr(result, "text_content", None)
    if markdown is None:
        markdown = str(result)

    markdown = markdown.strip()
    if not markdown:
        raise ConversionError("没有提取到 Markdown 内容。")

    return markdown
