"""
Generates an interactive, modern light-theme HTML Dashboard for Method 1 Call Center Evaluations.
"""

import os
import json
import html
from typing import List, Dict, Any


def generate_html_dashboard(
    json_path: str = "callcenter_archive_eval/method1_direct_eval/results/callcenter_eval_results.json",
    output_html_path: str = "callcenter_archive_eval/method1_direct_eval/callcenter_eval_dashboard.html"
):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON results not found at {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        calls: List[Dict[str, Any]] = json.load(f)

    total_calls = len(calls)
    if total_calls == 0:
        return

    avg_conf = sum(c.get("overall_confidence_score", 0) for c in calls) / total_calls
    passed_count = sum(1 for c in calls if c.get("status") in ["EXCELLENT", "PASSED"])
    pass_rate = (passed_count / total_calls) * 100
    risk_count = sum(1 for c in calls if (c.get("extracted_entities", {}).get("risk_level") in ["HIGH", "CRITICAL"]))
    
    # Calculate sub-score averages
    avg_res = sum(c.get("scores", {}).get("resolution_and_effectiveness", 0) for c in calls) / total_calls
    avg_sec = sum(c.get("scores", {}).get("security_compliance_and_policy", 0) for c in calls) / total_calls
    avg_emp = sum(c.get("scores", {}).get("customer_empathy_and_tone", 0) for c in calls) / total_calls
    avg_flu = sum(c.get("scores", {}).get("conversational_fluency_and_clarity", 0) for c in calls) / total_calls

    cards_html = []
    for c in calls:
        cid = html.escape(str(c.get("call_id", "")))
        tag = html.escape(str(c.get("call_tag", "Call")))
        domain = html.escape(str(c.get("domain", "Customer Care")))
        lang = html.escape(str(c.get("language", "English")))
        status = c.get("status", "NEEDS_REVIEW")
        score = c.get("overall_confidence_score", 0)
        
        entities = c.get("extracted_entities", {})
        risk = entities.get("risk_level", "LOW")
        outcome = html.escape(str(entities.get("call_outcome", "RESOLVED")))
        issue = html.escape(str(entities.get("customer_core_issue", "N/A")))
        
        scores = c.get("scores", {})
        s_res = scores.get("resolution_and_effectiveness", 0)
        s_sec = scores.get("security_compliance_and_policy", 0)
        s_emp = scores.get("customer_empathy_and_tone", 0)
        s_flu = scores.get("conversational_fluency_and_clarity", 0)
        
        summary = html.escape(c.get("executive_summary", ""))
        audio_file = html.escape(c.get("audio_file", ""))
        audio_path = c.get("audio_path", "")
        audio_uri = "file:///" + audio_path.replace("\\", "/") if audio_path else "#"
        
        strengths = "".join([f"<li>{html.escape(s)}</li>" for s in c.get("key_strengths", [])])
        weaknesses = "".join([f"<li>{html.escape(w)}</li>" for w in c.get("weaknesses_or_risk_flags", [])])
        recommendations = "".join([f"<li>{html.escape(r)}</li>" for r in c.get("actionable_recommendations", [])])
        
        # Format turns
        turn_bubbles = []
        turns = c.get("turns", [])
        for t in turns:
            role = t.get("speaker_role", "SPEAKER")
            ts = html.escape(t.get("timestamp", ""))
            text = html.escape(t.get("text", ""))
            role_class = "agent-turn" if role == "AGENT" else "customer-turn"
            role_label = "Agent" if role == "AGENT" else "Customer"
            turn_bubbles.append(f"""
                <div class="turn-row {role_class}">
                    <div class="turn-meta"><span class="role-tag">{role_label}</span> <span class="time-tag">{ts}</span></div>
                    <div class="turn-bubble">{text}</div>
                </div>
            """)
        turns_html = "".join(turn_bubbles)

        # Status & Risk badge styles
        status_badge_class = "badge-success" if status in ["EXCELLENT", "PASSED"] else ("badge-warning" if status == "NEEDS_REVIEW" else "badge-danger")
        risk_badge_class = "badge-danger" if risk in ["HIGH", "CRITICAL"] else ("badge-warning" if risk == "MEDIUM" else "badge-info")

        score_color = "#16a34a" if score >= 80 else ("#d97706" if score >= 60 else "#dc2626")

        cards_html.append(f"""
        <div class="call-card" data-status="{status}" data-risk="{risk}" data-search="{cid.lower()} {tag.lower()} {domain.lower()} {lang.lower()}">
            <div class="card-header">
                <div class="header-main">
                    <div class="call-title-row">
                        <span class="call-id">#{cid}</span>
                        <h3 class="call-title">{tag}</h3>
                        <span class="badge {status_badge_class}">{status}</span>
                        <span class="badge {risk_badge_class}">Risk: {risk}</span>
                    </div>
                    <div class="call-submeta">
                        <span><strong>Domain:</strong> {domain}</span> •
                        <span><strong>Language:</strong> {lang}</span> •
                        <span><strong>Outcome:</strong> {outcome}</span> •
                        <span><strong>Turns:</strong> {len(turns)}</span>
                    </div>
                </div>
                <div class="score-circle" style="border-color: {score_color}; color: {score_color};">
                    <span class="score-num">{score}</span>
                    <span class="score-lbl">Score</span>
                </div>
            </div>

            <div class="card-body">
                <div class="metrics-grid">
                    <div class="metric-bar-item">
                        <div class="metric-bar-label"><span>Resolution & Goal</span><span>{s_res}%</span></div>
                        <div class="bar-bg"><div class="bar-fill" style="width: {s_res}%;"></div></div>
                    </div>
                    <div class="metric-bar-item">
                        <div class="metric-bar-label"><span>Security & Policy</span><span>{s_sec}%</span></div>
                        <div class="bar-bg"><div class="bar-fill" style="width: {s_sec}%;"></div></div>
                    </div>
                    <div class="metric-bar-item">
                        <div class="metric-bar-label"><span>Empathy & Tone</span><span>{s_emp}%</span></div>
                        <div class="bar-bg"><div class="bar-fill" style="width: {s_emp}%;"></div></div>
                    </div>
                    <div class="metric-bar-item">
                        <div class="metric-bar-label"><span>Fluency & Clarity</span><span>{s_flu}%</span></div>
                        <div class="bar-bg"><div class="bar-fill" style="width: {s_flu}%;"></div></div>
                    </div>
                </div>

                <div class="summary-box">
                    <strong>Core Issue:</strong> {issue}<br/>
                    <strong>Executive Summary:</strong> {summary}
                </div>

                {f'<div class="audio-strip">🎵 <strong>Recording:</strong> <code>{audio_file}</code> <a href="{audio_uri}" class="btn-audio" target="_blank">Open Audio File</a></div>' if audio_file else ''}

                <div class="feedback-cols">
                    <div class="feedback-col col-strengths">
                        <h4>✓ Key Strengths</h4>
                        <ul>{strengths}</ul>
                    </div>
                    <div class="feedback-col col-weaknesses">
                        <h4>⚠️ Risks & Vulnerabilities</h4>
                        <ul>{weaknesses}</ul>
                    </div>
                </div>

                <div class="recommendations-box">
                    <h4>💡 Actionable Recommendations</h4>
                    <ul>{recommendations}</ul>
                </div>

                <details class="transcript-details">
                    <summary>View Complete Call Transcript ({len(turns)} turns)</summary>
                    <div class="transcript-container">
                        {turns_html}
                    </div>
                </details>
            </div>
        </div>
        """)

    all_cards = "\n".join(cards_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Center QA & Conversational AI Audit Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --info: #0284c7;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        body {{ background-color: var(--bg-page); color: var(--text-main); line-height: 1.5; padding: 32px 24px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        
        /* Header */
        .page-header {{ margin-bottom: 28px; }}
        .page-header h1 {{ font-size: 26px; font-weight: 700; color: var(--text-main); margin-bottom: 6px; }}
        .page-header p {{ color: var(--text-muted); font-size: 14px; }}
        
        /* Stats Grid */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 28px; }}
        .stat-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 10px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.03); }}
        .stat-card .stat-val {{ font-size: 28px; font-weight: 700; color: var(--text-main); }}
        .stat-card .stat-label {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; font-weight: 500; }}
        
        /* Controls */
        .controls-row {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 24px; background: var(--bg-card); padding: 14px 18px; border: 1px solid var(--border-color); border-radius: 8px; }}
        .search-input {{ flex: 1; min-width: 250px; padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 14px; outline: none; }}
        .filter-select {{ padding: 8px 12px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 14px; outline: none; background: #fff; }}

        /* Cards */
        .call-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 12px; margin-bottom: 22px; box-shadow: 0 2px 5px rgba(0,0,0,0.02); overflow: hidden; }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border-color); background: #ffffff; }}
        .call-title-row {{ display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }}
        .call-id {{ font-size: 13px; font-weight: 700; color: var(--primary); background: #eff6ff; padding: 3px 8px; border-radius: 4px; }}
        .call-title {{ font-size: 18px; font-weight: 600; color: var(--text-main); }}
        .call-submeta {{ font-size: 13px; color: var(--text-muted); margin-top: 6px; }}
        
        .score-circle {{ width: 62px; height: 62px; border-radius: 50%; border: 3px solid; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; flex-shrink: 0; }}
        .score-num {{ font-size: 18px; font-weight: 700; line-height: 1; }}
        .score-lbl {{ font-size: 10px; text-transform: uppercase; font-weight: 600; margin-top: 2px; }}

        .card-body {{ padding: 22px 24px; }}
        
        /* Badges */
        .badge {{ font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .badge-success {{ background: #dcfce7; color: #15803d; }}
        .badge-warning {{ background: #fef3c7; color: #b45309; }}
        .badge-danger {{ background: #fee2e2; color: #b91c1c; }}
        .badge-info {{ background: #e0f2fe; color: #0369a1; }}

        /* Metrics grid */
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px; }}
        .metric-bar-item {{ background: #f8fafc; border: 1px solid var(--border-color); padding: 12px 14px; border-radius: 8px; }}
        .metric-bar-label {{ display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; margin-bottom: 6px; color: #334155; }}
        .bar-bg {{ height: 7px; background: #e2e8f0; border-radius: 999px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: var(--primary); border-radius: 999px; }}

        .summary-box {{ background: #f8fafc; border-left: 4px solid var(--primary); padding: 14px 16px; border-radius: 0 6px 6px 0; margin-bottom: 18px; font-size: 14px; line-height: 1.6; color: #1e293b; }}
        
        .audio-strip {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 10px 14px; border-radius: 6px; margin-bottom: 18px; font-size: 13px; display: flex; align-items: center; justify-content: space-between; }}
        .btn-audio {{ background: var(--primary); color: #fff; text-decoration: none; padding: 5px 12px; border-radius: 4px; font-weight: 500; font-size: 12px; }}

        /* Feedback columns */
        .feedback-cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 18px; }}
        @media (max-width: 768px) {{ .feedback-cols {{ grid-template-columns: 1fr; }} }}
        .feedback-col {{ border-radius: 8px; padding: 14px 16px; border: 1px solid var(--border-color); font-size: 13px; }}
        .col-strengths {{ background: #f0fdf4; border-color: #bbf7d0; }}
        .col-strengths h4 {{ color: #166534; font-size: 13px; margin-bottom: 8px; font-weight: 600; }}
        .col-weaknesses {{ background: #fffbeb; border-color: #fef08a; }}
        .col-weaknesses h4 {{ color: #92400e; font-size: 13px; margin-bottom: 8px; font-weight: 600; }}
        .feedback-col ul {{ padding-left: 18px; margin: 0; }}
        .feedback-col li {{ margin-bottom: 4px; color: #334155; }}

        .recommendations-box {{ background: #f8fafc; border: 1px solid var(--border-color); border-radius: 8px; padding: 14px 16px; margin-bottom: 18px; font-size: 13px; }}
        .recommendations-box h4 {{ font-size: 13px; margin-bottom: 8px; font-weight: 600; color: #1e293b; }}
        .recommendations-box ul {{ padding-left: 18px; margin: 0; }}
        .recommendations-box li {{ margin-bottom: 4px; color: #334155; }}

        /* Transcript */
        .transcript-details {{ background: #ffffff; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }}
        .transcript-details summary {{ padding: 12px 16px; font-weight: 600; font-size: 13px; cursor: pointer; background: #f8fafc; user-select: none; }}
        .transcript-container {{ padding: 16px; max-height: 480px; overflow-y: auto; background: #fafafa; display: flex; flex-direction: column; gap: 10px; }}
        .turn-row {{ display: flex; flex-direction: column; max-width: 85%; }}
        .turn-meta {{ font-size: 11px; margin-bottom: 3px; color: var(--text-muted); }}
        .role-tag {{ font-weight: 600; }}
        .turn-bubble {{ padding: 10px 14px; border-radius: 8px; font-size: 13px; line-height: 1.5; }}
        
        .agent-turn {{ align-self: flex-start; }}
        .agent-turn .turn-bubble {{ background: #ffffff; border: 1px solid #cbd5e1; color: #0f172a; border-left: 3px solid var(--primary); }}
        .agent-turn .role-tag {{ color: var(--primary); }}

        .customer-turn {{ align-self: flex-end; }}
        .customer-turn .turn-bubble {{ background: #e0f2fe; border: 1px solid #bae6fd; color: #0369a1; text-align: right; }}
        .customer-turn .turn-meta {{ text-align: right; }}
        .customer-turn .role-tag {{ color: #0284c7; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="page-header">
            <h1>Contact Center Conversational AI Audit Dashboard</h1>
            <p>Comprehensive QA, Operational Compliance, and Performance Evaluation across 11 Multilingual Real-World Calls (Archive 1)</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-val">{total_calls}</div>
                <div class="stat-label">Calls Evaluated</div>
            </div>
            <div class="stat-card">
                <div class="stat-val">{avg_conf:.1f}%</div>
                <div class="stat-label">Average Confidence Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-val">{pass_rate:.1f}%</div>
                <div class="stat-label">QA Compliance Pass Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-val" style="color: {'#dc2626' if risk_count > 0 else '#16a34a'};">{risk_count}</div>
                <div class="stat-label">High / Critical Risk Flags</div>
            </div>
        </div>

        <div class="controls-row">
            <input type="text" id="searchInput" class="search-input" placeholder="Search by Call ID, Category, Language, or Domain...">
            <select id="statusFilter" class="filter-select">
                <option value="ALL">All Statuses</option>
                <option value="EXCELLENT">Excellent</option>
                <option value="PASSED">Passed</option>
                <option value="NEEDS_REVIEW">Needs Review</option>
                <option value="CRITICAL_RISK">Critical Risk</option>
            </select>
            <select id="riskFilter" class="filter-select">
                <option value="ALL">All Risk Levels</option>
                <option value="LOW">Low Risk</option>
                <option value="MEDIUM">Medium Risk</option>
                <option value="HIGH">High Risk</option>
                <option value="CRITICAL">Critical Risk</option>
            </select>
        </div>

        <div id="cardsList">
            {all_cards}
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('searchInput');
        const statusFilter = document.getElementById('statusFilter');
        const riskFilter = document.getElementById('riskFilter');
        const cards = document.querySelectorAll('.call-card');

        function filterCards() {{
            const searchVal = searchInput.value.toLowerCase().trim();
            const statusVal = statusFilter.value;
            const riskVal = riskFilter.value;

            cards.forEach(card => {{
                const cardSearch = card.getAttribute('data-search');
                const cardStatus = card.getAttribute('data-status');
                const cardRisk = card.getAttribute('data-risk');

                const matchesSearch = !searchVal || cardSearch.includes(searchVal);
                const matchesStatus = statusVal === 'ALL' || cardStatus === statusVal;
                const matchesRisk = riskVal === 'ALL' || cardRisk === riskVal;

                if (matchesSearch && matchesStatus && matchesRisk) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}

        searchInput.addEventListener('input', filterCards);
        statusFilter.addEventListener('change', filterCards);
        riskFilter.addEventListener('change', filterCards);
    </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated clean light-theme dashboard -> {output_html_path}")
    return output_html_path


if __name__ == "__main__":
    generate_html_dashboard()
