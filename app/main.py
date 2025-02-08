from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from .worker import analyze_pr_task
from .config import Settings

app = FastAPI(title="Code Review Agent")
settings = Settings()

class PRAnalysisRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str | None = None


@app.get("/")
async def get_root():
    return {"message": "Code Review Agent API"}

@app.post("/analyze-pr")
async def analyze_pr(request: PRAnalysisRequest):
    task = analyze_pr_task.delay(
        repo_url=request.repo_url,
        pr_number=request.pr_number,
        github_token=request.github_token
    )
    return {"task_id": task.id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    result = AsyncResult(task_id)
    if result.failed():
        return {
            "task_id": task_id,
            "status": result.status,
            "error": str(result.result)
        }
    return {"task_id": task_id, "status": result.status}

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    result = AsyncResult(task_id)
    if not result.ready():
        raise HTTPException(status_code=404, detail="Task not completed")
    if result.failed():
        raise HTTPException(status_code=500, detail=str(result.result))
    return result.get()