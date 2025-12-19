from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from pydantic import ValidationError
import pydantic_core

from db_orm import get_session
from models import NoteCreate, NoteUpdate
from orm_models import NoteORM

router = APIRouter()

def render_error_page(title: str, error: str) -> HTMLResponse:
    safe_error = (
        error.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    html = f"""
    <html>
        <body>
            <h1>{title}</h1>
            <p style="color:red">{safe_error}</p>
            <p><a href="/">Back</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=400)



@router.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_session)) -> str:
    stmt = select(NoteORM).order_by(NoteORM.id.desc())
    notes = db.execute(stmt).scalars().all()

    items = ""
    for n in notes:
        items += f"""
        <li>
            {n.text}
            <a href="/edit/{n.id}">edit</a>
            <form method="post" action="/delete/{n.id}" style="display:inline">
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


@router.post("/add")
def add_note_form(text: str = Form(...), db: Session = Depends(get_session)):
    try:
        payload = NoteCreate(text=text)
    except (ValidationError, pydantic_core.ValidationError):
        return render_error_page("Cannot add note", "Text must not be empty")

    n = NoteORM(text=payload.text, created_at=NoteORM.now_utc())
    db.add(n)
    db.commit()
    return RedirectResponse("/", status_code=303)



@router.post("/delete/{note_id}")
def delete_note_form(note_id: int, db: Session = Depends(get_session)):
    n = db.get(NoteORM, note_id)
    if n is None:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(n)
    db.commit()
    return RedirectResponse("/", status_code=303)


@router.get("/edit/{note_id}", response_class=HTMLResponse)
def edit_note_page(note_id: int, db: Session = Depends(get_session)) -> str:
    n = db.get(NoteORM, note_id)
    if n is None:
        raise HTTPException(status_code=404, detail="Note not found")

    # Простой HTML escape для textarea, чтобы не ломать страницу
    text_escaped = (
        n.text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return f"""
    <html>
        <body>
            <h1>Edit note #{note_id}</h1>

            <form method="post" action="/edit/{note_id}">
                <textarea name="text">{text_escaped}</textarea><br>
                <button type="submit">Save</button>
                <a href="/">Cancel</a>
            </form>
        </body>
    </html>
    """


@router.post("/edit/{note_id}")
def edit_note_save(note_id: int, text: str = Form(...), db: Session = Depends(get_session)):
    try:
        payload = NoteUpdate(text=text)
    except (ValidationError, pydantic_core.ValidationError):
        return render_error_page("Cannot update note", "Text must not be empty")

    n = db.get(NoteORM, note_id)
    if n is None:
        raise HTTPException(status_code=404, detail="Note not found")

    n.text = payload.text
    db.commit()
    return RedirectResponse("/", status_code=303)



