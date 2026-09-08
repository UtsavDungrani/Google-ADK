"""
ADK Evaluation HTML Report Generator.
Converts Google ADK eval_results.csv and evalset definitions into clean,
interactive, and highly readable HTML tables matching the tabular format
response produced during Python test runs.
"""

import os
import sys
import csv
import json
import re
import html
import datetime
from typing import List, Dict, Any, Optional, Tuple


def _escape(text: Optional[str]) -> str:
    """Safely escape text for HTML insertion."""
    if text is None:
        return ""
    return html.escape(str(text))


def _format_inline_md(line: str) -> str:
    """Formats bold, italic, and inline code within a single line."""
    # Inline code (`code`)
    line = re.sub(r"`([^`]+)`", r"<code class='inline-code'>\1</code>", line)
    # Bold (**bold**)
    line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", line)
    # Italic (*italic*)
    line = re.sub(r"(?<!\*)\*([^*\n\s][^*\n]*?[^*\n\s]|\S)\*(?!\*)", r"<em>\1</em>", line)
    return line


def _format_cell_markdown(text: Optional[str]) -> str:
    """
    Renders multiline markdown text cleanly inside a table cell.
    Preserves linebreaks, lists, bold, and code formatting with compact spacing.
    """
    if not text or not str(text).strip():
        return "<span class='cell-empty'>None</span>"

    escaped = html.escape(str(text).strip())

    # Code blocks (triple backticks)
    escaped = re.sub(
        r"```(?:[a-zA-Z0-9_-]+)?\n?(.*?)```",
        r"<pre class='cell-code-block'><code>\1</code></pre>",
        escaped,
        flags=re.DOTALL
    )

    lines = escaped.split("\n")
    formatted_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("* ", "- ", "• ")):
            if not in_list:
                formatted_lines.append("<ul class='cell-list'>")
                in_list = "ul"
            content = stripped[2:].strip()
            formatted_lines.append(f"<li>{_format_inline_md(content)}</li>")
        elif re.match(r"^\d+\.\s+", stripped):
            if not in_list:
                formatted_lines.append("<ol class='cell-list'>")
                in_list = "ol"
            content = re.sub(r"^\d+\.\s+", "", stripped)
            formatted_lines.append(f"<li>{_format_inline_md(content)}</li>")
        else:
            if in_list:
                tag = "</ul>" if in_list == "ul" else "</ol>"
                formatted_lines.append(tag)
                in_list = False
            if stripped:
                formatted_lines.append(f"<p class='cell-p'>{_format_inline_md(line)}</p>")
            else:
                formatted_lines.append("<div class='cell-spacer'></div>")

    if in_list:
        tag = "</ul>" if in_list == "ul" else "</ol>"
        formatted_lines.append(tag)

    return "".join(formatted_lines)


def _format_tool_calls_cell(raw_text: Optional[str]) -> str:
    """
    Formats tool calls inside a table cell.
    Highlights tool function names, wraps arguments in readable monospace blocks.
    """
    if not raw_text or not str(raw_text).strip():
        return "<span class='cell-empty'>None (No tools called)</span>"

    lines = str(raw_text).strip().split("\n")
    html_items = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        name_match = re.search(r"name='([^']+)'", line)
        tool_name = name_match.group(1) if name_match else None

        args_match = re.search(r"args=(\{.*?\})(?:\s+name=|\s+partial_args=|$)", line)
        args_str = args_match.group(1) if args_match else ""

        id_match = re.search(r"id=(?:'([^']*)'|None)", line)
        call_id = id_match.group(1) if (id_match and id_match.group(1)) else ""

        # Format arguments
        clean_args = args_str
        try:
            import ast
            parsed_dict = ast.literal_eval(args_str)
            if isinstance(parsed_dict, dict):
                clean_args = json.dumps(parsed_dict, indent=2)
        except Exception:
            clean_args = args_str

        if tool_name:
            id_tag = f"<span class='call-id'>({html.escape(call_id)})</span>" if call_id else ""
            html_items.append(f"""
            <div class="tool-call-item">
              <div class="tool-name-badge">⚡ {html.escape(tool_name)} {id_tag}</div>
              <pre class="tool-args-block">{html.escape(clean_args)}</pre>
            </div>
            """)
        else:
            html_items.append(f"<pre class='tool-args-block'>{html.escape(line)}</pre>")

    return "".join(html_items)


_format_markdown_snippet = _format_cell_markdown


def _parse_tool_calls(raw_text: Optional[str]) -> List[Dict[str, Any]]:
    """Parses Google ADK tool calls into structured dictionaries."""
    if not raw_text or not str(raw_text).strip():
        return []

    results = []
    lines = str(raw_text).strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        name_match = re.search(r"name='([^']+)'", line)
        tool_name = name_match.group(1) if name_match else "unknown_tool"

        id_match = re.search(r"id=(?:'([^']*)'|None)", line)
        call_id = id_match.group(1) if (id_match and id_match.group(1)) else None

        args_match = re.search(r"args=(\{.*?\})(?:\s+name=|\s+partial_args=|$)", line)
        args_str = args_match.group(1) if args_match else "{}"

        clean_args = args_str
        try:
            import ast
            parsed_dict = ast.literal_eval(args_str)
            if isinstance(parsed_dict, dict):
                clean_args = json.dumps(parsed_dict, indent=2)
        except Exception:
            clean_args = args_str

        results.append({
            "name": tool_name,
            "args_formatted": clean_args,
            "call_id": call_id,
            "raw": line
        })
    return results


def _human_metric_name(metric_name: str) -> str:
    """Converts metric identifier to human-friendly display label."""
    mapping = {
        "response_match_score": "Lexical Response Match (ROUGE-1)",
        "rubric_based_final_response_quality_v1": "Rubric Final Response Quality",
        "rubric_based_tool_use_quality_v1": "Rubric Tool Use Quality"
    }
    return mapping.get(metric_name, metric_name.replace("_", " ").title())


def _human_case_title(case_id: str) -> str:
    """Converts case_id like case_01_order_tracking to clean title."""
    cleaned = re.sub(r"^case_\d+_", "", case_id)
    return cleaned.replace("_", " ").title()


def load_evalset_metadata(evalset_path: Optional[str] = None) -> Dict[str, Any]:
    """Loads additional context like rubrics and descriptions from evalset.json."""
    if not evalset_path or not os.path.exists(evalset_path):
        return {}

    try:
        with open(evalset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        metadata = {
            "eval_set_id": data.get("eval_set_id", ""),
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "cases": {}
        }
        for case in data.get("eval_cases", []):
            cid = case.get("eval_id")
            conversation = case.get("conversation", [])
            turns_meta = []
            all_rubrics = []
            for inv_idx, inv in enumerate(conversation, start=1):
                rubrics = []
                for r in inv.get("rubrics", []):
                    entry = {
                        "rubric_id": r.get("rubric_id", ""),
                        "type": r.get("type", ""),
                        "text": (r.get("rubric_content") or {}).get("text_property", "")
                    }
                    rubrics.append(entry)
                    all_rubrics.append(entry)
                turns_meta.append({
                    "turn_idx": inv_idx,
                    "rubrics": rubrics
                })
            metadata["cases"][cid] = {
                "total_turns": len(conversation),
                "turns": turns_meta,
                "rubrics": all_rubrics
            }
        return metadata
    except Exception:
        return {}


def parse_csv_runs(csv_path: str) -> List[Dict[str, Any]]:
    """
    Parses eval_results.csv into distinct execution runs.
    Accurately supports both single-turn and multi-turn conversational evaluations.
    """
    if not os.path.exists(csv_path):
        return []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return []

    # Segment rows into runs: a new run starts when a (eval_id, metric_name, prompt) repeats
    runs_data = []
    current_run_rows = []
    seen_in_current_run = set()

    for row in rows:
        key = (row.get("eval_id", ""), row.get("metric_name", ""), row.get("prompt", ""))
        if key in seen_in_current_run:
            if current_run_rows:
                runs_data.append(current_run_rows)
            current_run_rows = [row]
            seen_in_current_run = {key}
        else:
            current_run_rows.append(row)
            seen_in_current_run.add(key)

    if current_run_rows:
        runs_data.append(current_run_rows)

    parsed_runs = []
    total_runs = len(runs_data)

    for run_idx, run_rows in enumerate(runs_data, start=1):
        is_latest = (run_idx == total_runs)

        # Track prompt sequence per case to identify turn numbers (Turn 1, Turn 2, Turn 3)
        case_prompts: Dict[str, List[str]] = {}
        for r in run_rows:
            eid = r.get("eval_id", "unknown_case")
            p = r.get("prompt", "")
            if eid not in case_prompts:
                case_prompts[eid] = []
            if p not in case_prompts[eid]:
                case_prompts[eid].append(p)

        # Invocations dictionary keyed by (eval_id, prompt)
        invocations_dict: Dict[Tuple[str, str], Dict[str, Any]] = {}
        metrics_dict: Dict[str, List[Dict[str, Any]]] = {}
        processed_rows = []

        for r in run_rows:
            eid = r.get("eval_id", "unknown_case")
            mname = r.get("metric_name", "unknown_metric")
            prompt_text = r.get("prompt", "")
            turns_list = case_prompts.get(eid, [prompt_text])
            turn_idx = (turns_list.index(prompt_text) + 1) if prompt_text in turns_list else 1
            total_turns = len(turns_list)

            row_entry = {
                "eval_set_id": r.get("eval_set_id", ""),
                "eval_id": eid,
                "turn_idx": turn_idx,
                "total_turns": total_turns,
                "metric_name": mname,
                "threshold": float(r.get("threshold", 0.0) or 0.0),
                "score": float(r.get("score", 0.0) or 0.0),
                "eval_status": r.get("eval_status", "UNKNOWN"),
                "prompt": prompt_text,
                "expected_response": r.get("expected_response", ""),
                "actual_response": r.get("actual_response", ""),
                "expected_tool_calls": r.get("expected_tool_calls", ""),
                "actual_tool_calls": r.get("actual_tool_calls", ""),
            }
            processed_rows.append(row_entry)

            # Add to metric grouping
            if mname not in metrics_dict:
                metrics_dict[mname] = []
            metrics_dict[mname].append(row_entry)

            # Add to invocations grouping
            inv_key = (eid, prompt_text)
            if inv_key not in invocations_dict:
                invocations_dict[inv_key] = {
                    "eval_id": eid,
                    "turn_idx": turn_idx,
                    "total_turns": total_turns,
                    "prompt": prompt_text,
                    "expected_response": row_entry["expected_response"],
                    "actual_response": row_entry["actual_response"],
                    "expected_tool_calls": row_entry["expected_tool_calls"],
                    "actual_tool_calls": row_entry["actual_tool_calls"],
                    "metrics": [],
                    "overall_status": "PASSED"
                }

            invocations_dict[inv_key]["metrics"].append({
                "metric_name": mname,
                "threshold": row_entry["threshold"],
                "score": row_entry["score"],
                "status": row_entry["eval_status"]
            })
            if row_entry["eval_status"] != "PASSED":
                invocations_dict[inv_key]["overall_status"] = "FAILED"

        cases_list = list(invocations_dict.values())
        unique_case_ids = sorted(list(set(c["eval_id"] for c in cases_list)))
        total_cases = len(unique_case_ids)

        # Unique scenario pass/fail: passes only if all turns of that scenario pass
        case_status_map: Dict[str, str] = {}
        for c in cases_list:
            cid = c["eval_id"]
            if cid not in case_status_map:
                case_status_map[cid] = "PASSED"
            if c["overall_status"] != "PASSED":
                case_status_map[cid] = "FAILED"

        passed_cases = sum(1 for cid, stat in case_status_map.items() if stat == "PASSED")
        failed_cases = total_cases - passed_cases
        case_pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0.0

        total_metrics = len(run_rows)
        passed_metrics = sum(1 for r in run_rows if r.get("eval_status") == "PASSED")
        failed_metrics = total_metrics - passed_metrics
        metric_pass_rate = (passed_metrics / total_metrics * 100) if total_metrics > 0 else 0.0

        # Summary for each metric
        metrics_summary = []
        for mname, mrows in metrics_dict.items():
            scores = [r["score"] for r in mrows]
            passed = sum(1 for r in mrows if r["eval_status"] == "PASSED")
            failed = len(mrows) - passed
            thresh = mrows[0]["threshold"] if mrows else 0.0
            avg_score = sum(scores) / len(scores) if scores else 0.0
            overall_status = "PASSED" if failed == 0 else "FAILED"
            metrics_summary.append({
                "metric_name": mname,
                "threshold": thresh,
                "count": len(mrows),
                "passed": passed,
                "failed": failed,
                "avg_score": avg_score,
                "pass_rate": (passed / len(mrows) * 100) if mrows else 0.0,
                "overall_status": overall_status,
                "rows": mrows
            })

        parsed_runs.append({
            "run_index": run_idx,
            "run_name": f"Run #{run_idx}" + (" (Latest)" if is_latest else ""),
            "is_latest": is_latest,
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "case_pass_rate": round(case_pass_rate, 1),
            "total_metrics": total_metrics,
            "passed_metrics": passed_metrics,
            "failed_metrics": failed_metrics,
            "metric_pass_rate": round(metric_pass_rate, 1),
            "metrics_summary": metrics_summary,
            "cases": cases_list,
            "rows": processed_rows
        })

    return parsed_runs


def generate_html_content(
    runs: List[Dict[str, Any]],
    evalset_meta: Dict[str, Any],
    source_csv_name: str = "evals/eval_results.csv"
) -> str:
    """Renders comprehensive HTML with easy-to-read tables and minimal clean CSS."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eval_set_id = evalset_meta.get("eval_set_id", "customer_care_evals")
    eval_set_name = evalset_meta.get("name", "Customer Care Benchmark Eval Set")

    total_runs_count = len(runs)
    latest_run = runs[-1] if runs else None

    # Cumulative calculations
    all_total_cases = sum(r["total_cases"] for r in runs)
    all_passed_cases = sum(r["passed_cases"] for r in runs)
    all_pass_rate = round((all_passed_cases / all_total_cases * 100), 1) if all_total_cases > 0 else 0.0

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ADK Evaluation Tabular Report &bull; {eval_set_name}</title>
  <style>
    /* Minimal Modern CSS for ADK Tabular Evaluation Report */
    :root {{
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #cbd5e1;
      --border-light: #e2e8f0;
      --th-bg: #f1f5f9;
      --tr-even: #f8fafc;
      --tr-hover: #f1f5f9;
      --pass-bg: #dcfce7;
      --pass-text: #15803d;
      --pass-border: #86efac;
      --fail-bg: #fee2e2;
      --fail-text: #b91c1c;
      --fail-border: #fca5a5;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --tool-bg: #f8fafc;
      --tool-border: #cbd5e1;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.45;
      padding: 20px 24px 60px;
    }}

    .container {{
      max-width: 100%;
      margin: 0 auto;
    }}

    /* Header */
    header.report-header {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px 24px;
      margin-bottom: 20px;
      box-shadow: var(--shadow-sm);
    }}
    .header-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }}
    h1.report-title {{
      font-size: 1.45rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .meta-subtitle {{
      font-size: 0.86rem;
      color: var(--text-muted);
      margin-top: 4px;
    }}
    .meta-badge {{
      display: inline-block;
      background: #f1f5f9;
      border: 1px solid var(--border-light);
      padding: 2px 8px;
      border-radius: 4px;
      font-family: ui-monospace, monospace;
      font-size: 0.82rem;
      color: #334155;
    }}
    .timestamp-badge {{
      font-size: 0.82rem;
      color: var(--text-muted);
      background: #ffffff;
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 6px;
      white-space: nowrap;
    }}

    /* KPI Summary Row */
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px 16px;
      box-shadow: var(--shadow-sm);
    }}
    .kpi-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 600;
    }}
    .kpi-value {{
      font-size: 1.5rem;
      font-weight: 700;
      margin: 4px 0 2px;
    }}
    .kpi-hint {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}
    .text-pass {{ color: var(--pass-text); }}
    .text-fail {{ color: var(--fail-text); }}

    /* Toolbar */
    .toolbar {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 12px 16px;
      margin-bottom: 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      box-shadow: var(--shadow-sm);
    }}
    .toolbar-left, .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .btn {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 0.84rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.1s ease;
    }}
    .btn:hover {{
      background: #f1f5f9;
      border-color: #94a3b8;
    }}
    .btn.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}
    .search-input {{
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 0.84rem;
      width: 240px;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.15);
    }}
    .select-dropdown {{
      padding: 6px 10px;
      border: 1px solid var(--border);
      border-radius: 4px;
      font-size: 0.84rem;
      background: #ffffff;
      cursor: pointer;
    }}

    /* View Switcher Tabs */
    .tabs-bar {{
      display: flex;
      gap: 6px;
      margin-bottom: 16px;
      border-bottom: 2px solid var(--border-light);
      padding-bottom: 0;
    }}
    .tab-btn {{
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      padding: 8px 16px;
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      margin-bottom: -2px;
    }}
    .tab-btn:hover {{
      color: var(--text);
    }}
    .tab-btn.active {{
      color: var(--primary);
      border-bottom-color: var(--primary);
    }}

    /* Table Container & Grid Styles */
    .table-container {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow-x: auto;
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }}

    .section-banner {{
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .section-banner-title {{
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .adk-summary-tag {{
      font-family: ui-monospace, monospace;
      font-size: 0.82rem;
      background: #ffffff;
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 4px;
      color: #334155;
    }}

    table.adk-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }}
    table.adk-table th {{
      background-color: var(--th-bg);
      color: #334155;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.74rem;
      letter-spacing: 0.04em;
      padding: 9px 12px;
      border: 1px solid var(--border);
      white-space: nowrap;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    table.adk-table td {{
      padding: 10px 12px;
      border: 1px solid var(--border);
      vertical-align: top;
      line-height: 1.45;
    }}
    table.adk-table tbody tr:nth-child(even) {{
      background-color: var(--tr-even);
    }}
    table.adk-table tbody tr:hover {{
      background-color: var(--tr-hover);
    }}

    /* Column Sizing Helpers */
    .col-idx {{ width: 38px; text-align: center; font-weight: 600; color: var(--text-muted); }}
    .col-status {{ width: 95px; text-align: center; }}
    .col-score {{ width: 75px; text-align: right; font-family: ui-monospace, monospace; font-weight: 700; }}
    .col-threshold {{ width: 75px; text-align: right; font-family: ui-monospace, monospace; color: var(--text-muted); }}
    .col-case-id {{ width: 170px; font-family: ui-monospace, monospace; font-size: 0.82rem; }}
    .col-metric {{ width: 180px; font-family: ui-monospace, monospace; font-size: 0.8rem; }}
    .col-prompt {{ min-width: 220px; max-width: 320px; }}
    .col-expected {{ min-width: 250px; max-width: 380px; }}
    .col-actual {{ min-width: 280px; max-width: 440px; }}
    .col-tools {{ min-width: 230px; max-width: 380px; }}

    /* Status Badges */
    .badge {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-align: center;
      white-space: nowrap;
    }}
    .badge-pass {{
      background: var(--pass-bg);
      color: var(--pass-text);
      border: 1px solid var(--pass-border);
    }}
    .badge-fail {{
      background: var(--fail-bg);
      color: var(--fail-text);
      border: 1px solid var(--fail-border);
    }}
    .badge-turn {{
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      font-size: 0.72rem;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
      margin-left: 6px;
      display: inline-block;
      vertical-align: middle;
    }}

    /* Markdown inside cells */
    .cell-p {{ margin-bottom: 6px; }}
    .cell-p:last-child {{ margin-bottom: 0; }}
    .cell-list {{ padding-left: 18px; margin-bottom: 6px; }}
    .cell-list li {{ margin-bottom: 3px; }}
    .cell-spacer {{ height: 6px; }}
    .inline-code {{
      background: #f1f5f9;
      color: #0f172a;
      padding: 1px 4px;
      border-radius: 3px;
      font-family: ui-monospace, monospace;
      font-size: 0.84em;
    }}
    .cell-code-block {{
      background: #0f172a;
      color: #f1f5f9;
      padding: 8px 10px;
      border-radius: 4px;
      font-family: ui-monospace, monospace;
      font-size: 0.78rem;
      white-space: pre-wrap;
      word-break: break-all;
      margin: 6px 0;
    }}
    .cell-empty {{
      color: #94a3b8;
      font-style: italic;
      font-size: 0.82rem;
    }}

    /* Tool Call Card inside cell */
    .tool-call-item {{
      background: #ffffff;
      border: 1px solid var(--tool-border);
      border-radius: 4px;
      padding: 6px 8px;
      margin-bottom: 6px;
    }}
    .tool-call-item:last-child {{ margin-bottom: 0; }}
    .tool-name-badge {{
      font-family: ui-monospace, monospace;
      font-size: 0.8rem;
      font-weight: 700;
      color: #1e40af;
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 4px;
    }}
    .call-id {{
      font-size: 0.72rem;
      font-weight: normal;
      color: #64748b;
    }}
    .tool-args-block {{
      background: var(--tool-bg);
      border: 1px solid #e2e8f0;
      border-radius: 3px;
      padding: 4px 6px;
      font-family: ui-monospace, monospace;
      font-size: 0.76rem;
      color: #334155;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    /* Compact / Expand Toggle */
    .expand-toggle-btn {{
      font-size: 0.72rem;
      color: var(--primary);
      cursor: pointer;
      background: none;
      border: none;
      padding: 2px 0;
      text-decoration: underline;
    }}

    /* Footer */
    footer.report-footer {{
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-muted);
      margin-top: 30px;
      padding-top: 16px;
      border-top: 1px solid var(--border-light);
    }}

    /* Print optimization */
    @media print {{
      body {{ background: #fff; padding: 0; }}
      .toolbar, .tabs-bar, .btn {{ display: none !important; }}
      table.adk-table {{ font-size: 0.72rem; }}
      table.adk-table th, table.adk-table td {{ padding: 4px 6px; }}
    }}
  </style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <header class="report-header">
    <div class="header-top">
      <div>
        <h1 class="report-title">
          <span>📋</span> Google ADK Evaluation &bull; Tabular Results Report
        </h1>
        <div class="meta-subtitle">
          Dataset: <span class="meta-badge">{_escape(eval_set_id)}</span> &bull; 
          Target Agent: <span class="meta-badge">customer_care.agent (root_agent)</span> &bull;
          Source Ledger: <span class="meta-badge">{_escape(os.path.basename(source_csv_name))}</span>
        </div>
      </div>
      <div>
        <div class="timestamp-badge">📅 Generated: {now_str}</div>
      </div>
    </div>
  </header>
""")

    cur_run = latest_run if latest_run else {
        "total_cases": 0, "passed_cases": 0, "failed_cases": 0,
        "case_pass_rate": 0.0, "total_metrics": 0, "passed_metrics": 0,
        "failed_metrics": 0, "metric_pass_rate": 0.0
    }

    pass_class = "text-pass" if cur_run["case_pass_rate"] >= 80.0 else "text-fail"

    # Top KPI Metrics Row
    html_parts.append(f"""
  <!-- KPI Metrics Row -->
  <div class="kpi-row">
    <div class="kpi-card">
      <div class="kpi-label">Scenario Pass Rate</div>
      <div class="kpi-value {pass_class}">{cur_run['case_pass_rate']}%</div>
      <div class="kpi-hint"><strong>{cur_run['passed_cases']}</strong> / {cur_run['total_cases']} scenarios passed</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Metric Thresholds</div>
      <div class="kpi-value">{cur_run['passed_metrics']} <span style="font-size: 0.95rem; color: var(--text-muted); font-weight: normal;">/ {cur_run['total_metrics']}</span></div>
      <div class="kpi-hint">{cur_run['metric_pass_rate']}% satisfied</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Evaluation Runs</div>
      <div class="kpi-value">{total_runs_count}</div>
      <div class="kpi-hint">Cumulative pass: {all_pass_rate}%</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-label">Status</div>
      <div class="kpi-value {'text-pass' if cur_run['failed_cases'] == 0 else 'text-fail'}">
        {"PASSED" if cur_run['failed_cases'] == 0 else "FAILURES"}
      </div>
      <div class="kpi-hint">{"All criteria satisfied" if cur_run['failed_cases'] == 0 else f"{cur_run['failed_cases']} case(s) below threshold"}</div>
    </div>
  </div>

  <!-- Toolbar Controls -->
  <div class="toolbar">
    <div class="toolbar-left">
      <span style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted);">FILTER:</span>
      <button class="btn active" onclick="filterTableRows('all', this)">All Rows</button>
      <button class="btn" onclick="filterTableRows('passed', this)">Passed Only</button>
      <button class="btn" onclick="filterTableRows('failed', this)">Failed Only</button>
    </div>

    <div class="toolbar-right">
      <input type="text" id="tableSearch" class="search-input" placeholder="Search tables (case, prompt, tool, etc.)..." onkeyup="searchTables()">
""")

    if total_runs_count > 1:
        html_parts.append("""
      <select id="runSelector" class="select-dropdown" onchange="switchRun(this.value)">
""")
        for r in runs:
            selected_attr = "selected" if r["is_latest"] else ""
            html_parts.append(f"""        <option value="run_container_{r['run_index']}" {selected_attr}>{r['run_name']} ({r['case_pass_rate']}% pass)</option>\n""")
        html_parts.append("""      </select>\n""")

    html_parts.append("""
    </div>
  </div>

  <!-- View Switcher Tabs -->
  <div class="tabs-bar">
    <button class="tab-btn active" onclick="switchTab('tab_master', this)">📋 Master Tabular Grid (All Columns & Rows)</button>
    <button class="tab-btn" onclick="switchTab('tab_by_metric', this)">📊 ADK Metric Tables (_print_details format)</button>
    <button class="tab-btn" onclick="switchTab('tab_by_scenario', this)">📑 Scenario Matrix</button>
    <button class="tab-btn" onclick="switchTab('tab_history', this)">📈 Run History</button>
  </div>
""")

    # Render Run Containers
    for run in runs:
        run_container_id = f"run_container_{run['run_index']}"
        container_style = "block" if run["is_latest"] else "none"

        html_parts.append(f"""
  <!-- Run Container: {run['run_name']} -->
  <div id="{run_container_id}" class="run-container" style="display: {container_style};">

    <!-- TAB 1: MASTER TABULAR GRID (All Columns exactly as evaluated) -->
    <div id="{run_container_id}_tab_master" class="tab-panel" style="display: block;">
      <div class="table-container">
        <div class="section-banner">
          <div class="section-banner-title">
            <span>📋 Full Evaluation Results Table</span>
            <span class="adk-summary-tag">{len(run['rows'])} Invocations &bull; {run['run_name']}</span>
          </div>
          <div>
            <span class="badge {'badge-pass' if run['failed_metrics'] == 0 else 'badge-fail'}">
              {run['passed_metrics']} / {run['total_metrics']} PASSED
            </span>
          </div>
        </div>

        <table class="adk-table" id="{run_container_id}_master_table">
          <thead>
            <tr>
              <th class="col-idx">#</th>
              <th class="col-status">eval_status</th>
              <th class="col-case-id">eval_id</th>
              <th class="col-metric">metric_name</th>
              <th class="col-score">score</th>
              <th class="col-threshold">threshold</th>
              <th class="col-prompt">prompt</th>
              <th class="col-expected">expected_response</th>
              <th class="col-actual">actual_response</th>
              <th class="col-tools">expected_tool_calls</th>
              <th class="col-tools">actual_tool_calls</th>
            </tr>
          </thead>
          <tbody>
""")

        for row_idx, r in enumerate(run["rows"], start=1):
            status = r.get("eval_status", "UNKNOWN")
            badge_class = "badge-pass" if status == "PASSED" else "badge-fail"
            try:
                score_val = float(r.get("score", 0.0) or 0.0)
                thresh_val = float(r.get("threshold", 0.0) or 0.0)
            except ValueError:
                score_val, thresh_val = 0.0, 0.0

            search_blob = f"{r.get('eval_id', '')} {r.get('metric_name', '')} {status} {r.get('prompt', '')} {r.get('actual_tool_calls', '')}".lower()

            html_parts.append(f"""
            <tr data-status="{status.lower()}" data-search="{_escape(search_blob)}">
              <td class="col-idx">{row_idx}</td>
              <td class="col-status">
                <span class="badge {badge_class}">{_escape(status)}</span>
              </td>
              <td class="col-case-id">
                <strong>{_escape(r.get('eval_id', ''))}</strong>
                {f'<span class="badge-turn">Turn {r.get("turn_idx", 1)}/{r.get("total_turns", 1)}</span>' if r.get("total_turns", 1) > 1 else ''}
              </td>
              <td class="col-metric">
                <code>{_escape(r.get('metric_name', ''))}</code>
              </td>
              <td class="col-score { 'text-pass' if status == 'PASSED' else 'text-fail' }">
                {score_val:.4f}
              </td>
              <td class="col-threshold">
                ≥ {thresh_val:.2f}
              </td>
              <td class="col-prompt">
                {_format_cell_markdown(r.get('prompt', ''))}
              </td>
              <td class="col-expected">
                {_format_cell_markdown(r.get('expected_response', ''))}
              </td>
              <td class="col-actual">
                {_format_cell_markdown(r.get('actual_response', ''))}
              </td>
              <td class="col-tools">
                {_format_tool_calls_cell(r.get('expected_tool_calls', ''))}
              </td>
              <td class="col-tools">
                {_format_tool_calls_cell(r.get('actual_tool_calls', ''))}
              </td>
            </tr>
""")

        html_parts.append("""
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 2: ADK METRIC TABLES (_print_details tabular format) -->
    <div id=\"""" + run_container_id + """_tab_by_metric" class="tab-panel" style="display: none;">
""")

        for m in run["metrics_summary"]:
            m_status = m["overall_status"]
            badge_class = "badge-pass" if m_status == "PASSED" else "badge-fail"

            html_parts.append(f"""
      <div class="table-container">
        <div class="section-banner">
          <div class="section-banner-title">
            <span>📊 Metric Table: <code>{_escape(m['metric_name'])}</code></span>
            <span class="adk-summary-tag">Expected threshold: &ge; {m['threshold']:.2f}, actual average: {m['avg_score']:.4f}</span>
          </div>
          <div>
            <span class="badge {badge_class}">
              Summary: `{m_status}` ({m['passed']}/{m['count']} Passed)
            </span>
          </div>
        </div>

        <table class="adk-table">
          <thead>
            <tr>
              <th class="col-idx">#</th>
              <th class="col-status">eval_status</th>
              <th class="col-score">score</th>
              <th class="col-threshold">threshold</th>
              <th class="col-case-id">eval_id</th>
              <th class="col-prompt">prompt</th>
              <th class="col-expected">expected_response</th>
              <th class="col-actual">actual_response</th>
              <th class="col-tools">expected_tool_calls</th>
              <th class="col-tools">actual_tool_calls</th>
            </tr>
          </thead>
          <tbody>
""")

            for idx, r in enumerate(m["rows"], start=1):
                row_status = r["eval_status"]
                row_badge = "badge-pass" if row_status == "PASSED" else "badge-fail"
                search_blob = f"{r['eval_id']} {m['metric_name']} {row_status} {r['prompt']} {r['actual_tool_calls']}".lower()

                html_parts.append(f"""
            <tr data-status="{row_status.lower()}" data-search="{_escape(search_blob)}">
              <td class="col-idx">{idx}</td>
              <td class="col-status">
                <span class="badge {row_badge}">{_escape(row_status)}</span>
              </td>
              <td class="col-score { 'text-pass' if row_status == 'PASSED' else 'text-fail' }">
                {r['score']:.4f}
              </td>
              <td class="col-threshold">
                ≥ {r['threshold']:.2f}
              </td>
              <td class="col-case-id">
                <strong>{_escape(r['eval_id'])}</strong>
                {f'<span class="badge-turn">Turn {r.get("turn_idx", 1)}/{r.get("total_turns", 1)}</span>' if r.get("total_turns", 1) > 1 else ''}
              </td>
              <td class="col-prompt">
                {_format_cell_markdown(r['prompt'])}
              </td>
              <td class="col-expected">
                {_format_cell_markdown(r['expected_response'])}
              </td>
              <td class="col-actual">
                {_format_cell_markdown(r['actual_response'])}
              </td>
              <td class="col-tools">
                {_format_tool_calls_cell(r['expected_tool_calls'])}
              </td>
              <td class="col-tools">
                {_format_tool_calls_cell(r['actual_tool_calls'])}
              </td>
            </tr>
""")

            html_parts.append("""
          </tbody>
        </table>
      </div>
""")

        html_parts.append("""
    </div>

    <!-- TAB 3: SCENARIO MATRIX (Consolidated by Case) -->
    <div id=\"""" + run_container_id + """_tab_by_scenario" class="tab-panel" style="display: none;">
      <div class="table-container">
        <div class="section-banner">
          <div class="section-banner-title">
            <span>📑 Consolidated Scenario Matrix</span>
            <span class="adk-summary-tag">""" + str(run['total_cases']) + """ Test Scenarios</span>
          </div>
          <div>
            <span class="badge """ + ('badge-pass' if run['failed_cases'] == 0 else 'badge-fail') + """">
              """ + str(run['passed_cases']) + """ / """ + str(run['total_cases']) + """ Scenarios Passed
            </span>
          </div>
        </div>

        <table class="adk-table">
          <thead>
            <tr>
              <th class="col-idx">#</th>
              <th class="col-status">Overall</th>
              <th class="col-case-id">Scenario (eval_id)</th>
              <th class="col-prompt">User Prompt</th>
              <th style="width: 220px;">Metric Scores</th>
              <th class="col-expected">Expected Response</th>
              <th class="col-actual">Actual Model Response</th>
              <th class="col-tools">Tool Execution</th>
            </tr>
          </thead>
          <tbody>
""")

        for case_idx, case in enumerate(run["cases"], start=1):
            c_status = case["overall_status"]
            c_badge = "badge-pass" if c_status == "PASSED" else "badge-fail"

            metric_pills = []
            for m in case["metrics"]:
                m_color = "var(--pass-text)" if m["status"] == "PASSED" else "var(--fail-text)"
                short_name = m["metric_name"].replace("rubric_based_", "").replace("_quality_v1", "").replace("_score", "")
                metric_pills.append(f"""
                <div style="font-size: 0.78rem; font-family: monospace; margin-bottom: 2px;">
                  <strong style="color: {m_color};">{short_name}:</strong> {m['score']:.2f} (thresh &ge; {m['threshold']:.2f})
                </div>
                """)
            metric_pills_html = "".join(metric_pills)

            search_blob = f"{case['eval_id']} {c_status} {case['prompt']}".lower()

            html_parts.append(f"""
            <tr data-status="{c_status.lower()}" data-search="{_escape(search_blob)}">
              <td class="col-idx">{case_idx}</td>
              <td class="col-status">
                <span class="badge {c_badge}">{_escape(c_status)}</span>
              </td>
              <td class="col-case-id">
                <strong>{_escape(_human_case_title(case['eval_id']))}</strong>
                {f'<span class="badge-turn">Turn {case.get("turn_idx", 1)}/{case.get("total_turns", 1)}</span>' if case.get("total_turns", 1) > 1 else ''}
                <div style="font-size: 0.75rem; color: var(--text-muted);">{_escape(case['eval_id'])}</div>
              </td>
              <td class="col-prompt">
                {_format_cell_markdown(case['prompt'])}
              </td>
              <td>
                {metric_pills_html}
              </td>
              <td class="col-expected">
                {_format_cell_markdown(case['expected_response'])}
              </td>
              <td class="col-actual">
                {_format_cell_markdown(case['actual_response'])}
              </td>
              <td class="col-tools">
                <div style="font-size: 0.74rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Actual Tools:</div>
                {_format_tool_calls_cell(case['actual_tool_calls'])}
              </td>
            </tr>
""")

        html_parts.append("""
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: RUN HISTORY LEDGER -->
    <div id=\"""" + run_container_id + """_tab_history" class="tab-panel" style="display: none;">
      <div class="table-container">
        <div class="section-banner">
          <div class="section-banner-title">
            <span>📈 Historical Executions Ledger</span>
            <span class="adk-summary-tag">""" + str(total_runs_count) + """ Executions Recorded</span>
          </div>
        </div>

        <table class="adk-table">
          <thead>
            <tr>
              <th class="col-idx">Run #</th>
              <th>Run Label</th>
              <th>Scenarios Evaluated</th>
              <th>Scenarios Passed</th>
              <th>Scenarios Failed</th>
              <th>Scenario Pass Rate</th>
              <th>Metric Pass Rate</th>
              <th style="width: 120px;">Inspect Run</th>
            </tr>
          </thead>
          <tbody>
""")

        for r_hist in reversed(runs):
            hist_badge = '<span class="badge badge-pass">100.0%</span>' if r_hist['case_pass_rate'] == 100.0 else f'<span class="badge badge-fail">{r_hist["case_pass_rate"]}%</span>'
            html_parts.append(f"""
            <tr>
              <td class="col-idx">{r_hist['run_index']}</td>
              <td><strong>{_escape(r_hist['run_name'])}</strong></td>
              <td>{r_hist['total_cases']} scenarios</td>
              <td><span class="text-pass"><strong>{r_hist['passed_cases']}</strong></span></td>
              <td><span class="text-fail"><strong>{r_hist['failed_cases']}</strong></span></td>
              <td>{hist_badge}</td>
              <td><strong>{r_hist['metric_pass_rate']}%</strong> ({r_hist['passed_metrics']}/{r_hist['total_metrics']})</td>
              <td>
                <button class="btn" style="padding: 2px 8px; font-size: 0.78rem;" onclick="switchRun('run_container_{r_hist['run_index']}'); document.getElementById('runSelector').value='run_container_{r_hist['run_index']}';">
                  View Run
                </button>
              </td>
            </tr>
""")

        html_parts.append("""
          </tbody>
        </table>
      </div>
    </div>

  </div>
""")

    # Footer and minimal vanilla JavaScript
    html_parts.append("""
  <footer class="report-footer">
    Google Agent Development Kit (ADK) &bull; Customer Care Multi-Agent System &bull; Minimal CSS Tabular Report
  </footer>

</div>

<script>
  let activeTabName = 'tab_master';

  // Switch between tabs
  function switchTab(tabKey, btnElement) {
    activeTabName = tabKey;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (btnElement) btnElement.classList.add('active');

    const activeContainer = document.querySelector('.run-container[style*="display: block"]') || document.querySelector('.run-container');
    if (!activeContainer) return;

    activeContainer.querySelectorAll('.tab-panel').forEach(panel => {
      panel.style.display = panel.id.endsWith(tabKey) ? 'block' : 'none';
    });
  }

  // Switch between runs
  function switchRun(containerId) {
    document.querySelectorAll('.run-container').forEach(c => {
      c.style.display = (c.id === containerId) ? 'block' : 'none';
    });
    // Ensure active tab panel is visible in switched container
    const activeContainer = document.getElementById(containerId);
    if (activeContainer) {
      activeContainer.querySelectorAll('.tab-panel').forEach(panel => {
        panel.style.display = panel.id.endsWith(activeTabName) ? 'block' : 'none';
      });
    }
    searchTables();
  }

  // Filter table rows by status (all / passed / failed)
  function filterTableRows(status, btnElement) {
    const buttons = document.querySelectorAll('.toolbar-left .btn');
    buttons.forEach(b => {
      if (b.innerText.toLowerCase().includes(status) || (status === 'all' && b.innerText === 'All Rows')) {
        b.classList.add('active');
      } else if (b.getAttribute('onclick') && b.getAttribute('onclick').includes('filterTableRows')) {
        b.classList.remove('active');
      }
    });

    const activeContainer = document.querySelector('.run-container[style*="display: block"]') || document.querySelector('.run-container');
    if (!activeContainer) return;

    const rows = activeContainer.querySelectorAll('tbody tr[data-status]');
    rows.forEach(tr => {
      const rowStatus = tr.getAttribute('data-status');
      if (status === 'all' || rowStatus === status) {
        tr.style.display = '';
      } else {
        tr.style.display = 'none';
      }
    });
  }

  // Real-time search across all table rows
  function searchTables() {
    const query = document.getElementById('tableSearch').value.toLowerCase().trim();
    const activeContainer = document.querySelector('.run-container[style*="display: block"]') || document.querySelector('.run-container');
    if (!activeContainer) return;

    const rows = activeContainer.querySelectorAll('tbody tr[data-search]');
    rows.forEach(tr => {
      const searchBlob = tr.getAttribute('data-search') || '';
      if (!query || searchBlob.includes(query)) {
        tr.style.display = '';
      } else {
        tr.style.display = 'none';
      }
    });
  }
</script>

</body>
</html>
""")

    return "".join(html_parts)


def generate_html_report(
    csv_path: str = "evals/eval_results.csv",
    output_html_path: Optional[str] = None,
    evalset_path: Optional[str] = "evals/customer_care.evalset.json",
) -> str:
    """
    Main entry point: Reads eval_results.csv, combines with evalset metadata,
    and writes out the enhanced tabular eval_results.html report.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Evaluation results CSV '{csv_path}' not found.")

    if not output_html_path:
        output_html_path = csv_path.replace(".csv", ".html")
        if not output_html_path.endswith(".html"):
            output_html_path += ".html"

    runs = parse_csv_runs(csv_path)
    if not runs:
        raise ValueError(f"No evaluation records could be parsed from '{csv_path}'.")

    evalset_meta = load_evalset_metadata(evalset_path)
    html_content = generate_html_content(
        runs=runs,
        evalset_meta=evalset_meta,
        source_csv_name=csv_path
    )

    out_dir = os.path.dirname(os.path.abspath(output_html_path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_html_path)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate tabular HTML evaluation report from ADK CSV")
    parser.add_argument("--csv", default="evals/eval_results.csv", help="Input eval_results.csv path")
    parser.add_argument("--output", default="evals/eval_results.html", help="Output HTML file path")
    parser.add_argument("--evalset", default="evals/customer_care.evalset.json", help="EvalSet JSON path")

    args = parser.parse_args()
    report_path = generate_html_report(
        csv_path=args.csv,
        output_html_path=args.output,
        evalset_path=args.evalset
    )
    print("=" * 65)
    print("  ADK TABULAR EVALUATION HTML REPORT GENERATED")
    print("=" * 65)
    print(f"• Input CSV   : {args.csv}")
    print(f"• Output HTML : {report_path}")
    print("=" * 65)


if __name__ == "__main__":
    main()
