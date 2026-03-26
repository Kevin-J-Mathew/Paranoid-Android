import subprocess
import os
import json
import time
from datetime import datetime
from typing import Dict, Any
from ..core.config import config  # pyre-ignore[21]
from ..core.llm import get_llm  # pyre-ignore[21]

# Maximum number of repair attempts per failed test
MAX_REPAIR_ATTEMPTS = 2

REPAIR_SYSTEM_PROMPT = """You are an expert Playwright test debugger. A Playwright test failed with an error.
Your job is to fix the test code so it passes. 

RULES:
1. Return ONLY the complete fixed Python code — no explanation, no markdown backticks.
2. Fix the specific error described. Common fixes:
   - NameError: Add the missing import or variable definition
   - AttributeError: Use the correct Playwright API method
   - Timeout: The element doesn't exist yet or is hidden — wait for it or check a different selector
   - AssertionError: The assertion logic is wrong — fix the expected value or use a different assertion
3. Use `playwright.sync_api` (synchronous, NOT async)
4. Use `expect()` from playwright for assertions, NOT bare `assert`
5. Do NOT hallucinate methods. Valid Playwright expect methods include:
   to_be_visible, to_have_text, to_contain_text, to_have_count, to_be_checked, to_be_empty, to_have_class, to_have_value
6. For class checks use regex: expect(locator).to_have_class(re.compile(r'completed'))
7. When TodoMVC list is empty, .todo-count, .filters, .clear-completed DO NOT EXIST in the DOM
8. Use .text_content() not .text to read element text
9. Check completion via expect(checkbox).to_be_checked() not CSS styles
10. Always include `import re` at the top if using re.compile()
11. Keep the exact same function name as the original test
12. Keep all video recording context setup (record_video_dir, record_video_size) intact
13. In the finally block, always call context.close() BEFORE browser.close()"""


def _repair_test(original_code: str, error_message: str, scenario_name: str) -> str:
    """Use the LLM to repair a failed test based on the error message."""
    llm = get_llm()
    from langchain_core.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content=REPAIR_SYSTEM_PROMPT),
        HumanMessage(content=f"""The following Playwright test FAILED. Fix it.

TEST NAME: {scenario_name}

ORIGINAL CODE:
```python
{original_code}
```

ERROR:
```
{error_message}
```

Return ONLY the complete fixed Python code. No markdown, no explanation.""")
    ]

    response = llm.invoke(messages)
    content = response.content if isinstance(response.content, str) else str(response.content)

    # Extract code block if wrapped in markdown
    code_block = content
    if "```python" in content:
        code_block = content.split("```python")[1].split("```")[0].strip()
    elif "```" in content:
        code_block = content.split("```")[1].split("```")[0].strip()

    return code_block


def _run_single_test(file_path: str, scenario_name: str) -> Dict[str, Any]:
    """Run a single pytest file and return the result dict."""
    start_time = time.time()

    try:
        result = subprocess.run(
            ["python", "-m", "pytest", file_path, "-v", "--tb=short",
             "--timeout=30", "--no-header", "-rN"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        duration_ms = (time.time() - start_time) * 1000
        stdout = result.stdout + result.stderr
        passed = result.returncode == 0

        # Find screenshot
        screenshot_path = None
        expected_screenshot = os.path.join(config.SCREENSHOTS_DIR, f"{scenario_name}.png")
        if os.path.exists(expected_screenshot):
            screenshot_path = expected_screenshot

        # Find most recently created video
        video_path = None
        try:
            webm_files = sorted(
                [f for f in os.listdir(config.SCREENSHOTS_DIR) if f.endswith(".webm")],
                key=lambda f: os.path.getmtime(os.path.join(config.SCREENSHOTS_DIR, f)),
                reverse=True
            )
            if webm_files:
                video_path = os.path.join(config.SCREENSHOTS_DIR, webm_files[0])
        except Exception:
            pass

        error_message = None
        if not passed:
            lines = stdout.split("\n")
            error_lines = [l for l in lines if "FAILED" in l or "Error" in l or "assert" in l.lower()]
            error_message = "\n".join(error_lines[:5]) if error_lines else stdout[-500:]

        return {
            "passed": passed,
            "duration_ms": round(duration_ms, 2),
            "error_message": error_message,
            "screenshot_path": screenshot_path,
            "video_path": video_path,
            "video_url": f"/screenshots/{os.path.basename(video_path)}" if video_path else None,
            "stdout": stdout[:2000]
        }

    except subprocess.TimeoutExpired:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "passed": False,
            "duration_ms": round(duration_ms, 2),
            "error_message": "Test timed out after 60 seconds",
            "screenshot_path": None,
            "video_path": None,
            "video_url": None,
            "stdout": ""
        }
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return {
            "passed": False,
            "duration_ms": round(duration_ms, 2),
            "error_message": str(e),
            "screenshot_path": None,
            "video_path": None,
            "video_url": None,
            "stdout": ""
        }


def run_test_execution_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Execution Agent: Runs each generated Playwright test file and captures results.
    Includes a self-healing repair loop that feeds errors back to the LLM to fix broken tests.
    """
    generated_tests = state["generated_tests"]
    story_id = state["story_id"]

    print(f"\n{'='*60}")
    print(f"[Test Execution Agent] STARTED — {len(generated_tests)} tests to run")
    print(f"[Test Execution Agent] Target: {config.TARGET_APP_URL}")
    print(f"[Test Execution Agent] Self-healing: up to {MAX_REPAIR_ATTEMPTS} repair attempts per failed test")
    print(f"{'='*60}")

    step = {
        "agent_name": "Test Execution Agent",
        "status": "running",
        "message": f"Executing {len(generated_tests)} test files against {config.TARGET_APP_URL}...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "test_execution_agent"

    execution_results = []

    for i, test in enumerate(generated_tests, 1):
        file_path = test.get("file_path")
        scenario_name = test["scenario_name"]

        print(f"[Test Execution Agent] Running test {i}/{len(generated_tests)}: {scenario_name}")

        if not file_path or not os.path.exists(file_path):
            print(f"[Test Execution Agent]   -> ERROR: File not found: {file_path}")
            execution_results.append({
                "test_name": scenario_name,
                "status": "error",
                "duration_ms": 0,
                "error_message": f"Test file not found: {file_path}",
                "screenshot_path": None,
                "video_path": None,
                "video_url": None,
                "stdout": "",
                "repair_attempts": 0,
                "was_repaired": False
            })
            continue

        # --- Initial run ---
        result = _run_single_test(file_path, scenario_name)
        total_duration = result["duration_ms"]
        repair_attempts = 0
        was_repaired = False

        if result["passed"]:
            print(f"[Test Execution Agent]   -> PASSED ({round(total_duration)}ms)")
        else:
            print(f"[Test Execution Agent]   -> FAILED ({round(total_duration)}ms)")
            if result["error_message"]:
                print(f"[Test Execution Agent]   -> Error: {result['error_message'][:200]}")

            # --- Self-healing repair loop ---
            for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
                print(f"[Test Execution Agent]   -> REPAIRING (attempt {attempt}/{MAX_REPAIR_ATTEMPTS})...")

                try:
                    # Read the current test code
                    with open(file_path, "r") as f:
                        original_code = f.read()

                    # Ask LLM to fix it
                    repaired_code = _repair_test(
                        original_code,
                        result["error_message"] or "Unknown error",
                        scenario_name
                    )
                    print(f"[Test Execution Agent]   -> Repair generated {len(repaired_code)} chars")

                    # Ensure imports are present in repaired code
                    headers = []
                    if "import re" not in repaired_code:
                        headers.append("import re")
                    if "TARGET_URL =" not in repaired_code and "TARGET_URL=" not in repaired_code:
                        headers.append(f'\nTARGET_URL = "{config.TARGET_APP_URL}"\nSCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")\nos.makedirs(SCREENSHOTS_DIR, exist_ok=True)')
                    if "import pytest" not in repaired_code:
                        headers.insert(0, "import pytest\nfrom playwright.sync_api import sync_playwright, expect\nimport os")

                    if headers:
                        repaired_code = "\n".join(headers) + "\n\n" + repaired_code

                    # Overwrite the test file with repaired code
                    with open(file_path, "w") as f:
                        f.write(repaired_code)

                    # Re-run the repaired test
                    print(f"[Test Execution Agent]   -> Re-running repaired test...")
                    result = _run_single_test(file_path, scenario_name)
                    total_duration += result["duration_ms"]
                    repair_attempts = attempt

                    if result["passed"]:
                        was_repaired = True
                        print(f"[Test Execution Agent]   -> PASSED after repair ✓ (attempt {attempt})")
                        break
                    else:
                        print(f"[Test Execution Agent]   -> Still FAILED after repair attempt {attempt}")
                        if result["error_message"]:
                            print(f"[Test Execution Agent]   -> Error: {result['error_message'][:200]}")

                except Exception as e:
                    print(f"[Test Execution Agent]   -> Repair attempt {attempt} crashed: {str(e)[:200]}")
                    break

        status = "passed" if result["passed"] else "failed"
        execution_results.append({
            "test_name": scenario_name,
            "status": status,
            "duration_ms": round(total_duration, 2),
            "error_message": result["error_message"],
            "screenshot_path": result["screenshot_path"],
            "video_path": result["video_path"],
            "video_url": result["video_url"],
            "stdout": result["stdout"],
            "repair_attempts": repair_attempts,
            "was_repaired": was_repaired
        })

    passed_count = sum(1 for r in execution_results if r["status"] == "passed")
    failed_count = sum(1 for r in execution_results if r["status"] == "failed")
    error_count = sum(1 for r in execution_results if r["status"] == "error")
    repaired_count = sum(1 for r in execution_results if r.get("was_repaired"))
    total = len(execution_results)

    print(f"[Test Execution Agent] Results: {passed_count}/{total} passed, {failed_count} failed, {error_count} errors")
    if repaired_count > 0:
        print(f"[Test Execution Agent] Self-healed: {repaired_count} tests were repaired and passed ✓")

    state["execution_results"] = execution_results
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Execution complete: {passed_count}/{total} passed, "
        f"{failed_count} failed, {error_count} errors"
        + (f", {repaired_count} self-healed" if repaired_count > 0 else "")
    )
    state["agent_steps"][-1]["data"] = {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "repaired": repaired_count,
        "pass_rate": round(passed_count / total * 100, 1) if total > 0 else 0
    }
    print(f"[Test Execution Agent] COMPLETED ✓")
    return state
