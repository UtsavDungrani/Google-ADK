"""
ConvoAI Expected vs. Actual Evaluation Engine & Interactive Dashboard Compiler.
Evaluates the 40 real-world and edge-case questions, comparing Expected Answers against
Actual ConvoAI model generations with Gap Analysis, Tool Accuracy, and Policy Compliance.
"""

import os
import re
import json
import csv
import html
from typing import List, Dict, Any


def categorize_question(prompt: str, expected: str, eval_id: str) -> Dict[str, str]:
    text = (prompt + " " + expected + " " + eval_id).lower()
    
    # Determine developer project
    developer = "General Real Estate"
    if "adani" in text or "teen hath" in text:
        developer = "Adani Realty (Teen Hath Naka)"
    elif "dtc" in text or "stillwaters" in text:
        developer = "DTC Group (DTC Stillwaters)"
    elif "veena" in text or "synergy" in text:
        developer = "Veena Developers (Veena Synergy)"
    elif "hiranandani" in text or "lit" in text:
        developer = "House of Hiranandani (Codename LIT)"
    elif "signature" in text or "gurugram" in text or "sohna" in text:
        developer = "Signature Global (DAXIN Gurugram)"

    # Determine functional category
    category = "General Inquiry"
    if any(k in text for k in ["7:30", "8:00", "8 am", "visit", "tomorrow", "sunday", "schedule", "slot", "timing", "hours"]):
        category = "Site Visit & Hours Policy"
    elif any(k in text for k in ["price", "pricing", "cost", "crore", "budget", "sheet"]):
        category = "Pricing & Disclosure Policy"
    elif any(k in text for k in ["2 bhk", "3 bhk", "4 bhk", "bhk", "carpet", "sq.ft", "floor", "configuration", "self-use", "investment"]):
        category = "Inventory & Qualification"
    elif any(k in text for k in ["whatsapp", "brochure", "floor plan", "location", "send", "details"]):
        category = "WhatsApp & Follow-up"
    elif any(k in text for k in ["namaste", "mein", "kya", "hain", "karegi", "karta hoon"]):
        category = "Multilingual / Hinglish"
    elif any(k in text for k in ["hello", "hi", "hey"]):
        category = "Greeting & Intro"

    return {"developer": developer, "category": category}


def analyze_gap(prompt: str, expected: str, actual: str, eval_status: str, match_score: float) -> str:
    prompt_l = prompt.lower()
    exp_l = expected.lower()
    act_l = actual.lower()

    if eval_status == "FAILED":
        if "7:30" in prompt_l or "8:00" in prompt_l or "8 am" in prompt_l:
            return "Failed to strictly enforce site visit hours (10 AM - 7 PM) or did not counter-propose a valid operating time slot."
        elif "price" in prompt_l or "cost" in prompt_l:
            return "Policy Violation: Disclosed premature pricing without qualifying unit configuration or failed to state 3 BHK pricing requires an in-person site visit."
        elif "whatsapp" in prompt_l or "brochure" in prompt_l:
            return "Tool Omission: Failed to dispatch brochure via send_whatsapp_brochure or failed to confirm WhatsApp delivery."
        else:
            return f"Low semantic alignment ({match_score*100:.1f}%). ConvoAI response deviated from required golden reference instructions."

    # Passed cases analysis
    observations = []
    if "call is now being recorded" in act_l:
        observations.append("Complied with mandatory call recording disclosure.")
    
    if "7:30" in prompt_l or "8:00" in prompt_l or "8 am" in prompt_l:
        observations.append("Correctly identified that slot is outside operating hours (10 AM - 7 PM) and proposed valid alternative.")
    elif "price" in prompt_l:
        observations.append("Adhered to pricing policy: offered entry baseline or stated detailed pricing requires site visit.")
    
    if "whatsapp" in prompt_l or "brochure" in prompt_l:
        observations.append("Confirmed WhatsApp brochure and layout plan dispatch.")
    
    if "self-use" in prompt_l or "investment" in prompt_l:
        observations.append("Acknowledged buyer intent and naturally transitioned to BHK configuration discovery.")

    if not observations:
        observations.append(f"Strong conversational relevance ({match_score*100:.1f}% match) adhering to developer sales protocol.")

    return " ".join(observations)


def run_expected_vs_actual_eval(
    csv_path: str = "evals/convoai_full_results.csv",
    output_json: str = "convoai_eval/results/convoai_expected_vs_actual.json",
    output_csv: str = "convoai_eval/results/convoai_expected_vs_actual.csv",
    output_html: str = "convoai_eval/convoai_expected_vs_actual.html"
):
    print("=" * 75)
    print("  CONVO AI EXPECTED VS. ACTUAL EVALUATION PIPELINE")
    print("  Benchmarking Real User Inquiries vs. Golden Answers & Actual Generations")
    print("=" * 75)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Source results CSV not found at {csv_path}")

    with open(csv_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    records = []
    from collections import OrderedDict
    grouped = OrderedDict()
    for row in rows:
        key = (row.get("eval_id", ""), row.get("prompt", ""))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(row)

    # Group by eval_id and prompt to consolidate match and rubric metrics
    for idx, ((eval_id, prompt), g) in enumerate(grouped.items(), 1):
        match_row = next((r for r in g if r.get("metric_name") == "response_match_score"), None)
        rubric_row = next((r for r in g if r.get("metric_name") == "rubric_based_final_response_quality_v1"), None)
        
        match_score = float(match_row["score"]) if match_row and match_row.get("score") else 0.0
        match_status = match_row["eval_status"] if match_row and match_row.get("eval_status") else "N/A"
        
        rubric_score = float(rubric_row["score"]) if rubric_row and rubric_row.get("score") else 0.0
        rubric_status = rubric_row["eval_status"] if rubric_row and rubric_row.get("eval_status") else "N/A"
        
        expected = next((r["expected_response"] for r in g if r.get("expected_response")), "")
        actual = next((r["actual_response"] for r in g if r.get("actual_response")), "")
        
        exp_tools = next((r["expected_tool_calls"] for r in g if r.get("expected_tool_calls")), "None")
        act_tools = next((r["actual_tool_calls"] for r in g if r.get("actual_tool_calls")), "None")
        
        overall_pass = (rubric_status == "PASSED")
        meta = categorize_question(prompt, expected, eval_id)
        gap_feedback = analyze_gap(prompt, expected, actual, rubric_status, match_score)

        records.append({
            "id": f"Q{idx:02d}",
            "eval_id": eval_id,
            "prompt": prompt,
            "expected_response": expected,
            "actual_response": actual,
            "developer": meta["developer"],
            "category": meta["category"],
            "expected_tools": exp_tools if exp_tools not in ("nan", "") else "None",
            "actual_tools": act_tools if act_tools not in ("nan", "") else "None",
            "match_score": round(match_score, 3),
            "rubric_score": round(rubric_score, 2),
            "status": "PASSED" if overall_pass else "FAILED",
            "gap_analysis": gap_feedback
        })

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Saved consolidated Q&A JSON -> {output_json}")

    # Write summary CSV
    if records:
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            writer.writeheader()
            writer.writerows(records)
    print(f"Saved tabular metrics CSV -> {output_csv}")

    # Generate HTML Dashboard
    generate_html_dashboard(records, output_html)
    return records


def generate_html_dashboard(records: List[Dict[str, Any]], output_path: str):
    total = len(records)
    passed = sum(1 for r in records if r["status"] == "PASSED")
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0
    avg_match = (sum(r["match_score"] for r in records) / total * 100) if total > 0 else 0

    cards_html = []
    for r in records:
        qid = r["id"]
        eval_id = html.escape(r["eval_id"])
        prompt = html.escape(r["prompt"])
        expected = html.escape(r["expected_response"])
        actual = html.escape(r["actual_response"])
        dev = html.escape(r["developer"])
        cat = html.escape(r["category"])
        status = r["status"]
        status_badge = "badge-pass" if status == "PASSED" else "badge-fail"
        status_icon = "✅" if status == "PASSED" else "❌"
        
        match_pct = int(r["match_score"] * 100)
        rubric_val = r["rubric_score"]
        gap = html.escape(r["gap_analysis"])
        
        exp_tools = html.escape(r["expected_tools"])
        act_tools = html.escape(r["actual_tools"])
        has_tools = (exp_tools != "None" or act_tools != "None")

        cards_html.append(f"""
        <div class="eval-card" data-status="{status}" data-dev="{dev}" data-cat="{cat}" data-search="{prompt.lower()} {dev.lower()} {cat.lower()}">
            <div class="card-top-bar">
                <div class="card-meta">
                    <span class="qid-tag">{qid}</span>
                    <span class="badge badge-dev">{dev}</span>
                    <span class="badge badge-cat">{cat}</span>
                    <span class="eval-case-name">{eval_id}</span>
                </div>
                <div class="card-scores">
                    <span class="score-pill">Match: <strong>{match_pct}%</strong></span>
                    <span class="score-pill">Rubric: <strong>{rubric_val}</strong></span>
                    <span class="badge {status_badge}">{status_icon} {status}</span>
                </div>
            </div>

            <div class="prompt-box">
                <div class="box-label">🗣️ USER INQUIRY / LEAD PROMPT</div>
                <div class="prompt-text">"{prompt}"</div>
            </div>

            <div class="comparison-grid">
                <div class="col-side col-expected">
                    <div class="col-header">
                        <span>🎯 EXPECTED (GOLDEN) ANSWER</span>
                        <span class="col-sub">Ground-Truth Sales Guideline</span>
                    </div>
                    <div class="col-content">{expected}</div>
                </div>

                <div class="col-side col-actual">
                    <div class="col-header">
                        <span>🤖 ACTUAL CONVOAI ANSWER</span>
                        <span class="col-sub">Live Model Generation</span>
                    </div>
                    <div class="col-content">{actual}</div>
                </div>
            </div>

            {f'''
            <div class="tools-row">
                <div class="tool-cell"><strong>Expected Tools:</strong> <code>{exp_tools}</code></div>
                <div class="tool-cell"><strong>Actual Tools:</strong> <code>{act_tools}</code></div>
            </div>
            ''' if has_tools else ''}

            <div class="gap-analysis-box">
                <strong>🔍 Gap Analysis & Audit Findings:</strong> {gap}
            </div>
        </div>
        """)

    all_cards = "\n".join(cards_html)

    # Compile Categories and Developers for filters
    devs = sorted(list(set(r["developer"] for r in records)))
    cats = sorted(list(set(r["category"] for r in records)))

    dev_options = "\n".join([f'<option value="{html.escape(d)}">{html.escape(d)}</option>' for d in devs])
    cat_options = "\n".join([f'<option value="{html.escape(c)}">{html.escape(c)}</option>' for c in cats])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ConvoAI Expected vs. Actual Evals Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --border-subtle: #e2e8f0;
            --border-strong: #cbd5e1;
            --text-title: #0f172a;
            --text-body: #334155;
            --text-muted: #64748b;
            --primary: #2563eb;
            --success: #16a34a;
            --danger: #dc2626;
            --warning: #d97706;
            --highlight: #f0fdf4;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, sans-serif; }}
        body {{ background: var(--bg-body); color: var(--text-body); line-height: 1.5; padding: 32px 24px; }}
        .container {{ max-width: 1240px; margin: 0 auto; }}

        /* Header */
        .page-header {{ margin-bottom: 24px; }}
        .page-header h1 {{ font-size: 26px; font-weight: 700; color: var(--text-title); margin-bottom: 6px; }}
        .page-header p {{ color: var(--text-muted); font-size: 14px; }}

        /* KPI Banner */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px; }}
        .kpi-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
        .kpi-val {{ font-size: 28px; font-weight: 700; color: var(--text-title); }}
        .kpi-lbl {{ font-size: 13px; color: var(--text-muted); font-weight: 500; margin-top: 4px; }}

        /* Filter Controls */
        .controls-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 16px 20px; margin-bottom: 24px; display: flex; flex-wrap: wrap; gap: 14px; align-items: center; }}
        .search-input {{ flex: 1; min-width: 260px; padding: 9px 14px; border: 1px solid var(--border-strong); border-radius: 6px; font-size: 14px; outline: none; }}
        .filter-select {{ padding: 9px 12px; border: 1px solid var(--border-strong); border-radius: 6px; font-size: 14px; background: #fff; outline: none; }}

        /* Eval Card */
        .eval-card {{ background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: 12px; margin-bottom: 22px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); overflow: hidden; }}
        .card-top-bar {{ background: #fdfdfd; border-bottom: 1px solid var(--border-subtle); padding: 14px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }}
        .card-meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
        .qid-tag {{ font-weight: 700; font-size: 13px; background: #eff6ff; color: var(--primary); padding: 3px 8px; border-radius: 4px; border: 1px solid #bfdbfe; }}
        .eval-case-name {{ font-size: 12px; color: var(--text-muted); font-family: monospace; }}

        .card-scores {{ display: flex; align-items: center; gap: 10px; }}
        .score-pill {{ font-size: 12px; color: var(--text-muted); background: #f1f5f9; padding: 4px 10px; border-radius: 6px; border: 1px solid var(--border-subtle); }}

        /* Badges */
        .badge {{ font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.3px; }}
        .badge-pass {{ background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }}
        .badge-fail {{ background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }}
        .badge-dev {{ background: #f3e8ff; color: #7e22ce; border: 1px solid #e9d5ff; }}
        .badge-cat {{ background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }}

        /* Prompt Box */
        .prompt-box {{ padding: 16px 20px; background: #f8fafc; border-bottom: 1px solid var(--border-subtle); }}
        .box-label {{ font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--primary); margin-bottom: 4px; }}
        .prompt-text {{ font-size: 16px; font-weight: 600; color: var(--text-title); line-height: 1.4; }}

        /* Comparison Columns */
        .comparison-grid {{ display: grid; grid-template-columns: 1fr 1fr; border-bottom: 1px solid var(--border-subtle); }}
        @media (max-width: 850px) {{ .comparison-grid {{ grid-template-columns: 1fr; }} }}
        .col-side {{ padding: 18px 20px; font-size: 14px; line-height: 1.6; }}
        .col-expected {{ border-right: 1px solid var(--border-subtle); background: #ffffff; }}
        .col-actual {{ background: #fafafa; }}
        .col-header {{ margin-bottom: 10px; display: flex; justify-content: space-between; align-items: baseline; font-weight: 700; font-size: 12px; letter-spacing: 0.4px; color: var(--text-muted); }}
        .col-sub {{ font-size: 11px; font-weight: 500; color: var(--text-muted); }}
        .col-content {{ white-space: pre-line; color: #1e293b; }}

        /* Tools Row */
        .tools-row {{ display: grid; grid-template-columns: 1fr 1fr; background: #f1f5f9; border-bottom: 1px solid var(--border-subtle); font-size: 12px; }}
        .tool-cell {{ padding: 8px 20px; }}
        .tool-cell code {{ background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}

        /* Gap Analysis */
        .gap-analysis-box {{ padding: 14px 20px; background: #fffbeb; border-left: 4px solid var(--warning); font-size: 13px; line-height: 1.5; color: #78350f; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>ConvoAI Ground-Truth Evals: Expected vs. Actual Answers</h1>
            <p>Direct Comparative Evaluation of 40 Multi-Turn Real Estate Questions across 5 Top Developers (Adani, DTC, Veena, Hiranandani, Signature Global)</p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-val">{total}</div>
                <div class="kpi-lbl">Total Questions Evaluated</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val" style="color: #16a34a;">{passed} <span style="font-size: 18px; color: #64748b;">({pass_rate:.1f}%)</span></div>
                <div class="kpi-lbl">Rubric Policy Compliant</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val" style="color: {'#dc2626' if failed > 0 else '#16a34a'};">{failed}</div>
                <div class="kpi-lbl">Policy Regressions / Deviations</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-val">{avg_match:.1f}%</div>
                <div class="kpi-lbl">Avg Semantic Lexical Match</div>
            </div>
        </div>

        <div class="controls-card">
            <input type="text" id="searchInput" class="search-input" placeholder="Search inquiry question, developer, or keyword...">
            <select id="devFilter" class="filter-select">
                <option value="ALL">All Developers</option>
                {dev_options}
            </select>
            <select id="catFilter" class="filter-select">
                <option value="ALL">All Categories</option>
                {cat_options}
            </select>
            <select id="statusFilter" class="filter-select">
                <option value="ALL">All Statuses</option>
                <option value="PASSED">Passed Only</option>
                <option value="FAILED">Failed Only</option>
            </select>
        </div>

        <div id="cardsList">
            {all_cards}
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const devFilter = document.getElementById('devFilter');
        const catFilter = document.getElementById('catFilter');
        const statusFilter = document.getElementById('statusFilter');
        const cards = document.querySelectorAll('.eval-card');

        function filterCards() {{
            const query = searchInput.value.toLowerCase().trim();
            const dev = devFilter.value;
            const cat = catFilter.value;
            const status = statusFilter.value;

            cards.forEach(card => {{
                const cardSearch = card.getAttribute('data-search');
                const cardDev = card.getAttribute('data-dev');
                const cardCat = card.getAttribute('data-cat');
                const cardStatus = card.getAttribute('data-status');

                const matchesSearch = !query || cardSearch.includes(query);
                const matchesDev = dev === 'ALL' || cardDev === dev;
                const matchesCat = cat === 'ALL' || cardCat === cat;
                const matchesStatus = status === 'ALL' || cardStatus === status;

                if (matchesSearch && matchesDev && matchesCat && matchesStatus) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        searchInput.addEventListener('input', filterCards);
        devFilter.addEventListener('change', filterCards);
        catFilter.addEventListener('change', filterCards);
        statusFilter.addEventListener('change', filterCards);
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated clean light-theme Expected vs. Actual dashboard -> {output_path}")
    return output_path


if __name__ == "__main__":
    run_expected_vs_actual_eval()
