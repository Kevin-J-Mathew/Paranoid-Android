import os
import base64
import json
from datetime import datetime
from typing import Dict, Any
from ..core.config import config  # pyre-ignore[21]


def _encode_screenshot(screenshot_path: str) -> str:
    """Encode screenshot as base64 for embedding in HTML report."""
    if not screenshot_path or not os.path.exists(screenshot_path):
        return ""
    with open(screenshot_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def run_report_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Report Agent: Generates a comprehensive self-contained HTML report with all evidence.
    """
    story_id = state["story_id"]
    story_text = state["story_text"]
    parsed_requirements = state["parsed_requirements"]
    execution_results = state["execution_results"]
    regression_analysis = state["regression_analysis"]
    agent_steps = state["agent_steps"]
    run_id = state.get("run_id", story_id)

    print(f"\n{'='*60}")
    print(f"[Report Agent] STARTED — Generating HTML report")
    print(f"{'='*60}")

    step = {
        "agent_name": "Report Agent",
        "status": "running",
        "message": "Generating comprehensive HTML test report with evidence...",
        "timestamp": datetime.utcnow().isoformat(),
    }
    state["agent_steps"].append(step)
    state["current_step"] = "report_agent"

    # Calculate metrics
    total = len(execution_results)
    passed = sum(1 for r in execution_results if r["status"] == "passed")
    failed = sum(1 for r in execution_results if r["status"] == "failed")
    errors = sum(1 for r in execution_results if r["status"] == "error")
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0
    regression_risk = regression_analysis.get("overall_regression_risk", "unknown")
    risk_color_map = {
        "critical": "#ef4444",
        "high": "#f97316",
        "medium": "#eab308",
        "low": "#22c55e",
        "none": "#22c55e",
        "unknown": "#6b7280"
    }
    risk_color = risk_color_map.get(regression_risk, "#6b7280")

    # Build test result rows
    result_rows = ""
    for r in execution_results:
        status_color = {
            "passed": "#22c55e",
            "failed": "#ef4444",
            "error": "#f97316",
            "skipped": "#6b7280"
        }.get(r["status"], "#6b7280")

        screenshot_html = ""
        if r.get("screenshot_path"):
            b64 = _encode_screenshot(r["screenshot_path"])
            if b64:
                screenshot_html = f'<img src="{b64}" style="max-width:300px;border:1px solid #ddd;border-radius:4px;margin-top:8px;" />'

        reg_flag = next(
            (f for f in regression_analysis.get("flags", []) if f.get("test_name") == r["test_name"]),
            None
        )
        regression_badge = ""
        if reg_flag and reg_flag.get("is_regression"):
            regression_badge = f'<span style="background:#ef4444;color:white;padding:2px 8px;border-radius:12px;font-size:11px;margin-left:8px;">REGRESSION</span>'

        error_html = ""
        if r.get("error_message"):
            error_html = f'<pre style="background:#1e1e1e;color:#f8f8f2;padding:12px;border-radius:4px;font-size:12px;overflow-x:auto;margin-top:8px;">{r["error_message"][:1000]}</pre>'

        result_rows += f"""
        <div style="border:1px solid #e5e7eb;border-radius:8px;padding:16px;margin-bottom:16px;">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
              <span style="font-weight:600;font-size:15px;">{r["test_name"]}</span>
              {regression_badge}
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="color:#6b7280;font-size:13px;">{r["duration_ms"]}ms</span>
              <span style="background:{status_color};color:white;padding:4px 12px;border-radius:20px;font-size:13px;font-weight:600;text-transform:uppercase;">{r["status"]}</span>
            </div>
          </div>
          {error_html}
          {screenshot_html}
        </div>"""

    # Build regression flags section
    regression_rows = ""
    for flag in regression_analysis.get("flags", []):
        if flag.get("is_regression"):
            regression_rows += f"""
            <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:12px;margin-bottom:8px;">
              <strong>{flag["test_name"]}</strong>: {flag["explanation"]}
              <br><span style="color:#6b7280;font-size:12px;">Severity: {flag.get("severity","unknown").upper()}</span>
            </div>"""

    if not regression_rows:
        regression_rows = '<p style="color:#22c55e;">✓ No regressions detected in this run.</p>'

    # Build agent steps section
    steps_html = ""
    for s in agent_steps:
        icon = "✓" if s["status"] == "completed" else ("✗" if s["status"] == "failed" else "⟳")
        color = "#22c55e" if s["status"] == "completed" else ("#ef4444" if s["status"] == "failed" else "#3b82f6")
        steps_html += f"""
        <div style="display:flex;gap:12px;margin-bottom:8px;align-items:flex-start;">
          <span style="color:{color};font-size:16px;min-width:20px;">{icon}</span>
          <div>
            <span style="font-weight:600;color:{color};">{s["agent_name"]}</span>
            <span style="color:#6b7280;font-size:12px;margin-left:8px;">{s["timestamp"]}</span>
            <p style="color:#374151;margin:2px 0 0 0;font-size:14px;">{s["message"]}</p>
          </div>
        </div>"""

    # Recommendations
    recommendations_html = ""
    for rec in regression_analysis.get("recommendations", []):
        recommendations_html += f'<li style="margin-bottom:4px;">{rec}</li>'

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    html_report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sentinel-Agent Test Report — {story_id}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f9fafb; color: #111827; }}
  .header {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 32px 40px; }}
  .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
  .header p {{ color: #94a3b8; font-size: 14px; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px; }}
  .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 32px; }}
  .metric-card {{ background: white; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .metric-card .value {{ font-size: 36px; font-weight: 800; }}
  .metric-card .label {{ font-size: 13px; color: #6b7280; margin-top: 4px; }}
  .section {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .section h2 {{ font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 12px; }}
  .story-box {{ background: #f8fafc; border-left: 4px solid #3b82f6; padding: 16px; border-radius: 4px; font-size: 14px; line-height: 1.6; }}
</style>
</head>
<body>
<div class="header">
  <h1>🤖 Sentinel-Agent Test Report</h1>
  <p>Run ID: {run_id} | Generated: {timestamp} | Story: {story_id}</p>
</div>
<div class="container">
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="value" style="color:#3b82f6;">{total}</div>
      <div class="label">Total Tests</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:#22c55e;">{passed}</div>
      <div class="label">Passed</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:#ef4444;">{failed + errors}</div>
      <div class="label">Failed / Error</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:{risk_color};">{regression_risk.upper()}</div>
      <div class="label">Regression Risk</div>
    </div>
  </div>

  <div class="section">
    <h2>📋 User Story</h2>
    <div class="story-box">{story_text}</div>
    <p style="margin-top:12px;color:#6b7280;font-size:13px;">
      Summary: {parsed_requirements.get("story_summary", "N/A")} |
      Risk Areas: {", ".join(parsed_requirements.get("risk_areas", []))}
    </p>
  </div>

  <div class="section">
    <h2>🧪 Test Results ({pass_rate}% Pass Rate)</h2>
    {result_rows}
  </div>

  <div class="section">
    <h2>🔍 Regression Analysis</h2>
    <p style="margin-bottom:12px;color:#374151;">{regression_analysis.get("regression_summary", "")}</p>
    {regression_rows}
    {"<h3 style='margin-top:16px;font-size:15px;font-weight:600;'>Recommendations:</h3><ul style='margin-top:8px;padding-left:20px;color:#374151;font-size:14px;'>" + recommendations_html + "</ul>" if recommendations_html else ""}
  </div>

  <div class="section">
    <h2>🤖 Agent Execution Timeline</h2>
    {steps_html}
  </div>
</div>
</body>
</html>"""

    # Save report to disk
    report_filename = f"report_{run_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
    report_path = os.path.join(config.REPORTS_DIR, report_filename)
    print(f"[Report Agent] Writing report to: {report_filename}")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_report)
    print(f"[Report Agent] Report written: {len(html_report)} bytes")

    state["report_html"] = html_report
    state["report_path"] = report_path
    state["report_filename"] = report_filename
    state["agent_steps"][-1]["status"] = "completed"
    state["agent_steps"][-1]["message"] = f"Report generated: {report_filename}"
    state["agent_steps"][-1]["data"] = {
        "report_path": report_path,
        "pass_rate": pass_rate,
        "total_tests": total
    }
    print(f"[Report Agent] COMPLETED ✓")
    return state
