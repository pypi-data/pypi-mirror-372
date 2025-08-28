"""
FastAPI server setup for Broadie API.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from broadie.config.settings import BroadieSettings

from .routes import router as api_router
from .websocket import router as ws_router


def create_app(agent=None, settings=None) -> FastAPI:
    """Create and configure the FastAPI application."""
    if settings is None:
        settings = BroadieSettings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.state.settings = settings
    app.state.agent = agent

    # CORS: allow all origins/headers/methods to support local dev on different ports
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # cannot use "*" with credentials; set to False for permissive CORS
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = settings.api_prefix or ""
    app.include_router(api_router, prefix=prefix)
    app.include_router(ws_router, prefix=prefix)
    # Serve the frontend UI (SPA) from root
    static_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, "static", "ui")
    )
    assets_dir = os.path.join(static_dir, "assets")
    # Mount built assets (JS/CSS/images) at /assets
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    # Mount SPA at root, ensuring API under /api remains unaffected
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="spa")
    # Optional: keep /ui path serving the SPA for backward compatibility
    app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")
    return app


app = create_app()

if __name__ == "__main__":  # pragma: no cover
    settings = BroadieSettings()
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
