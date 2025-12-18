from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException

from db import get_conn
from models import Note, NoteCreate

router = APIRouter()


@router.get("/notes", response_model=List[Note])
def list_notes() -> List[Note]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    return [Note(**dict(r)) for r in rows]


@router.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate) -> Note:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (payload.text, created_at),
        )
        note_id = cur.lastrowid
        row = conn.execute(
            "SELECT id, text, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
    return Note(**dict(row))


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
