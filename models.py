from pydantic import BaseModel, Field, field_validator, ValidationError


class NoteCreate(BaseModel):
    text: str = Field(max_length=10_000)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text must not be empty")
        return v

class NoteUpdate(BaseModel):
    text: str = Field(max_length=10_000)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Text must not be empty")
        return v

class Note(BaseModel):
    id: int
    text: str
    created_at: str

