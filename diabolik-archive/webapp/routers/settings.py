import os
import subprocess
import time
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

try:
    from ..database import get_stats, DB_PATH, count_albi
except ImportError:
    from database import get_stats, DB_PATH, count_albi

router = APIRouter(prefix="/api/settings", tags=["settings"])

_refresh_process = None
_refresh_started_at = None
_refresh_albi_before = 0
_refresh_albi_after = 0
_refresh_completed = False
_refresh_error = None

SCRAPER_DIR = os.path.join(os.path.dirname(__file__), "..", "..")
SCRAPER_PATH = os.path.join(SCRAPER_DIR, "scraper.py")


@router.get("/status")
def api_status():
    stats = get_stats()
    return stats


@router.post("/refresh")
def api_refresh():
    global _refresh_process, _refresh_started_at, _refresh_albi_before
    global _refresh_albi_after, _refresh_completed, _refresh_error

    if _refresh_process is not None and _refresh_process.poll() is None:
        return JSONResponse(
            status_code=409,
            content={"detail": "Un refresh è già in corso", "pid": _refresh_process.pid},
        )

    _refresh_albi_before = count_albi()
    _refresh_albi_after = 0
    _refresh_completed = False
    _refresh_error = None
    _refresh_started_at = datetime.now().isoformat()

    try:
        _refresh_process = subprocess.Popen(
            ["python", SCRAPER_PATH],
            cwd=SCRAPER_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        _refresh_error = str(e)
        raise HTTPException(status_code=500, detail=f"Errore avvio scraper: {e}")

    return {"status": "avviato", "pid": _refresh_process.pid}


@router.get("/refresh/status")
def api_refresh_status():
    global _refresh_process, _refresh_started_at, _refresh_albi_before
    global _refresh_albi_after, _refresh_completed, _refresh_error

    if _refresh_process is None:
        return {"in_corso": False}

    rc = _refresh_process.poll()

    if rc is None:
        return {
            "in_corso": True,
            "pid": _refresh_process.pid,
            "avviato_alle": _refresh_started_at,
        }

    if not _refresh_completed:
        _refresh_albi_after = count_albi()
        _refresh_completed = True

    albi_aggiunti = _refresh_albi_after - _refresh_albi_before

    return {
        "in_corso": False,
        "pid": _refresh_process.pid,
        "avviato_alle": _refresh_started_at,
        "albi_aggiunti": albi_aggiunti if rc == 0 else 0,
        "errore": _refresh_error if rc != 0 else None,
    }


@router.get("/backup")
def api_backup():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=404, detail="Database non trovato")

    today = datetime.now().strftime("%Y%m%d")
    filename = f"diabolikbackup{today}.db"

    return FileResponse(
        path=DB_PATH,
        filename=filename,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
