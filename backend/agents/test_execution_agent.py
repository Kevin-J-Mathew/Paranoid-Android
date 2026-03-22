import subprocess
import os
import json
import time
from datetime import datetime
from typing import Dict, Any
from ..core.config import config


def run_test_execution_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Execution Agent: Runs each generated Playwright test file and captures results.
    Uses subprocess to run pytest on each file individually.
    """
    generated_tests = state["generated_tests"]
    story_id = state["story_id"]

    step = {
        "agent_name": "Test Execution Agent",
        "status": "running",
        "message": f"Executing {len(generated_tests)} test files against {config.TARGET_APP_URL}...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "test_execution_agent"

    execution_results = []

    for test in generated_tests:
        file_path = test.get("file_path")
        scenario_name = test["scenario_name"]

        if not file_path or not os.path.exists(file_path):
            execution_results.append({
                "test_name": scenario_name,
                "status": "error",
                "duration_ms": 0,
                "error_message": f"Test file not found: {file_path}",
                "screenshot_path": None,
                "stdout": ""
            })
            continue

        start_time = time.time()

        try:
            # Run pytest on the individual test file with timeout
            result = subprocess.run(
                ["python", "-m", "pytest", file_path, "-v", "--tb=short",
                 "--timeout=30", "--no-header", "-rN"],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second overall timeout
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            duration_ms = (time.time() - start_time) * 1000
            stdout = result.stdout + result.stderr
            passed = result.returncode == 0

            # Find screenshot if it was created
            screenshot_path = None
            expected_screenshot = os.path.join(
                config.SCREENSHOTS_DIR, f"{scenario_name}.png"
            )
            if os.path.exists(expected_screenshot):
                screenshot_path = expected_screenshot

            status = "passed" if passed else "failed"
            error_message = None

            if not passed:
                # Extract error from stdout
                lines = stdout.split("\n")
                error_lines = [l for l in lines if "FAILED" in l or "Error" in l or "assert" in l.lower()]
                error_message = "\n".join(error_lines[:5]) if error_lines else stdout[-500:]

            execution_results.append({
                "test_name": scenario_name,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "error_message": error_message,
                "screenshot_path": screenshot_path,
                "stdout": stdout[:2000]  # Cap log length
            })

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            execution_results.append({
                "test_name": scenario_name,
                "status": "error",
                "duration_ms": round(duration_ms, 2),
                "error_message": "Test timed out after 60 seconds",
                "screenshot_path": None,
                "stdout": ""
            })
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            execution_results.append({
                "test_name": scenario_name,
                "status": "error",
                "duration_ms": round(duration_ms, 2),
                "error_message": str(e),
                "screenshot_path": None,
                "stdout": ""
            })

    passed_count = sum(1 for r in execution_results if r["status"] == "passed")
    failed_count = sum(1 for r in execution_results if r["status"] == "failed")
    error_count = sum(1 for r in execution_results if r["status"] == "error")
    total = len(execution_results)

    state["execution_results"] = execution_results
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = (
        f"Execution complete: {passed_count}/{total} passed, "
        f"{failed_count} failed, {error_count} errors"
    )
    state["agent_steps"][-1]["data"] = {
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "errors": error_count,
        "pass_rate": round(passed_count / total * 100, 1) if total > 0 else 0
    }
    return state
