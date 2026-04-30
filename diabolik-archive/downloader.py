import os
from pathlib import Path

import requests

from config import COVERS_DIR, REQUEST_TIMEOUT, USER_AGENT


def download_cover(url: str, year: str | None, slug: str) -> tuple[str | None, bool]:
    if not url:
        return None, False

    year_dir = year if year else "sconosciuto"
    target_dir = Path(COVERS_DIR) / year_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = _guess_ext(url)
    filename = f"{slug}{ext}"
    filepath = target_dir / filename

    if filepath.exists():
        return str(filepath), True

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        filepath.write_bytes(resp.content)
        return str(filepath), False
    except Exception:
        return None, False


def _guess_ext(url: str) -> str:
    path = url.split("?")[0]
    _, ext = os.path.splitext(path)
    if ext and len(ext) <= 5:
        return ext.lower()
    return ".jpg"
