from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from db import get_conn

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home() -> str:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, text, created_at FROM notes ORDER BY id DESC"
        ).fetchall()

    items = ""
    for r in rows:
        items += f"""
        <li>
            {r['text']}
            <a href="/edit/{r['id']}">edit</a>
            <form method="post" action="/delete/{r['id']}" style="display:inline">
                <button type="submit">delete</button>
            </form>
        </li>
        """


    return f"""
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

@router.get("/edit/{note_id}", response_class=HTMLResponse)
def edit_note_page(note_id: int) -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, text, created_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")

    text = row["text"]
    return f"""
    <html>
        <body>
            <h1>Edit note #{note_id}</h1>

            <form method="post" action="/edit/{note_id}">
                <textarea name="text">{text}</textarea><br>
                <button type="submit">Save</button>
                <a href="/">Cancel</a>
            </form>
        </body>
    </html>
    """


@router.post("/edit/{note_id}")
def edit_note_save(note_id: int, text: str = Form(...)):
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE notes SET text = ? WHERE id = ?",
            (text, note_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")

    return RedirectResponse("/", status_code=303)


@router.post("/add")
def add_note_form(text: str = Form(...)):
    created_at = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notes (text, created_at) VALUES (?, ?)",
            (text, created_at),
        )
    return RedirectResponse("/", status_code=303)


@router.post("/delete/{note_id}")
def delete_note_form(note_id: int):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found")
    return RedirectResponse("/", status_code=303)
