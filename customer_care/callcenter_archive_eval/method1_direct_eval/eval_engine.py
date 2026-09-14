"""
Multilingual Call Center Evaluation Engine.
Evaluates real-world customer support, billing, finance, and sales calls
using Gemini 3.6 Flash as an expert Conversational AI Auditor.
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

EVALUATION_SYSTEM_PROMPT = """
You are a Principal Voice & Conversational AI Auditor and QA Specialist for Global Enterprise Contact Centers.
Your task is to thoroughly analyze real call recordings and transcripts between Call Center Agents (AGENT) and Customers (CUSTOMER) across multiple domains (Customer Support, Billing & Invoicing, Financial Trading/Account Management, and Sales) in multiple languages (English, Russian, Polish, French, German, Spanish, Portuguese).

You must evaluate the conversation with high rigor, taking into account operational procedures, risk management, customer sentiment, compliance, security boundaries (such as remote desktop access like AnyDesk, bank wire instructions, or investment disclosures), and agent communication quality.

Scoring Criteria (Grade each strictly from 0 to 100):
1. overall_confidence_score: Calibrated overall evaluation score of how successfully the interaction was conducted.
2. resolution_and_effectiveness_score: How effectively the agent understood the customer's core intent/issue and delivered a concrete resolution or sales pitch.
3. security_compliance_and_policy_score: Adherence to security protocols (e.g. verifying accounts, disclaimer disclosures, cautious handling of credentials/funds, remote access risks).
4. customer_empathy_and_tone_score: Professionalism, active listening, patience with confused/frustrated customers, de-escalation skills.
5. conversational_fluency_and_clarity_score: Natural flow, clear pacing, absence of confusing jargon, and effective language handling.

You must output your evaluation strictly as valid JSON adhering to this JSON schema:
{
  "call_id": string,
  "call_tag": string,
  "domain": string,
  "language": string,
  "status": "EXCELLENT" | "PASSED" | "NEEDS_REVIEW" | "CRITICAL_RISK",
  "overall_confidence_score": int,
  "scores": {
    "resolution_and_effectiveness": int,
    "security_compliance_and_policy": int,
    "customer_empathy_and_tone": int,
    "conversational_fluency_and_clarity": int
  },
  "extracted_entities": {
    "customer_core_issue": string,
    "financial_or_product_details": string,
    "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
    "call_outcome": "RESOLVED" | "FOLLOW_UP_REQUIRED" | "UNRESOLVED_DISPUTE" | "TECHNICAL_BLOCKER"
  },
  "executive_summary": string,
  "key_strengths": [string],
  "weaknesses_or_risk_flags": [string],
  "actionable_recommendations": [string]
}
"""

class CallCenterEvaluator:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def evaluate_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        call_id = call_data.get("call_id", "")
        call_tag = call_data.get("call_tag", "")
        metadata = call_data.get("metadata", {})
        audio_file = call_data.get("audio_file", "")
        audio_path = call_data.get("audio_path", "")
        turns = call_data.get("turns", [])

        # Format transcript lines
        formatted_dialogue = []
        for t in turns:
            role = t.get("speaker_role", "SPEAKER")
            timestamp = t.get("timestamp", "")
            text = t.get("text", "")
            formatted_dialogue.append(f"[{role} @ {timestamp}]: {text}")

        transcript_str = "\n".join(formatted_dialogue)

        meta_context = []
        for k, v in metadata.items():
            if k not in ["call_id", "call_tag", "audio_file", "audio_path", "docx_file", "folder_name"] and v:
                meta_context.append(f"- {k}: {v}")
        meta_str = "\n".join(meta_context) if meta_context else "No prior metadata summary."

        prompt = f"""
CALL IDENTIFIER: {call_id}
CALL CATEGORY/TAG: {call_tag}
AUDIO RECORDING FILENAME: {audio_file}

PRE-RECORDED SUMMARY CONTEXT:
{meta_str}

FULL CALL TRANSCRIPT ({len(turns)} turns):
{transcript_str}

Please perform an in-depth, rigorous QA and Conversational AI evaluation of this contact center interaction according to the schema provided. Return ONLY the JSON object.
"""

        models_to_try = [self.model_name, "gemini-3.5-flash"]
        response = None
        last_err = None

        for m in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                    config=types.GenerateContentConfig(
                        system_instruction=EVALUATION_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                if response and response.text:
                    break
            except Exception as e:
                last_err = e
                continue

        if not response or not response.text:
            raise RuntimeError(f"Failed to generate evaluation from Gemini: {last_err}")

        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        result = json.loads(text)
        result["call_id"] = call_id
        result["call_tag"] = call_tag
        result["audio_file"] = audio_file
        result["audio_path"] = audio_path
        result["turn_count"] = len(turns)
        return result
