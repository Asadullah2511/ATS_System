from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import shutil
from pathlib import Path
import json

from src.graphs.ats_graph import create_ats_graph
from src.utils.logger import setup_logger

app = FastAPI(
    title="ATS System API",
    description="Applicant Tracking System powered by LangGraph",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = setup_logger("ats_api")

UPLOAD_DIR = Path("data/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class JobDescription(BaseModel):
    job_id: str
    description: str


class EvaluationResponse(BaseModel):
    status: str
    evaluation: dict
    error: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "ATS System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "evaluate": "/evaluate",
            "batch_evaluate": "/batch-evaluate"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ATS System"}


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_candidate(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    job_id: str = Form(...)
):
    try:
        file_path = UPLOAD_DIR / resume.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        logger.info(f"Processing resume: {resume.filename} for job: {job_id}")

        graph = create_ats_graph()

        initial_state = {
            "messages": [],
            "resume_file_path": str(file_path),
            "job_description": job_description,
            "job_id": job_id
        }

        result = graph.invoke(initial_state)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        logger.info(f"Evaluation completed for {resume.filename}")

        return EvaluationResponse(
            status="success",
            evaluation=result.get("final_evaluation", {})
        )

    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if file_path.exists():
            file_path.unlink()


@app.post("/batch-evaluate")
async def batch_evaluate(
    resumes: list[UploadFile] = File(...),
    job_description: str = Form(...),
    job_id: str = Form(...)
):
    results = []

    for resume in resumes:
        try:
            file_path = UPLOAD_DIR / resume.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(resume.file, buffer)

            logger.info(f"Processing resume: {resume.filename}")

            graph = create_ats_graph()

            initial_state = {
                "messages": [],
                "resume_file_path": str(file_path),
                "job_description": job_description,
                "job_id": job_id
            }

            result = graph.invoke(initial_state)

            results.append({
                "filename": resume.filename,
                "status": "success" if not result.get("error") else "error",
                "evaluation": result.get("final_evaluation", {}),
                "error": result.get("error")
            })

        except Exception as e:
            logger.error(f"Error processing {resume.filename}: {str(e)}")
            results.append({
                "filename": resume.filename,
                "status": "error",
                "error": str(e)
            })

        finally:
            if file_path.exists():
                file_path.unlink()

    ranked_results = sorted(
        [r for r in results if r["status"] == "success"],
        key=lambda x: x["evaluation"].get("scores", {}).get("overall_score", 0),
        reverse=True
    )

    return {
        "status": "completed",
        "total": len(resumes),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results,
        "ranked_candidates": ranked_results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
