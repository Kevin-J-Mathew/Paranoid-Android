import json
import os
from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from ..core.llm import get_llm
from ..core.config import config


GENERATION_SYSTEM_PROMPT = """You are an expert Playwright test engineer. Generate production-quality Python Playwright tests.

RULES:
1. Use `playwright.sync_api` (synchronous, not async)
2. Every test function starts with `test_` prefix  
3. Use the exact URL provided — do not hardcode a different URL
4. Every test must have a screenshot at the end: `page.screenshot(path=screenshot_path)`
5. Use `expect` from `playwright.sync_api` for assertions
6. Handle waits properly: use `page.wait_for_selector()` or `expect(locator).to_be_visible()`
7. Each test must be self-contained and independent
8. Return ONLY valid Python code, no markdown, no explanation

The file structure must be exactly:
```python
import pytest
from playwright.sync_api import sync_playwright, expect
import os

TARGET_URL = "https://demo.playwright.dev/todomvc"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def test_SCENARIO_NAME():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(TARGET_URL)
            # ... test steps ...
            screenshot_path = os.path.join(SCREENSHOTS_DIR, "SCENARIO_NAME.png")
            page.screenshot(path=screenshot_path)
        finally:
            browser.close()
```

For the TodoMVC app at https://demo.playwright.dev/todomvc:
- Add todo input: page.locator(".new-todo")
- Todo list items: page.locator(".todo-list li")
- Checkbox to complete: page.locator(".todo-list li .toggle")
- Delete button (appears on hover): page.locator(".todo-list li .destroy")
- Filter links: page.locator(".filters a") 
- Clear completed button: page.locator(".clear-completed")
- Todo count: page.locator(".todo-count")
- Edit: double-click on label, then edit the .edit input"""


def run_test_generation_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Generation Agent: Uses LLM + RAG context to generate Playwright test code.
    """
    requirements = state["parsed_requirements"]
    rag_context = state["rag_context"]
    story_text = state["story_text"]
    story_id = state["story_id"]

    step = {
        "agent_name": "Test Generation Agent",
        "status": "running",
        "message": f"Generating Playwright tests for {len(requirements.get('testable_scenarios', []))} scenarios...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "test_generation_agent"

    # Build RAG context string
    rag_context_str = ""
    if rag_context.get("similar_tests"):
        rag_context_str += "\n\nHISTORICAL SIMILAR TESTS (learn from these patterns):\n"
        for item in rag_context["similar_tests"][:3]:
            rag_context_str += f"- {item['document']}\n"
            if item["metadata"].get("test_code"):
                rag_context_str += f"  Code snippet: {item['metadata']['test_code'][:300]}\n"

    if rag_context.get("similar_bugs"):
        rag_context_str += "\n\nHISTORICAL BUGS TO WATCH FOR:\n"
        for item in rag_context["similar_bugs"][:3]:
            rag_context_str += f"- {item['document']}\n"

    llm = get_llm(temperature=0.2)
    generated_tests = []

    scenarios = requirements.get("testable_scenarios", [])
    edge_cases = requirements.get("edge_cases", [])

    # Add edge case scenarios
    for ec in edge_cases[:2]:
        scenarios.append({
            "name": f"edge_case_{ec.replace(' ', '_').lower()[:30]}",
            "description": ec,
            "steps": ["Navigate to app", ec, "Verify app handles it gracefully"],
            "expected_result": "App handles edge case without crashing",
            "priority": "medium",
            "test_type": "edge_case"
        })

    for scenario in scenarios:
        scenario_name = scenario["name"].replace(" ", "_").replace("-", "_").lower()

        messages = [
            SystemMessage(content=GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=f"""Generate a Playwright test for this scenario.

USER STORY: {story_text}

SCENARIO:
Name: {scenario_name}
Description: {scenario["description"]}
Steps: {json.dumps(scenario["steps"])}
Expected Result: {scenario["expected_result"]}
Priority: {scenario["priority"]}
Type: {scenario["test_type"]}
{rag_context_str}

Generate the complete Python Playwright test function. Function name must be `test_{scenario_name}`.
Return ONLY the Python code, no markdown backticks, no explanation.""")
        ]

        response = llm.invoke(messages)
        test_code = response.content.strip()

        # Clean up any markdown if model adds it despite instructions
        if "```python" in test_code:
            test_code = test_code.split("```python")[1].split("```")[0].strip()
        elif "```" in test_code:
            test_code = test_code.split("```")[1].split("```")[0].strip()

        generated_tests.append({
            "scenario_name": scenario_name,
            "scenario": scenario,
            "test_code": test_code,
            "file_name": f"test_{scenario_name}_{story_id[:8]}.py"
        })

    # Write test files to disk
    written_files = []
    for test in generated_tests:
        file_path = os.path.join(config.TESTS_OUTPUT_DIR, test["file_name"])
        with open(file_path, "w") as f:
            # Ensure proper imports at top of file
            final_code = test["test_code"]
            if "import pytest" not in final_code:
                final_code = "import pytest\nfrom playwright.sync_api import sync_playwright, expect\nimport os\n\n" + final_code
            f.write(final_code)
        test["file_path"] = file_path
        written_files.append(file_path)

    state["generated_tests"] = generated_tests
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Generated {len(generated_tests)} test files: {', '.join([t['file_name'] for t in generated_tests])}"
    )
    state["agent_steps"][-1]["data"] = {
        "test_count": len(generated_tests),
        "test_names": [t["scenario_name"] for t in generated_tests]
    }
    return state
