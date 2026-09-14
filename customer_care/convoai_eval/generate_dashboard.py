"""
Interactive HTML Dashboard Generator for Convo AI Voice Caller Evaluations.
Clean, professional, light-theme enterprise QA dashboard.
"""

import os
import json
from typing import List, Dict, Any

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Convo AI - Call Quality & Evaluation Report</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-page: #f8fafc;
      --card-bg: #ffffff;
      --border: #e2e8f0;
      --border-focus: #cbd5e1;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --text-subtle: #94a3b8;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --success-bg: #ecfdf5;
      --success-text: #065f46;
      --success-border: #a7f3d0;
      --warning-bg: #fffbeb;
      --warning-text: #92400e;
      --warning-border: #fde68a;
      --danger-bg: #fef2f2;
      --danger-text: #991b1b;
      --danger-border: #fecaca;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-page);
      color: var(--text-main);
      min-height: 100vh;
      line-height: 1.5;
      padding-bottom: 60px;
    }

    /* Top Navigation Bar */
    header {
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .brand-icon {
      width: 34px;
      height: 34px;
      border-radius: 6px;
      background: #2563eb;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 16px;
    }

    .brand-title h1 {
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-main);
    }

    .brand-title p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }

    .btn {
      padding: 7px 14px;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      text-decoration: none;
      transition: background-color 0.15s, border-color 0.15s;
    }

    .btn-primary {
      background: var(--primary);
      color: #ffffff;
      border: 1px solid var(--primary);
    }
    .btn-primary:hover {
      background: var(--primary-hover);
    }

    .btn-secondary {
      background: #ffffff;
      border: 1px solid var(--border);
      color: var(--text-main);
    }
    .btn-secondary:hover {
      background: #f1f5f9;
      border-color: var(--border-focus);
    }

    .container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }

    /* KPI Summary Stats */
    .kpi-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .kpi-box {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }

    .kpi-label {
      font-size: 0.78rem;
      font-weight: 500;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.025em;
      margin-bottom: 6px;
    }

    .kpi-value {
      font-size: 1.85rem;
      font-weight: 700;
      color: var(--text-main);
      line-height: 1.2;
    }

    .kpi-sub {
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* Charts Row */
    .charts-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 28px;
    }

    @media (max-width: 900px) {
      .charts-grid {
        grid-template-columns: 1fr;
      }
    }

    .chart-panel {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }

    .chart-title {
      font-size: 0.92rem;
      font-weight: 600;
      color: var(--text-main);
      margin-bottom: 16px;
    }

    .chart-box {
      position: relative;
      height: 250px;
    }

    /* Controls Bar: Search & Status Filter */
    .controls-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }

    .search-box {
      position: relative;
      width: 320px;
      max-width: 100%;
    }

    .search-input {
      width: 100%;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 0.85rem;
      color: var(--text-main);
      outline: none;
    }
    .search-input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    .status-filters {
      display: flex;
      gap: 6px;
    }

    .filter-tab {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-muted);
      cursor: pointer;
      transition: all 0.15s;
    }
    .filter-tab:hover {
      background: #f1f5f9;
      color: var(--text-main);
    }
    .filter-tab.active {
      background: #e0e7ff;
      border-color: #c7d2fe;
      color: #3730a3;
      font-weight: 600;
    }

    /* Call Cards Grid */
    .calls-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .call-row {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      transition: border-color 0.15s, box-shadow 0.15s;
      cursor: pointer;
    }
    .call-row:hover {
      border-color: #cbd5e1;
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.04);
    }

    .call-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      flex-wrap: wrap;
    }

    .call-info-main {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .call-title-bar {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .call-id-badge {
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--text-muted);
      background: #f1f5f9;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .call-project-name {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-main);
    }

    .status-tag {
      font-size: 0.72rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }
    .status-passed {
      background: var(--success-bg);
      color: var(--success-text);
      border: 1px solid var(--success-border);
    }
    .status-review {
      background: var(--warning-bg);
      color: var(--warning-text);
      border: 1px solid var(--warning-border);
    }
    .status-critical {
      background: var(--danger-bg);
      color: var(--danger-text);
      border: 1px solid var(--danger-border);
    }

    .call-meta-line {
      font-size: 0.82rem;
      color: var(--text-muted);
    }
    .call-meta-line strong {
      color: var(--text-main);
    }

    .call-score-block {
      text-align: right;
    }
    .score-number {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--primary);
    }
    .score-label {
      font-size: 0.72rem;
      color: var(--text-muted);
      text-transform: uppercase;
    }

    /* Mini Audio Player */
    .audio-strip {
      display: flex;
      align-items: center;
      gap: 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 6px 12px;
    }
    .audio-strip audio {
      flex: 1;
      height: 30px;
    }

    /* Submetrics pills */
    .metrics-summary-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      font-size: 0.8rem;
      color: var(--text-muted);
      border-top: 1px solid #f1f5f9;
      padding-top: 10px;
    }
    .metrics-summary-bar span strong {
      color: var(--text-main);
    }

    .call-summary-text {
      font-size: 0.84rem;
      color: #334155;
      line-height: 1.45;
    }

    /* Modal / Details Drawer */
    .modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.4);
      z-index: 100;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-backdrop.active {
      display: flex;
    }

    .modal-window {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 12px;
      width: 100%;
      max-width: 960px;
      max-height: 90vh;
      overflow-y: auto;
      padding: 28px;
      position: relative;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }

    .modal-close-btn {
      position: absolute;
      top: 20px;
      right: 20px;
      background: #f1f5f9;
      border: 1px solid var(--border);
      color: var(--text-muted);
      width: 32px;
      height: 32px;
      border-radius: 6px;
      font-size: 1.1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .modal-close-btn:hover {
      background: #e2e8f0;
      color: var(--text-main);
    }

    .details-section {
      margin-top: 20px;
    }

    .details-section h4 {
      font-size: 0.82rem;
      font-weight: 600;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 8px;
    }

    .entity-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px;
      margin-bottom: 20px;
    }
    .entity-item {
      font-size: 0.82rem;
    }
    .entity-item .label {
      color: var(--text-muted);
      margin-bottom: 2px;
    }
    .entity-item .value {
      font-weight: 600;
      color: var(--text-main);
    }

    .findings-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 24px;
    }
    @media (max-width: 768px) {
      .findings-grid {
        grid-template-columns: 1fr;
      }
    }

    .finding-card {
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px;
      background: #ffffff;
    }
    .finding-card h5 {
      font-size: 0.82rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .finding-card.good {
      border-left: 3px solid #10b981;
    }
    .finding-card.warn {
      border-left: 3px solid #f59e0b;
    }
    .finding-card.action {
      border-left: 3px solid #2563eb;
    }

    .clean-list {
      list-style: none;
      font-size: 0.82rem;
      color: #334155;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .clean-list li {
      position: relative;
      padding-left: 14px;
      line-height: 1.4;
    }
    .clean-list li::before {
      content: "•";
      position: absolute;
      left: 0;
      color: var(--text-muted);
      font-weight: bold;
    }

    /* Normal Clean Chat Transcript */
    .dialogue-wrapper {
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      max-height: 380px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 10px;
    }

    .chat-row {
      display: flex;
      flex-direction: column;
      max-width: 80%;
      gap: 2px;
    }
    .chat-agent {
      align-self: flex-start;
    }
    .chat-user {
      align-self: flex-end;
    }

    .chat-speaker {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
    }
    .chat-agent .chat-speaker {
      color: #1d4ed8;
    }
    .chat-user .chat-speaker {
      color: #475569;
      text-align: right;
    }

    .chat-text {
      padding: 9px 13px;
      border-radius: 8px;
      font-size: 0.85rem;
      line-height: 1.45;
    }

    .chat-agent .chat-text {
      background: #ffffff;
      border: 1px solid var(--border);
      color: #0f172a;
    }

    .chat-user .chat-text {
      background: #e2e8f0;
      color: #0f172a;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">C</div>
      <div class="brand-title">
        <h1>Convo AI Quality Assurance</h1>
        <p>Voice Agent Call Evaluation & Regression Report</p>
      </div>
    </div>
    <div class="header-actions">
      <button class="btn btn-secondary" onclick="exportJSON()">Export JSON</button>
      <button class="btn btn-primary" onclick="exportCSV()">Export CSV</button>
    </div>
  </header>

  <div class="container">

    <!-- KPI Summary Row -->
    <div class="kpi-row">
      <div class="kpi-box">
        <div class="kpi-label">Average Confidence Score</div>
        <div class="kpi-value">__AVG_CONFIDENCE__%</div>
        <div class="kpi-sub">Overall intent & task accuracy</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-label">Compliance / Pass Rate</div>
        <div class="kpi-value" style="color: #059669;">__PASS_RATE__%</div>
        <div class="kpi-sub">__PASSED_CALLS__ of __TOTAL_CALLS__ calls passed</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-label">Lead Qualification</div>
        <div class="kpi-value">__AVG_QUAL__%</div>
        <div class="kpi-sub">BHK & self-use discovery</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-label">Site Visit Scheduling</div>
        <div class="kpi-value">__AVG_SCHED__%</div>
        <div class="kpi-sub">Appointment booking rate</div>
      </div>

      <div class="kpi-box">
        <div class="kpi-label">Total Calls Evaluated</div>
        <div class="kpi-value">__TOTAL_CALLS__</div>
        <div class="kpi-sub">__TOTAL_TURNS__ dialogue turns</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <div class="chart-panel">
        <div class="chart-title">Evaluation Dimensions (Fleet Average)</div>
        <div class="chart-box">
          <canvas id="radarChart"></canvas>
        </div>
      </div>
      <div class="chart-panel">
        <div class="chart-title">Project & Developer Confidence</div>
        <div class="chart-box">
          <canvas id="barChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Controls: Search & Filter -->
    <div class="controls-bar">
      <div class="search-box">
        <input type="text" id="searchInput" class="search-input" placeholder="Search developer, persona, or project..." onkeyup="filterCalls()">
      </div>
      <div class="status-filters">
        <button class="filter-tab active" onclick="setFilter('ALL', this)">All Calls (__TOTAL_CALLS__)</button>
        <button class="filter-tab" onclick="setFilter('PASSED', this)">Passed</button>
        <button class="filter-tab" onclick="setFilter('NEEDS_REVIEW', this)">Needs Review</button>
      </div>
    </div>

    <!-- Call Rows Container -->
    <div class="calls-container" id="callsGrid"></div>

  </div>

  <!-- Modal / Call Details Drawer -->
  <div class="modal-backdrop" id="modalOverlay" onclick="handleModalClick(event)">
    <div class="modal-window">
      <button class="modal-close-btn" onclick="closeModal()">&times;</button>
      <div id="modalBody"></div>
    </div>
  </div>

  <script>
    const callsData = __CALLS_DATA_JSON__;
    let currentFilter = 'ALL';

    function renderCalls() {
      const container = document.getElementById('callsGrid');
      const searchQuery = (document.getElementById('searchInput').value || '').toLowerCase();
      container.innerHTML = '';

      callsData.forEach((call, index) => {
        const status = call.status || 'PASSED';
        if (currentFilter !== 'ALL' && status !== currentFilter) return;

        const project = (call.developer_project || 'Real Estate').toLowerCase();
        const persona = (call.caller_persona || '').toLowerCase();
        const summary = (call.executive_summary || '').toLowerCase();
        if (searchQuery && !project.includes(searchQuery) && !persona.includes(searchQuery) && !summary.includes(searchQuery)) {
          return;
        }

        const conf = call.overall_confidence_score || 0;
        let statusTag = '<span class="status-tag status-passed">Passed</span>';
        if (status === 'NEEDS_REVIEW') {
          statusTag = '<span class="status-tag status-review">Needs Review</span>';
        } else if (status === 'CRITICAL_ISSUE') {
          statusTag = '<span class="status-tag status-critical">Critical</span>';
        }

        const card = document.createElement('div');
        card.className = 'call-row';
        card.onclick = () => openModal(index);

        card.innerHTML = `
          <div class="call-top">
            <div class="call-info-main">
              <div class="call-title-bar">
                <span class="call-id-badge">Call #${call.tab_id}</span>
                <span class="call-project-name">${call.developer_project || 'Real Estate Project'}</span>
                ${statusTag}
              </div>
              <div class="call-meta-line">
                Caller Persona: <strong>${call.caller_persona || 'AI Agent'}</strong> &bull; Total Turns: <strong>${call.turn_count || call.turns?.length || 0}</strong>
              </div>
            </div>

            <div class="call-score-block">
              <div class="score-number">${conf}%</div>
              <div class="score-label">Confidence Score</div>
            </div>
          </div>

          <div class="audio-strip" onclick="event.stopPropagation()">
            <audio controls preload="none">
              <source src="${call.audio_url}" type="audio/wav">
            </audio>
          </div>

          <div class="call-summary-text">
            ${call.executive_summary || 'Evaluation summary completed.'}
          </div>

          <div class="metrics-summary-bar">
            <span>Qualification: <strong>${call.scores?.lead_qualification || 0}%</strong></span>
            <span>Scheduling: <strong>${call.scores?.site_visit_scheduling || 0}%</strong></span>
            <span>Policy Boundaries: <strong>${call.scores?.objection_and_boundary || 0}%</strong></span>
            <span>Compliance & Tone: <strong>${call.scores?.compliance_and_tone || 0}%</strong></span>
            <span>Fluency: <strong>${call.scores?.conversational_fluency || 0}%</strong></span>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function openModal(index) {
      const call = callsData[index];
      const modalBody = document.getElementById('modalBody');
      const conf = call.overall_confidence_score || 0;

      let statusTag = '<span class="status-tag status-passed">Passed</span>';
      if (call.status === 'NEEDS_REVIEW') {
        statusTag = '<span class="status-tag status-review">Needs Review</span>';
      }

      let dialogueHtml = '';
      (call.turns || []).forEach(turn => {
        const isAgent = turn.speaker === 0 || turn.speaker_label === 'agent';
        const rowClass = isAgent ? 'chat-agent' : 'chat-user';
        const speaker = isAgent ? (call.caller_persona || 'AI Agent') : 'Customer';
        dialogueHtml += `
          <div class="chat-row ${rowClass}">
            <span class="chat-speaker">${speaker}</span>
            <div class="chat-text">${turn.message}</div>
          </div>
        `;
      });

      const strengthsHtml = (call.key_strengths || []).map(s => `<li>${s}</li>`).join('');
      const weaknessesHtml = (call.weaknesses_or_flags || []).map(w => `<li>${w}</li>`).join('');
      const recsHtml = (call.actionable_recommendations || []).map(r => `<li>${r}</li>`).join('');

      modalBody.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
          <div>
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
              <span class="call-id-badge">Call #${call.tab_id}</span>
              <h2 style="font-size: 1.25rem; font-weight: 700; color: #0f172a;">${call.developer_project}</h2>
              ${statusTag}
            </div>
            <p style="font-size: 0.85rem; color: #64748b;">
              Persona: <strong>${call.caller_persona}</strong> &bull; Length: <strong>${call.turns?.length || 0} turns</strong>
            </p>
          </div>
          <div style="text-align: right;">
            <div style="font-size: 1.75rem; font-weight: 700; color: #2563eb;">${conf}%</div>
            <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Confidence Score</div>
          </div>
        </div>

        <div class="audio-strip" style="margin-bottom: 20px;">
          <audio controls autoplay style="width: 100%;">
            <source src="${call.audio_url}" type="audio/wav">
          </audio>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; margin-bottom: 20px;">
          <div style="font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 4px;">Executive Evaluation Rationale</div>
          <p style="font-size: 0.88rem; color: #1e293b; line-height: 1.5;">${call.executive_summary}</p>
        </div>

        <div class="entity-grid">
          <div class="entity-item">
            <div class="label">Customer Intent</div>
            <div class="value">${call.extracted_entities?.intent || 'Property Inquiry'}</div>
          </div>
          <div class="entity-item">
            <div class="label">Configuration</div>
            <div class="value">${call.extracted_entities?.configuration || 'Not specified'}</div>
          </div>
          <div class="entity-item">
            <div class="label">Site Visit Time</div>
            <div class="value">${call.extracted_entities?.visit_datetime || 'None scheduled'}</div>
          </div>
          <div class="entity-item">
            <div class="label">Pricing Disclosed</div>
            <div class="value">${call.extracted_entities?.disclosed_pricing || 'N/A'}</div>
          </div>
          <div class="entity-item">
            <div class="label">Follow-up Channel</div>
            <div class="value">${call.extracted_entities?.channel_followup || 'WhatsApp'}</div>
          </div>
        </div>

        <div class="findings-grid">
          <div class="finding-card good">
            <h5>Observed Strengths</h5>
            <ul class="clean-list">${strengthsHtml || '<li>Consistent call progression.</li>'}</ul>
          </div>
          <div class="finding-card warn">
            <h5>Flags / Areas for Improvement</h5>
            <ul class="clean-list">${weaknessesHtml || '<li>No critical flags detected.</li>'}</ul>
          </div>
        </div>

        <div class="finding-card action" style="margin-bottom: 24px;">
          <h5>Recommended Improvements</h5>
          <ul class="clean-list">${recsHtml}</ul>
        </div>

        <h3 style="font-size: 0.95rem; font-weight: 600; color: #0f172a; margin-bottom: 6px;">Call Transcript (${call.turns?.length || 0} turns)</h3>
        <div class="dialogue-wrapper">
          ${dialogueHtml}
        </div>
      `;

      document.getElementById('modalOverlay').classList.add('active');
    }

    function closeModal() {
      const overlay = document.getElementById('modalOverlay');
      overlay.classList.remove('active');
      const audio = overlay.querySelector('audio');
      if (audio) audio.pause();
    }

    function handleModalClick(e) {
      if (e.target.id === 'modalOverlay') {
        closeModal();
      }
    }

    function setFilter(status, btn) {
      currentFilter = status;
      document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderCalls();
    }

    function filterCalls() {
      renderCalls();
    }

    function exportJSON() {
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(callsData, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", "convoai_eval_results.json");
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    }

    function exportCSV() {
      window.location.href = "results/convoai_eval_results.csv";
    }

    // Initialize Charts with clean light theme styling
    window.onload = () => {
      renderCalls();

      // Radar Chart
      const radarCtx = document.getElementById('radarChart').getContext('2d');
      new Chart(radarCtx, {
        type: 'radar',
        data: {
          labels: [
            'Lead Qualification',
            'Site Visit Scheduling',
            'Policy Boundaries',
            'Compliance & Tone',
            'Fluency & Pacing'
          ],
          datasets: [{
            label: 'Average Score',
            data: [__AVG_QUAL__, __AVG_SCHED__, __AVG_OBJ__, __AVG_COMP__, __AVG_FLUE__],
            backgroundColor: 'rgba(37, 99, 235, 0.12)',
            borderColor: '#2563eb',
            borderWidth: 2,
            pointBackgroundColor: '#2563eb',
            pointBorderColor: '#ffffff',
            pointRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              angleLines: { color: '#e2e8f0' },
              grid: { color: '#f1f5f9' },
              pointLabels: { color: '#475569', font: { size: 11, family: 'Inter' } },
              ticks: { color: '#94a3b8', backdropColor: 'transparent', stepSize: 20 },
              min: 0,
              max: 100
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });

      // Developer Bar Chart
      const projectMap = {};
      callsData.forEach(c => {
        const proj = c.developer_project || 'Other';
        if (!projectMap[proj]) projectMap[proj] = [];
        projectMap[proj].push(c.overall_confidence_score || 0);
      });

      const projLabels = Object.keys(projectMap);
      const projAverages = projLabels.map(k => Math.round(projectMap[k].reduce((a, b) => a + b, 0) / projectMap[k].length));

      const barCtx = document.getElementById('barChart').getContext('2d');
      new Chart(barCtx, {
        type: 'bar',
        data: {
          labels: projLabels,
          datasets: [{
            label: 'Avg Confidence (%)',
            data: projAverages,
            backgroundColor: '#3b82f6',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { grid: { display: false }, ticks: { color: '#64748b', font: { size: 11 } } },
            y: { grid: { color: '#f1f5f9' }, ticks: { color: '#64748b' }, min: 0, max: 100 }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    };
  </script>
</body>
</html>
"""


def generate_html_dashboard(
    results_json_path: str = "convoai_eval/results/convoai_eval_results.json",
    output_html_path: str = "convoai_eval/convoai_eval_dashboard.html"
):
    if not os.path.exists(results_json_path):
        raise FileNotFoundError(f"Cannot find results file at {results_json_path}")

    with open(results_json_path, "r", encoding="utf-8") as f:
        results: List[Dict[str, Any]] = json.load(f)

    total_calls = len(results)
    if total_calls == 0:
        print("No calls found in results.")
        return

    avg_confidence = round(sum(r.get("overall_confidence_score", 0) for r in results) / total_calls, 1)
    avg_qual = round(sum(r.get("scores", {}).get("lead_qualification", 0) for r in results) / total_calls, 1)
    avg_sched = round(sum(r.get("scores", {}).get("site_visit_scheduling", 0) for r in results) / total_calls, 1)
    avg_obj = round(sum(r.get("scores", {}).get("objection_and_boundary", 0) for r in results) / total_calls, 1)
    avg_comp = round(sum(r.get("scores", {}).get("compliance_and_tone", 0) for r in results) / total_calls, 1)
    avg_flue = round(sum(r.get("scores", {}).get("conversational_fluency", 0) for r in results) / total_calls, 1)

    passed_calls = sum(1 for r in results if r.get("status") in ["EXCELLENT", "PASSED"])
    pass_rate = round((passed_calls / total_calls) * 100, 1)
    total_turns = sum(len(r.get("turns", [])) for r in results)

    content = HTML_TEMPLATE
    content = content.replace("__AVG_CONFIDENCE__", str(avg_confidence))
    content = content.replace("__PASS_RATE__", str(pass_rate))
    content = content.replace("__PASSED_CALLS__", str(passed_calls))
    content = content.replace("__TOTAL_CALLS__", str(total_calls))
    content = content.replace("__AVG_QUAL__", str(avg_qual))
    content = content.replace("__AVG_SCHED__", str(avg_sched))
    content = content.replace("__AVG_OBJ__", str(avg_obj))
    content = content.replace("__AVG_COMP__", str(avg_comp))
    content = content.replace("__AVG_FLUE__", str(avg_flue))
    content = content.replace("__TOTAL_TURNS__", str(total_turns))
    content = content.replace("__CALLS_DATA_JSON__", json.dumps(results))

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated clean light-theme dashboard -> {output_html_path}")
    return output_html_path


if __name__ == "__main__":
    generate_html_dashboard()
