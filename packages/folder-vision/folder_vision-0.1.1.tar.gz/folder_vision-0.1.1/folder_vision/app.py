from fastapi import FastAPI
from . import __version__

app = FastAPI(title="Folder Vision Demo", version=__version__)


@app.get("/")
async def root():
    return {"message": "Hello, Folder Vision!"}


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok", "version": __version__}
