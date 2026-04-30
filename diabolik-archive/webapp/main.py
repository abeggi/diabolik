import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:
    from .database import init_webapp_db
    from .routers import albi, userdata, settings
except ImportError:
    from database import init_webapp_db
    from routers import albi, userdata, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_webapp_db()
    yield


app = FastAPI(title="Diabolik Archive", version="1.0.0", lifespan=lifespan)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COVERS_DIR = os.path.join(BASE_DIR, "..", "covers")
STATIC_DIR = os.path.join(BASE_DIR, "static")


app.mount("/covers", StaticFiles(directory=COVERS_DIR), name="covers")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(albi.router)
app.include_router(userdata.router)
app.include_router(settings.router)


@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/albo/{slug}")
def albo_page(slug: str):
    return FileResponse(os.path.join(STATIC_DIR, "albo.html"))


@app.get("/impostazioni")
def settings_page():
    return FileResponse(os.path.join(STATIC_DIR, "settings.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
