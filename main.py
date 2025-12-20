from fastapi import FastAPI

from dotenv import load_dotenv
load_dotenv()

from api import router as api_router
from views import router as views_router

from db_orm import engine
from orm_models import Base, NoteORM
from sqladmin import Admin, ModelView

app = FastAPI(title="Notes App")

from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(views_router)
app.include_router(api_router)


class NoteAdmin(ModelView, model=NoteORM):
    column_list = [NoteORM.id, NoteORM.text, NoteORM.created_at]
    form_columns = ["text"]


admin = Admin(app, engine)
admin.add_view(NoteAdmin)
