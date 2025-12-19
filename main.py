from fastapi import FastAPI

from api import router as api_router
from views import router as views_router

from db_orm import engine
from orm_models import Base

app = FastAPI(title="Notes App")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)



app.include_router(views_router)
app.include_router(api_router)
