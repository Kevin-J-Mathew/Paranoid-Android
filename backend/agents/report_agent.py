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
        "high": "#f59e0b",
        "medium": "#eab308",
        "low": "#22d3ee",
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
            "error": "#f59e0b",
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
            regression_badge = f'<span style="background:rgba(239,68,68,0.1);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:2px 8px;border-radius:4px;font-size:10px;font-family:\'JetBrains Mono\', monospace;margin-left:8px;box-shadow: 0 0 10px rgba(239,68,68,0.2);">CRITICAL_REGRESSION</span>'

        error_html = ""
        if r.get("error_message"):
            error_html = f'<pre style="background:rgba(239,68,68,0.05);color:#fca5a5;padding:12px;border-left:2px solid #ef4444;border-radius:0 4px 4px 0;font-size:11px;font-family:\'JetBrains Mono\', monospace;overflow-x:auto;margin-top:12px;box-shadow:inset 0 0 10px rgba(239,68,68,0.05);">{r["error_message"][:1000]}</pre>'

        result_rows += f"""
        <div style="background:#111111;border:1px solid #27272a;border-radius:8px;padding:16px;margin-bottom:16px;transition:border-color 0.2s;">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
              <span style="font-weight:600;font-size:14px;color:#f4f4f5;font-family:\'JetBrains Mono\', monospace;">{r["test_name"]}</span>
              {regression_badge}
            </div>
            <div style="display:flex;align-items:center;gap:12px;">
              <span style="color:#a1a1aa;font-size:11px;font-family:\'JetBrains Mono\', monospace;">LATENCY: <span style="color:#22d3ee">{r["duration_ms"]}ms</span></span>
              <span style="color:{status_color};border:1px solid {status_color}33;background:{status_color}1a;padding:4px 8px;border-radius:4px;font-size:10px;font-family:\'JetBrains Mono\', monospace;font-weight:700;text-transform:uppercase;box-shadow:0 0 8px {status_color}33;">{r["status"]}</span>
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
            <div style="background:rgba(239,68,68,0.05);border:1px solid rgba(239,68,68,0.2);border-radius:6px;padding:12px;margin-bottom:8px;">
              <strong style="color:#f87171;font-family:\'JetBrains Mono\', monospace;font-size:12px;">{flag["test_name"]}</strong>
              <span style="color:#e4e4e7;margin-left:8px;font-size:13px;">{flag["explanation"]}</span>
              <div style="color:#a1a1aa;font-size:10px;font-family:\'JetBrains Mono\', monospace;margin-top:6px;">SEVERITY: <span style="color:#ef4444">{flag.get("severity","unknown").upper()}</span></div>
            </div>"""

    if not regression_rows:
        regression_rows = '<p style="color:#22c55e;font-family:\'JetBrains Mono\', monospace;font-size:12px;">> NO_REGRESSIONS_DETECTED</p>'

    # Build agent steps section
    steps_html = ""
    for s in agent_steps:
        icon = "●"
        color = "#22c55e" if s["status"] == "completed" else ("#ef4444" if s["status"] == "failed" else "#22d3ee")
        steps_html += f"""
        <div style="display:flex;gap:12px;margin-bottom:12px;align-items:flex-start;background:#111111;padding:12px;border:1px solid #27272a;border-radius:6px;">
          <span style="color:{color};font-size:10px;min-width:14px;margin-top:2px;text-shadow:0 0 8px {color};">{icon}</span>
          <div>
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px;">
              <span style="font-weight:700;color:{color};font-family:\'JetBrains Mono\', monospace;font-size:12px;">{s["agent_name"].upper()}</span>
              <span style="color:#52525b;font-size:10px;font-family:\'JetBrains Mono\', monospace;">{s["timestamp"]}</span>
            </div>
            <p style="color:#a1a1aa;margin:0;font-size:13px;">{s["message"]}</p>
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
<title>Sentinel-Agent Report — {story_id}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ 
    font-family: 'Inter', sans-serif; 
    background-color: #080808; 
    color: #e4e4e7; 
    background-image: radial-gradient(rgba(255,255,255,0.05) 1px, transparent 1px);
    background-size: 20px 20px;
  }}
  .app-wrapper {{ padding: 24px; max-width: 1200px; margin: 0 auto; min-height: 100vh; }}
  .header {{ 
    background: #111111; 
    border: 1px solid #27272a; 
    border-radius: 12px; 
    padding: 32px 40px; 
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: ''; position: absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #00e5ff, transparent);
    opacity: 0.5;
  }}
  .header h1 {{ font-family: 'Space Grotesk', sans-serif; font-size: 24px; font-weight: 700; color: white; display:flex; align-items:center; gap:12px; margin-bottom: 12px; }}
  .header h1 span.accent {{ color: #00e5ff; text-shadow: 0 0 10px rgba(0,229,255,0.5); }}
  .header p {{ color: #a1a1aa; font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
  
  .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }}
  .metric-card {{ 
    background: #111111; 
    border: 1px solid #27272a; 
    border-radius: 8px; 
    padding: 24px; 
    text-align: right; 
    position: relative;
  }}
  .metric-card .value {{ font-family: 'Space Grotesk', sans-serif; font-size: 42px; font-weight: 700; line-height: 1; margin-bottom: 8px; }}
  .metric-card .label {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #a1a1aa; text-transform: uppercase; letter-spacing: 1px; }}
  
  .section {{ 
    background: #111111; 
    border: 1px solid #27272a; 
    border-radius: 12px; 
    padding: 32px; 
    margin-bottom: 24px; 
  }}
  .section h2 {{ 
    font-family: 'JetBrains Mono', monospace; 
    font-size: 12px; 
    font-weight: 700; 
    margin-bottom: 24px; 
    color: #22d3ee; 
    border-bottom: 1px solid #27272a; 
    padding-bottom: 12px; 
    text-transform: uppercase;
    letter-spacing: 2px;
  }}
  .story-box {{ background: #080808; border: 1px solid #27272a; padding: 20px; border-radius: 6px; font-size: 14px; line-height: 1.6; color: #d4d4d8; }}
</style>
</head>
<body>
<div class="app-wrapper">
  <div class="header">
    <h1><span class="accent">PARANOID ANDROID</span> / TEST_REPORT</h1>
    <p>RUN_ID: {run_id} &nbsp;|&nbsp; GENERATED: {timestamp} &nbsp;|&nbsp; SOURCE: {story_id}</p>
  </div>
  
  <div class="metrics-grid">
    <div class="metric-card">
      <div class="value" style="color:#e4e4e7;">{total}</div>
      <div class="label">Total Cases</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:#4ade80; text-shadow:0 0 15px rgba(74,222,128,0.4);">{passed}</div>
      <div class="label">Passed</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:#f87171; text-shadow:0 0 15px rgba(248,113,113,0.4);">{failed + errors}</div>
      <div class="label">Failed / Error</div>
    </div>
    <div class="metric-card">
      <div class="value" style="color:{risk_color}; text-shadow:0 0 15px {risk_color}66; font-size: 32px; padding-top:10px;">{regression_risk.replace('_', ' ').upper()}</div>
      <div class="label">Regression Risk</div>
    </div>
  </div>

  <div class="section">
    <h2>> STORY_PAYLOAD</h2>
    <div class="story-box">{story_text}</div>
    <p style="margin-top:16px;color:#a1a1aa;font-size:11px;font-family:'JetBrains Mono', monospace;">
      <span style="color:#22d3ee">SUMMARY:</span> {parsed_requirements.get("story_summary", "N/A")}<br><br>
      <span style="color:#22d3ee">RISK_AREAS:</span> {", ".join(parsed_requirements.get("risk_areas", []))}
    </p>
  </div>

  <div class="section">
    <h2>> EXECUTION_LOGS ({pass_rate}% SUCCESS_RATE)</h2>
    {result_rows}
  </div>

  <div class="section">
    <h2>> REGRESSION_ANALYSIS</h2>
    <p style="margin-bottom:16px;color:#d4d4d8;font-size:14px;line-height:1.5;">{regression_analysis.get("regression_summary", "")}</p>
    {regression_rows}
    {"<h3 style='margin-top:24px;margin-bottom:8px;font-size:11px;font-family:\"JetBrains Mono\", monospace;color:#22d3ee;letter-spacing:1px;'>RECOMMENDATIONS:</h3><ul style='padding-left:16px;color:#a1a1aa;font-size:13px;line-height:1.6;'>" + recommendations_html + "</ul>" if recommendations_html else ""}
  </div>

  <div class="section" style="margin-bottom:40px;">
    <h2>> SYSTEM_TRACE</h2>
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
