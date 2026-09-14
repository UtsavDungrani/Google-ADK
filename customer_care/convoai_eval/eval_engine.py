"""
Convo AI Evaluation Engine.
Evaluates real estate voice caller transcripts against domain-specific rubrics
using Gemini as an expert conversational AI evaluator.
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

EVALUATION_SYSTEM_PROMPT = """
You are an expert Voice Conversational AI Evaluation Engineer specializing in Real Estate Voice Agents.
Your task is to thoroughly analyze real call transcripts between an AI Caller Agent (speaker: 0) and prospective real estate leads/customers (speaker: 1).

You must evaluate the agent's performance with precision, identifying conversational nuance, factual fidelity, objection handling, operational policy adherence, and model confidence.

Scoring Criteria (Grade each from 0 to 100):
1. overall_confidence_score: The calibrated confidence that the AI agent understood user intent, maintained conversation control, avoided hallucinations, and handled the dialogue appropriately without confusion.
2. lead_qualification_score: How effectively the agent discovered buyer intent (self-use vs. investment, BHK configuration 2/3/4 BHK, budget, timeline).
3. site_visit_scheduling_score: How effectively the agent drove towards and scheduled an on-site visit or callback, negotiating date, time, and follow-up (e.g. WhatsApp confirmation).
4. objection_and_boundary_score: How well the agent enforced operational boundaries (e.g. site visit operating hours 10 AM - 7 PM, refusing impossible timings like 8 AM politely, following pricing disclosure policies where 3BHK prices require site visits).
5. compliance_and_tone_score: Call recording consent disclosure ("This call is now being recorded"), polite professional demeanor, courteous opening and closing.
6. conversational_fluency_score: Natural flow, avoidance of awkward repetition or looping, effective handling of silence/interruption, and smooth handling of language (including English and Hindi/Hinglish code-switching).

You must output your evaluation strictly as valid JSON adhering to the following JSON schema:
{
  "call_id": int,
  "developer_project": string,
  "caller_persona": string,
  "status": "EXCELLENT" | "PASSED" | "NEEDS_REVIEW" | "CRITICAL_ISSUE",
  "overall_confidence_score": int (0-100),
  "scores": {
    "lead_qualification": int (0-100),
    "site_visit_scheduling": int (0-100),
    "objection_and_boundary": int (0-100),
    "compliance_and_tone": int (0-100),
    "conversational_fluency": int (0-100)
  },
  "extracted_entities": {
    "intent": string,
    "configuration": string,
    "visit_datetime": string,
    "channel_followup": string,
    "disclosed_pricing": string
  },
  "executive_summary": string,
  "key_strengths": [string],
  "weaknesses_or_flags": [string],
  "actionable_recommendations": [string]
}
"""


class ConvoAIEvaluator:
    def __init__(self, model_name: str = "gemini-3.6-flash"):
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def evaluate_call(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single call record containing tab_id, audio_url, and turns.
        """
        tab_id = call_data.get("tab_id", 0)
        audio_url = call_data.get("audio_url", "")
        turns = call_data.get("turns", [])

        # Format transcript for prompt
        formatted_dialogue = []
        for turn in turns:
            role = "AI AGENT" if turn.get("speaker") == 0 else "CUSTOMER"
            msg = turn.get("message", "").strip()
            formatted_dialogue.append(f"[{role}]: {msg}")

        transcript_str = "\n".join(formatted_dialogue)

        prompt = f"""
Call ID / Tab: {tab_id}
Audio Recording Link: {audio_url}

FULL CALL TRANSCRIPT:
{transcript_str}

Please perform a rigorous evaluation of the AI AGENT in this real estate conversation. Return only the JSON object as specified.
"""

        response = None
        models_to_try = [self.model_name, "gemini-3.5-flash-lite"]
        last_err = None
        for m in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=m,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=prompt)]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=EVALUATION_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )
                break
            except Exception as e:
                last_err = e
                continue

        if not response:
            raise last_err

        try:
            result_json = json.loads(response.text)
            result_json["tab_id"] = tab_id
            result_json["audio_url"] = audio_url
            result_json["turn_count"] = len(turns)
            return result_json
        except Exception as err:
            # Fallback if parsing fails
            clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            result_json = json.loads(clean_text)
            result_json["tab_id"] = tab_id
            result_json["audio_url"] = audio_url
            result_json["turn_count"] = len(turns)
            return result_json
