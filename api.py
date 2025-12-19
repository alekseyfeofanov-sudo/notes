from datetime import timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from db_orm import get_session
from models import Note, NoteCreate, NoteUpdate
from orm_models import NoteORM

router = APIRouter()


def to_note(n: NoteORM) -> Note:
    # created_at у нас datetime с tz; в API отдаём строку ISO
    created_iso = n.created_at.astimezone(timezone.utc).isoformat()
    return Note(id=n.id, text=n.text, created_at=created_iso)


@router.get("/notes", response_model=List[Note])
def list_notes(db: Session = Depends(get_session)) -> List[Note]:
    stmt = select(NoteORM).order_by(NoteORM.id.desc())
    notes = db.execute(stmt).scalars().all()
    return [to_note(n) for n in notes]


@router.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_session)) -> Note:
    n = NoteORM(text=payload.text, created_at=NoteORM.now_utc())
    db.add(n)
    db.commit()
    db.refresh(n)
    return to_note(n)


@router.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_session)) -> Note:
    n = db.get(NoteORM, note_id)
    if n is None:
        raise HTTPException(status_code=404, detail="Note not found")

    n.text = payload.text
    db.commit()
    db.refresh(n)
    return to_note(n)


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_session)) -> None:
    n = db.get(NoteORM, note_id)
    if n is None:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(n)
    db.commit()
    # для 204 ничего не возвращаем
