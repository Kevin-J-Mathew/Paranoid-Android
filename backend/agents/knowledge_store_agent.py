from datetime import datetime
from typing import Dict, Any
from ..core.rag import get_rag_pipeline  # pyre-ignore[21]


def run_knowledge_store_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Knowledge Store Agent: Saves all results back to ChromaDB for future RAG queries.
    This is what enables the system to 'learn' from past runs.
    """
    story_id = state["story_id"]
    story_text = state["story_text"]
    execution_results = state["execution_results"]
    generated_tests = state["generated_tests"]
    regression_analysis = state["regression_analysis"]

    print(f"\n{'='*60}")
    print(f"[Knowledge Store Agent] STARTED — Storing {len(execution_results)} results")
    print(f"{'='*60}")

    step = {
        "agent_name": "Knowledge Store Agent",
        "status": "running",
        "message": "Storing results in knowledge base for future learning...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "knowledge_store_agent"

    rag = get_rag_pipeline()

    # Map test code by scenario name
    code_map = {t["scenario_name"]: t["test_code"] for t in generated_tests}

    # Store each test case result
    stored_count = 0
    for result in execution_results:
        test_name = result["test_name"]
        test_code = code_map.get(test_name, "")
        rag.add_test_case(
            story_id=story_id,
            story_text=story_text,
            test_code=test_code,
            test_name=test_name,
            outcome=result["status"],
            metadata={
                "duration_ms": str(result["duration_ms"]),
                "run_timestamp": datetime.utcnow().isoformat()
            }
        )
        # Store baseline pass rate (1.0 for passed, 0.0 for failed)
        rag.add_run_baseline(
            story_id=story_id,
            test_name=test_name,
            pass_rate=1.0 if result["status"] == "passed" else 0.0,
            avg_duration_ms=result["duration_ms"]
        )
        stored_count += 1

    # Store regression flags as bug reports if regressions found
    for flag in regression_analysis.get("flags", []):
        if flag.get("is_regression"):
            rag.add_bug_report(
                bug_id=f"reg_{story_id}_{flag['test_name']}",
                title=f"Regression in {flag['test_name']}",
                description=flag.get("explanation", ""),
                affected_area=flag["test_name"],
                severity=flag.get("severity", "medium")
            )

    stats = rag.get_collection_stats()
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Stored {stored_count} test results in knowledge base. "
        f"Total knowledge base: {stats['test_cases']} tests, "
        f"{stats['bug_reports']} bugs, {stats['run_baselines']} baselines."
    )
    state["agent_steps"][-1]["data"] = stats
    print(f"[Knowledge Store Agent] Stored {stored_count} results. DB: {stats['test_cases']} tests, {stats['bug_reports']} bugs")
    print(f"[Knowledge Store Agent] COMPLETED ✓")
    return state
