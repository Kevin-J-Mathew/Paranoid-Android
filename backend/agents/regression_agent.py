import json
from datetime import datetime
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage
from ..core.llm import get_llm
from ..core.rag import get_rag_pipeline


REGRESSION_SYSTEM_PROMPT = """You are a senior QA regression analyst. Analyze test results and identify regressions.

A regression is when a previously working test now fails, or when pass rate drops significantly.

Given test results and historical baselines, return ONLY a valid JSON object:
{
  "overall_regression_risk": "critical|high|medium|low|none",
  "regression_summary": "brief summary",
  "flags": [
    {
      "test_name": "test name",
      "is_regression": true/false,
      "baseline_pass_rate": 95.0 or null,
      "current_status": "passed|failed|error",
      "severity": "critical|warning|none",
      "explanation": "why this is or isn't a regression"
    }
  ],
  "recommendations": ["recommendation 1", "recommendation 2"]
}"""


def run_regression_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Regression Agent: Compares current run results against ChromaDB baselines.
    """
    execution_results = state["execution_results"]
    story_id = state["story_id"]
    story_text = state["story_text"]

    step = {
        "agent_name": "Regression Detection Agent",
        "status": "running",
        "message": "Comparing results against historical baselines...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "regression_agent"

    rag = get_rag_pipeline()

    # Build baseline context from ChromaDB
    baseline_context = []
    for result in execution_results:
        baseline = rag.get_baseline_for_test(story_id, result["test_name"])
        if baseline:
            baseline_context.append({
                "test_name": result["test_name"],
                "baseline_pass_rate": baseline.get("pass_rate"),
                "current_status": result["status"]
            })
        else:
            baseline_context.append({
                "test_name": result["test_name"],
                "baseline_pass_rate": None,  # No history → first run
                "current_status": result["status"]
            })

    # Check for false positive overrides in knowledge base
    false_positive_tests = set()
    similar_feedback = rag.query_similar_tests(f"false_positive feedback {story_text}", n_results=10)
    for item in similar_feedback:
        if item["metadata"].get("false_positive") == "True":
            false_positive_tests.add(item["metadata"].get("test_name", ""))

    # Build summary for LLM
    results_summary = json.dumps(execution_results, indent=2)
    baseline_summary = json.dumps(baseline_context, indent=2)
    false_positive_note = (
        f"The following tests are marked as false positives by humans and should not be flagged as regressions: "
        f"{list(false_positive_tests)}" if false_positive_tests else ""
    )

    llm = get_llm(temperature=0.0)
    messages = [
        SystemMessage(content=REGRESSION_SYSTEM_PROMPT),
        HumanMessage(content=f"""Analyze these test results for regressions.

STORY: {story_text}

CURRENT TEST RESULTS:
{results_summary}

HISTORICAL BASELINES:
{baseline_summary}

{false_positive_note}

Notes:
- If baseline_pass_rate is null, it's the first run — treat failed tests as new issues, not regressions
- If pass_rate drops by more than 20%, flag as regression
- Mark critical if a high-priority test fails

Return only the JSON object.""")
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        regression_analysis = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback
        regression_analysis = {
            "overall_regression_risk": "unknown",
            "regression_summary": "Could not complete regression analysis",
            "flags": [],
            "recommendations": ["Review test results manually"]
        }

    state["regression_analysis"] = regression_analysis
    state["agent_steps"][-1]["status"] = "completed"
    risk = regression_analysis.get("overall_regression_risk", "unknown")
    state["agent_steps"][-1]["message"] = (
        f"Regression risk: {risk.upper()}. "
        f"{regression_analysis.get('regression_summary', '')}"
    )
    state["agent_steps"][-1]["data"] = regression_analysis
    return state
