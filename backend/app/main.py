"""DocAlign API — FastAPI service."""

from __future__ import annotations

import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .analyze import analyze_master_only, run_pipeline
from .config import key_pool, settings
from .groq_client import GroqError
from .models import AlignmentReport, MasterProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docalign")

app = FastAPI(title="DocAlign API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MASTER_EXTENSIONS = (".pdf", ".docx")
CHILD_EXTENSIONS = (".docx",)


async def _read(upload: UploadFile, allowed: tuple[str, ...], label: str) -> bytes:
    name = (upload.filename or "").lower()
    if not name.endswith(allowed):
        raise HTTPException(
            status_code=400,
            detail=f"{label} must be one of: {', '.join(allowed)}",
        )
    data = await upload.read()
    if not data:
        raise HTTPException(status_code=400, detail=f"{label} is empty")
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"{label} exceeds {settings.max_upload_bytes // (1024 * 1024)} MB",
        )
    return data


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": settings.groq_model,
        "groq_keys_configured": key_pool.size(),
    }


@app.post("/api/analyze/master", response_model=MasterProfile)
async def analyze_master_endpoint(master: UploadFile = File(...)) -> MasterProfile:
    data = await _read(master, MASTER_EXTENSIONS, "Master document")
    try:
        return await analyze_master_only(data, master.filename or "master")
    except GroqError as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("master analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc


@app.post("/api/analyze", response_model=AlignmentReport)
async def analyze_endpoint(
    master: UploadFile = File(...),
    child: UploadFile = File(...),
) -> AlignmentReport:
    master_data = await _read(master, MASTER_EXTENSIONS, "Master document")
    child_data = await _read(child, CHILD_EXTENSIONS, "Document to verify")
    try:
        return await run_pipeline(
            master_data,
            master.filename or "master",
            child_data,
            child.filename or "document",
        )
    except GroqError as exc:
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("analysis failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}") from exc
