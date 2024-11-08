import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.router import router

# Initialize the FastAPI app
app = FastAPI(
    title="Shoppy",
    description="Fetch and curate products by EAN code",
    version="v0.0.1",
    contact={
        "name": "David Brawand",
        "email": "dbrawand@gmail.net",
        }
    )

# Mount static files
app_dir = os.path.dirname(__file__)
static_dir = os.path.join(app_dir, "static")
app.mount(f"/static", StaticFiles(directory=Path(static_dir)), name="static")

# mount the API routes
app.include_router(router)