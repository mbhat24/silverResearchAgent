import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .api.routes import router
from .config import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Silver Research Agent",
        description="AI-powered deep research agent for silver markets - worldwide & India",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    # Serve static frontend files
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dist), html=True), name="static")

        @app.get("/")
        async def serve_index():
            index_path = frontend_dist / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.debug)
