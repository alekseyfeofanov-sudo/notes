from fastapi import FastAPI

from db import init_db
from api import router as api_router
from views import router as views_router

app = FastAPI(title="Notes App")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(views_router)
app.include_router(api_router)
