import asyncio
import json
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Force line-buffered stdout so agent logs appear in real time (even from threads)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Allow running from either repo root (uvicorn backend.main:app) or backend/ (uvicorn main:app).
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from backend.database import init_db, save_run, get_all_runs, get_run_by_id  # pyre-ignore[21]
from backend.models.schemas import RunRequest, FeedbackRequest  # pyre-ignore[21]
from backend.core.graph import get_compiled_graph  # pyre-ignore[21]
from backend.core.rag import get_rag_pipeline  # pyre-ignore[21]
from backend.integrations.jira_client import get_jira_stories  # pyre-ignore[21]
from backend.core.config import config  # pyre-ignore[21]

# Store active run states for SSE streaming
active_runs: Dict[str, Dict[str, Any]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and ensure output directories exist on startup."""
    await init_db()
    os.makedirs(config.TESTS_OUTPUT_DIR, exist_ok=True)
    os.makedirs(config.REPORTS_DIR, exist_ok=True)
    os.makedirs(config.SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(config.CHROMA_DB_PATH, exist_ok=True)
    yield


app = FastAPI(
    title="Sentinel-Agent API",
    description="AI-Powered Context-Aware Release Testing Agent",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/screenshots",
    StaticFiles(directory=config.SCREENSHOTS_DIR),
    name="screenshots"
)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "model": config.GROQ_MODEL}


@app.get("/api/stories")
async def get_stories():
    """Get user stories (from Jira if configured, else mock data)."""
    stories = get_jira_stories()
    return {"stories": stories, "source": "jira" if config.JIRA_SERVER else "mock"}


@app.post("/api/runs/start")
async def start_run(request: RunRequest):
    """
    Start a new test run. Returns a run_id immediately.
    The actual execution happens asynchronously via /api/runs/{run_id}/stream.
    """
    run_id = request.run_id or str(uuid.uuid4())
    story = request.story
    story_id = story.story_id or story.title[:20].replace(" ", "-").lower()

    initial_state = {
        "run_id": run_id,
        "story_id": story_id,
        "story_text": f"{story.title}\n{story.description}" + (
            f"\nAcceptance Criteria: {story.acceptance_criteria}" if story.acceptance_criteria else ""
        ),
        "story_title": story.title,
        "story_type": story.source.value,
        "parsed_requirements": {},
        "rag_context": {},
        "generated_tests": [],
        "execution_results": [],
        "regression_analysis": {},
        "report_html": "",
        "report_path": "",
        "report_filename": "",
        "agent_steps": [],
        "current_step": "initializing",
        "errors": []
    }

    active_runs[run_id] = {
        "state": initial_state,
        "status": "pending",
        "completed": False
    }

    # Start the agent pipeline in the background
    asyncio.create_task(_execute_run(run_id, initial_state))

    return {"run_id": run_id, "status": "started", "message": "Run initiated. Stream events at /api/runs/{run_id}/stream"}


async def _execute_run(run_id: str, initial_state: Dict[str, Any]):
    """Execute the LangGraph pipeline in a thread pool (sync agents)."""
    try:
        active_runs[run_id]["status"] = "running"
        print(f"\n{'#'*60}")
        print(f"### PIPELINE STARTED: Run {run_id}")
        print(f"### Story: {initial_state.get('story_title', 'N/A')}")
        print(f"{'#'*60}")

        graph = get_compiled_graph()

        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            None,
            lambda: graph.invoke(initial_state)
        )

        execution_results = final_state.get("execution_results", [])
        total = len(execution_results)
        passed = sum(1 for r in execution_results if r["status"] == "passed")
        failed = sum(1 for r in execution_results if r["status"] in ("failed", "error"))

        active_runs[run_id]["state"] = final_state
        active_runs[run_id]["status"] = "completed"
        active_runs[run_id]["completed"] = True

        print(f"\n{'#'*60}")
        print(f"### PIPELINE COMPLETED: Run {run_id}")
        print(f"### Results: {passed}/{total} passed, {failed} failed")
        print(f"### Report: {final_state.get('report_filename', 'N/A')}")
        print(f"{'#'*60}\n")

        await save_run({
            "run_id": run_id,
            "story_id": final_state["story_id"],
            "story_title": final_state["story_title"],
            "story_text": final_state["story_text"],
            "status": "completed",
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "regression_risk": final_state.get("regression_analysis", {}).get("overall_regression_risk", "unknown"),
            "report_filename": final_state.get("report_filename", ""),
            "agent_steps": final_state.get("agent_steps", []),
            "execution_results": execution_results,
            "regression_analysis": final_state.get("regression_analysis", {})
        })

    except Exception as e:
        error_msg = str(e)
        if run_id in active_runs:
            active_runs[run_id]["status"] = "failed"
            active_runs[run_id]["completed"] = True
            active_runs[run_id]["error"] = error_msg
        print(f"\n{'!'*60}")
        print(f"!!! PIPELINE FAILED: Run {run_id}")
        print(f"!!! Error: {error_msg}")
        print(f"{'!'*60}")
        import traceback
        traceback.print_exc()


@app.get("/api/runs/{run_id}/stream")
async def stream_run(run_id: str):
    """
    Server-Sent Events (SSE) endpoint for real-time agent status updates.
    Frontend connects to this and receives agent steps as they happen.
    """
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail="Run not found")

    async def event_generator():
        last_step_count = 0
        timeout = 300  # 5 minute timeout
        elapsed = 0

        while elapsed < timeout:
            if run_id not in active_runs:
                break

            run_data = active_runs[run_id]
            state = run_data.get("state", {})
            agent_steps = state.get("agent_steps", [])

            # Send any new steps
            if len(agent_steps) > last_step_count:
                for step in agent_steps[last_step_count:]:
                    yield f"data: {json.dumps({'type': 'step', 'step': step})}\n\n"
                last_step_count = len(agent_steps)

            # Send status update
            status_data = {
                "type": "status",
                "status": run_data["status"],
                "current_step": state.get("current_step", ""),
                "steps_completed": len(agent_steps)
            }
            yield f"data: {json.dumps(status_data)}\n\n"

            # If completed, send final result
            if run_data.get("completed"):
                final_data = {
                    "type": "completed",
                    "run_id": run_id,
                    "status": run_data["status"],
                    "execution_results": state.get("execution_results", []),
                    "regression_analysis": state.get("regression_analysis", {}),
                    "report_filename": state.get("report_filename", ""),
                    "agent_steps": agent_steps
                }
                if run_data.get("error"):
                    final_data["error"] = run_data["error"]
                yield f"data: {json.dumps(final_data)}\n\n"
                break

            await asyncio.sleep(1)
            elapsed += 1

        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Get a specific run by ID."""
    # Check active runs first
    if run_id in active_runs:
        run = active_runs[run_id]
        return {
            "run_id": run_id,
            "status": run["status"],
            "state": run.get("state", {})
        }
    # Check DB
    run = await get_run_by_id(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/api/runs")
async def list_runs():
    """Get all historical test runs."""
    runs = await get_all_runs()
    return {"runs": runs}


@app.get("/api/reports/{filename}")
async def get_report(filename: str):
    """Serve a generated HTML report."""
    # Sanitize filename
    filename = os.path.basename(filename)
    report_path = os.path.join(config.REPORTS_DIR, filename)
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report_path, media_type="text/html")


@app.get("/api/reports")
async def list_reports():
    """List all generated reports."""
    reports = []
    if os.path.exists(config.REPORTS_DIR):
        for f in os.listdir(config.REPORTS_DIR):
            if f.endswith(".html"):
                path = os.path.join(config.REPORTS_DIR, f)
                reports.append({
                    "filename": f,
                    "size_kb": round(os.path.getsize(path) / 1024, 1),
                    "created_at": datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                })
    reports.sort(key=lambda x: x["created_at"], reverse=True)
    return {"reports": reports}


@app.get("/api/knowledge/stats")
async def get_knowledge_stats():
    """Get RAG knowledge base statistics."""
    rag = get_rag_pipeline()
    return rag.get_collection_stats()


@app.get("/api/knowledge/similar-tests")
async def get_similar_tests(query: str, n: int = 5):
    """Query knowledge base for similar tests."""
    rag = get_rag_pipeline()
    results = rag.query_similar_tests(query, n_results=n)
    return {"results": results}


@app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Agentic feedback loop: Mark a test as false positive.
    This updates the knowledge base so future runs don't flag it.
    """
    rag = get_rag_pipeline()
    rag.update_test_feedback(request.test_name, request.is_false_positive)
    return {
        "success": True,
        "message": f"Test '{request.test_name}' marked as false_positive={request.is_false_positive}. "
                   f"Future runs will learn from this feedback."
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Sentinel-Agent API server (no auto-reload)...")
    print("Restart manually with 'python main.py' after code changes.")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
