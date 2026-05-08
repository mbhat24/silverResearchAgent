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

    # Serve static frontend files (SPA) - MUST come before router
    frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        # Mount at root so asset paths work correctly
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="static")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            # Don't catch API routes - let them fall through to the router
            if full_path.startswith("api/"):
                return None
            index_path = frontend_dist / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}

    app.include_router(router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.debug)
