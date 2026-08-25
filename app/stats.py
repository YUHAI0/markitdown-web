from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4


def parse_visitor_id(value: str | None) -> str | None:
    if not value:
        return None
    try:
        UUID(value)
    except ValueError:
        return None
    return value


@dataclass(frozen=True)
class RecordResult:
    unique_users: int
    documents: int
    should_set_cookie: bool
    visitor_id: str


@contextmanager
def _exclusive_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "a+b")
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            if handle.read(1) == b"":
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


class StatsStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.lock_path = self.path.with_name(self.path.name + ".lock")

    def read(self) -> dict:
        with _exclusive_lock(self.lock_path):
            return self._load_unlocked()

    def record_conversion(self, visitor_id: str | None) -> RecordResult:
        valid = parse_visitor_id(visitor_id)
        should_set_cookie = valid is None
        new_id = valid or str(uuid4())

        with _exclusive_lock(self.lock_path):
            data = self._load_unlocked()
            data["documents"] = data["documents"] + 1
            if should_set_cookie:
                data["unique_users"] = data["unique_users"] + 1
            self._save_unlocked(data)

        return RecordResult(
            unique_users=data["unique_users"],
            documents=data["documents"],
            should_set_cookie=should_set_cookie,
            visitor_id=new_id,
        )

    def _load_unlocked(self) -> dict:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return {
                "unique_users": int(raw.get("unique_users") or 0),
                "documents": int(raw.get("documents") or 0),
            }
        except (FileNotFoundError, OSError, json.JSONDecodeError, TypeError, ValueError):
            return {"unique_users": 0, "documents": 0}

    def _save_unlocked(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {
                "unique_users": int(data["unique_users"]),
                "documents": int(data["documents"]),
            },
            ensure_ascii=False,
        )
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(self.path)
