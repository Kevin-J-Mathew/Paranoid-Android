import json
from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from ..core.llm import get_llm  # pyre-ignore[21]
from ..core.config import config  # pyre-ignore[21]


REQUIREMENTS_SYSTEM_PROMPT = """You are a senior QA architect. Your task is to analyze a user story and extract
structured, testable requirements. You must return ONLY a valid JSON object — no markdown, no explanation, just JSON.

The JSON structure must be:
{
  "story_summary": "one-line summary of what this story does",
  "testable_scenarios": [
    {
      "name": "scenario name as snake_case",
      "description": "what this scenario tests",
      "steps": ["step 1", "step 2", "step 3"],
      "expected_result": "what should happen",
      "priority": "high|medium|low",
      "test_type": "functional|regression|edge_case"
    }
  ],
  "risk_areas": ["area1", "area2"],
  "edge_cases": ["edge case description 1", "edge case description 2"]
}

Always generate at least 3 testable scenarios. Include at least 1 edge case scenario."""


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)

    return str(content)


def run_requirements_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Requirements Agent: Parses user story into structured testable scenarios.
    Runs synchronously within the LangGraph node.
    """
    story_text = state["story_text"]
    story_id = state["story_id"]

    print(f"\n{'='*60}")
    print(f"[Requirements Agent] STARTED — Story: {story_id}")
    print(f"{'='*60}")

    step = {
        "agent_name": "Requirements Agent",
        "status": "running",
        "message": f"Analyzing user story: '{story_text[:80]}...'",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "requirements_agent"

    print(f"[Requirements Agent] Calling Groq LLM...")
    llm = get_llm(temperature=0.1)
    messages = [
        SystemMessage(content=REQUIREMENTS_SYSTEM_PROMPT),
        HumanMessage(content=f"""Analyze this user story and extract testable scenarios.
        
Story ID: {story_id}
Story: {story_text}

Target Application URL: {config.TARGET_APP_URL}
This is a TodoMVC application. Users can: add todos, complete todos, delete todos, filter todos (All/Active/Completed), clear completed todos, edit todos by double-clicking.

Return only the JSON object as specified.""")
    ]

    response = llm.invoke(messages)
    raw = _message_content_to_text(response.content).strip()

    # Safely parse JSON even if model adds backticks
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        parsed = json.loads(raw)
        print(f"[Requirements Agent] Parsed {len(parsed.get('testable_scenarios', []))} scenarios")
    except json.JSONDecodeError:
        print(f"[Requirements Agent] WARNING: JSON parse failed, using fallback")
        # Fallback: create minimal structure
        parsed = {
            "story_summary": story_text[:100],
            "testable_scenarios": [
                {
                    "name": "basic_functionality_test",
                    "description": "Test basic functionality described in story",
                    "steps": ["Navigate to app", "Perform described action", "Verify result"],
                    "expected_result": "Action completes successfully",
                    "priority": "high",
                    "test_type": "functional"
                }
            ],
            "risk_areas": ["UI interaction"],
            "edge_cases": ["Empty input handling"]
        }

    state["parsed_requirements"] = parsed
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Extracted {len(parsed.get('testable_scenarios', []))} testable scenarios. "
        f"Risk areas: {', '.join(parsed.get('risk_areas', []))}"
    )
    state["agent_steps"][-1]["data"] = parsed
    print(f"[Requirements Agent] COMPLETED ✓")
    return state
