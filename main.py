from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import List

from fastapi import FastAPI, HTTPException, Response, Request
from pydantic import BaseModel, Field

from fastapi import Form
from fastapi.responses import HTMLResponse, RedirectResponse

DB_PATH = "notes.db"

app = FastAPI(title="Notes App")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


@app.on_event("startup")
def on_startup() -> None:
    init_db()


class NoteCreate(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class Note(BaseModel):
    id: int
    text: str
    created_at: str


@app.get("/notes", response_model=List[Note])
def list_notes() -> List[Note]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC"
        ).fetchall()
    return [Note(**dict(r)) for r in rows]


@app.post("/notes", response_model=Note, status_code=201)
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


@app.delete("/notes/{note_id}", status_code=204, response_class=Response)
def delete_note(note_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
    # НИЧЕГО НЕ ВОЗВРАЩАЕМ для 204


from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC"
        ).fetchall()

    items = ""
    for r in rows:
        items += f"""
        <li>
            {r['text']}
            <form method="post" action="/delete/{r['id']}" style="display:inline">
                <button type="submit">delete</button>
            </form>
        </li>
        """

    html = f"""
    <html>
        <body>
            <h1>Notes</h1>

            <form method="post" action="/add">
                <textarea name="text"></textarea><br>
                <button type="submit">Add</button>
            </form>

            <ul>
                {items}
            </ul>
        </body>
    </html>
    """
    return html


@app.post("/add")
def add_note_form(text: str = Form(...)):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (text, created_at),
        )
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{note_id}")
def delete_note_form(note_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return RedirectResponse("/", status_code=303)
