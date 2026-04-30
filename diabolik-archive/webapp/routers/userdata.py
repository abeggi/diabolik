from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..database import (
        toggle_preferito,
        save_note,
        add_tag,
        remove_tag,
        get_all_tags,
    )
except ImportError:
    from database import (
        toggle_preferito,
        save_note,
        add_tag,
        remove_tag,
        get_all_tags,
    )

router = APIRouter(prefix="/api", tags=["userdata"])


class NoteBody(BaseModel):
    note: str


class TagBody(BaseModel):
    tag: str


@router.post("/albi/{slug}/preferito")
def api_toggle_preferito(slug: str):
    try:
        stato = toggle_preferito(slug)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"preferito": stato}


@router.post("/albi/{slug}/note")
def api_save_note(slug: str, body: NoteBody):
    try:
        save_note(slug, body.note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok"}


@router.post("/albi/{slug}/tags")
def api_add_tag(slug: str, body: TagBody):
    try:
        add_tag(slug, body.tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok"}


@router.delete("/albi/{slug}/tags/{tag}")
def api_remove_tag(slug: str, tag: str):
    try:
        remove_tag(slug, tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "ok"}


@router.get("/tags")
def api_tags():
    return get_all_tags()
