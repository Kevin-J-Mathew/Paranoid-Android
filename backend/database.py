import aiosqlite
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

DATABASE_PATH = "sentinel.db"


async def init_db():
    """Initialize SQLite database with required tables."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id TEXT PRIMARY KEY,
                story_id TEXT NOT NULL,
                story_title TEXT,
                story_text TEXT,
                status TEXT NOT NULL,
                total_tests INTEGER DEFAULT 0,
                passed_tests INTEGER DEFAULT 0,
                failed_tests INTEGER DEFAULT 0,
                regression_risk TEXT,
                report_filename TEXT,
                agent_steps_json TEXT,
                execution_results_json TEXT,
                regression_analysis_json TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_run(run_data: Dict[str, Any]):
    """Save a completed test run to SQLite."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO test_runs 
            (id, story_id, story_title, story_text, status, total_tests, passed_tests, 
             failed_tests, regression_risk, report_filename, agent_steps_json, 
             execution_results_json, regression_analysis_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_data["run_id"],
            run_data["story_id"],
            run_data.get("story_title", ""),
            run_data.get("story_text", ""),
            run_data["status"],
            run_data.get("total_tests", 0),
            run_data.get("passed_tests", 0),
            run_data.get("failed_tests", 0),
            run_data.get("regression_risk", "unknown"),
            run_data.get("report_filename", ""),
            json.dumps(run_data.get("agent_steps", [])),
            json.dumps(run_data.get("execution_results", [])),
            json.dumps(run_data.get("regression_analysis", {})),
            datetime.utcnow().isoformat()
        ))
        await db.commit()


async def get_all_runs() -> List[Dict]:
    """Retrieve all test runs ordered by most recent."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM test_runs ORDER BY created_at DESC LIMIT 50"
        )
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["agent_steps"] = json.loads(d.get("agent_steps_json") or "[]")
            d["execution_results"] = json.loads(d.get("execution_results_json") or "[]")
            d["regression_analysis"] = json.loads(d.get("regression_analysis_json") or "{}")
            result.append(d)
        return result


async def get_run_by_id(run_id: str) -> Optional[Dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM test_runs WHERE id = ?", (run_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["agent_steps"] = json.loads(d.get("agent_steps_json") or "[]")
        d["execution_results"] = json.loads(d.get("execution_results_json") or "[]")
        d["regression_analysis"] = json.loads(d.get("regression_analysis_json") or "{}")
        return d
