from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.routers import analyze, generate
from backend.config import NVIDIA_API_KEY, REPLICATE_API_TOKEN
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Image Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(generate.router)

# Раздаем фронтенд
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    logger.info(f"Frontend mounted from {frontend_path}")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "providers": {
            "nvidia": bool(NVIDIA_API_KEY),
            "replicate": bool(REPLICATE_API_TOKEN),
            "pollinations": True
        }
    }

@app.get("/api/status")
async def status():
    return {
        "nvidia_available": bool(NVIDIA_API_KEY),
        "replicate_available": bool(REPLICATE_API_TOKEN),
        "pollinations_available": True
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)