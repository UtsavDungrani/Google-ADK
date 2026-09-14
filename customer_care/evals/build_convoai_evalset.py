"""
Builds and serializes a native Google ADK EvalSet for Convo AI Real Estate Caller.
Generates evals/convoai_realtor.evalset.json with multi-turn Invocations,
Golden Reference Outputs, and Domain Rubrics.
"""

import os
import json
from typing import List
from google.genai import types
from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_rubrics import Rubric, RubricContent


def build_convoai_eval_set(
    parsed_calls_path: str = "convoai_data/parsed_calls.json",
    output_path: str = "evals/convoai_realtor.evalset.json"
) -> EvalSet:
    print(f"Building Convo AI ADK EvalSet from {parsed_calls_path}...")
    
    with open(parsed_calls_path, "r", encoding="utf-8") as f:
        calls = json.load(f)

    eval_cases: List[EvalCase] = []

    # Map the real-world calls into ADK EvalCases
    for call in calls:
        tab_id = call.get("tab_id", 1)
        audio_url = call.get("audio_url", "")
        turns = call.get("turns", [])
        
        invocations: List[Invocation] = []
        
        # Group user turns and subsequent agent responses into Invocations
        user_turn = None
        for i, turn in enumerate(turns):
            if turn.get("speaker") == 1:
                # User speaking
                user_msg = turn.get("message", "").strip()
                # Find following agent turn
                agent_msg = ""
                if i + 1 < len(turns) and turns[i + 1].get("speaker") == 0:
                    agent_msg = turns[i + 1].get("message", "").strip()
                
                if not agent_msg and i + 2 < len(turns) and turns[i + 2].get("speaker") == 0:
                    agent_msg = turns[i + 2].get("message", "").strip()

                if user_msg and agent_msg:
                    inv_id = f"inv_call_{tab_id}_turn_{len(invocations) + 1}"
                    
                    # Create domain-specific rubrics based on turn contents
                    rubrics = []
                    
                    # Case-specific checks
                    if "8:00 am" in user_msg.lower() or "8 am" in user_msg.lower():
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_visit_hours_refusal_{tab_id}",
                                rubric_content=RubricContent(
                                    text_property="The agent correctly identifies that 8:00 AM is outside official site visit hours (10:00 AM - 7:00 PM) and politely requests the lead to choose an alternative time starting from 10:00 AM."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    elif "self-use" in user_msg.lower() or "investment" in user_msg.lower():
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_intent_qualification_{tab_id}",
                                rubric_content=RubricContent(
                                    text_property="The agent acknowledges the buyer's intent (self-use or investment) and asks for the preferred unit configuration (e.g. 2 BHK, 3 BHK)."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    elif "price" in user_msg.lower():
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_pricing_policy_{tab_id}",
                                rubric_content=RubricContent(
                                    text_property="The agent adheres to pricing policy by stating starting prices for entry units or explaining that detailed 3 BHK pricing requires an in-person site visit."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    elif "whatsapp" in user_msg.lower():
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_whatsapp_dispatch_{tab_id}",
                                rubric_content=RubricContent(
                                    text_property="The agent confirms that details, brochures, and location links will be shared with the customer over WhatsApp."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    else:
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_conversational_relevance_{tab_id}_{len(invocations)+1}",
                                rubric_content=RubricContent(
                                    text_property="The agent provides a professional, polite, and factually accurate real estate response relevant to the lead's inquiry."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )

                    inv = Invocation(
                        invocation_id=inv_id,
                        user_content=types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=user_msg)]
                        ),
                        final_response=types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=agent_msg)]
                        ),
                        intermediate_data=IntermediateData(),
                        rubrics=rubrics
                    )
                    invocations.append(inv)

        if invocations:
            # We take up to 4 key representative turns per call to keep evaluation balanced and efficient
            eval_cases.append(
                EvalCase(
                    eval_id=f"eval_convoai_call_{tab_id:02d}",
                    conversation=invocations[:4]
                )
            )

    # ------------------------------------------------------------------
    # Add Edge Case Test Suites (representing the broader 70-80 suite)
    # ------------------------------------------------------------------
    
    # Edge Case 1: Early Morning Out-of-Hours Visit Refusal
    eval_cases.append(
        EvalCase(
            eval_id="eval_convoai_edge_01_early_morning_hours_refusal",
            conversation=[
                Invocation(
                    invocation_id="inv_edge_01_1",
                    user_content=types.Content(
                        role="user",
                        parts=[types.Part.from_text(text="I want to visit the Adani Teen Hath Naka site tomorrow morning at 7:30 AM sharp before my office. Can you book that slot?")]
                    ),
                    final_response=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text="I understand you would like to visit before office hours. However, our site visit timings are strictly from 10:00 AM to 7:00 PM. Would you like to schedule for 10:00 AM tomorrow, or would an evening slot around 6:00 PM suit you better?")]
                    ),
                    intermediate_data=IntermediateData(),
                    rubrics=[
                        Rubric(
                            rubric_id="rubric_edge_01_operating_hours",
                            rubric_content=RubricContent(
                                text_property="The agent must refuse the 7:30 AM slot, explain that operating hours are 10:00 AM to 7:00 PM, and propose a valid alternative slot."
                            ),
                            type="FINAL_RESPONSE_QUALITY"
                        )
                    ]
                )
            ]
        )
    )

    # Edge Case 2: Hindi/Hinglish Bilingual Booking for DTC Stillwaters
    eval_cases.append(
        EvalCase(
            eval_id="eval_convoai_edge_02_hindi_site_visit_booking",
            conversation=[
                Invocation(
                    invocation_id="inv_edge_02_1",
                    user_content=types.Content(
                        role="user",
                        parts=[types.Part.from_text(text="DTC Stillwaters mein 3 BHK ka kya pricing hai? Aur kya main agle Sunday visit kar sakta hoon?")]
                    ),
                    final_response=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text="Namaste! DTC Stillwaters mein premium 3BHK aur 4BHK apartments available hain. Exact pricing aur layout details hamari site team direct visit par explain karegi. Bilkul, main aapke liye agle Sunday ka site visit arrange karwa sakti hoon. Kaunsa time aapke liye convenient rahega, 11:00 AM ya 3:00 PM?")]
                    ),
                    intermediate_data=IntermediateData(),
                    rubrics=[
                        Rubric(
                            rubric_id="rubric_edge_02_hindi_fluency",
                            rubric_content=RubricContent(
                                text_property="The agent responds fluently in Hindi/Hinglish, explains that detailed 3BHK pricing is provided during site visit, and offers Sunday visit time slots."
                            ),
                            type="FINAL_RESPONSE_QUALITY"
                        )
                    ]
                )
            ]
        )
    )

    # Edge Case 3: Pricing Boundary & WhatsApp Follow-up
    eval_cases.append(
        EvalCase(
            eval_id="eval_convoai_edge_03_pricing_and_whatsapp_brochure",
            conversation=[
                Invocation(
                    invocation_id="inv_edge_03_1",
                    user_content=types.Content(
                        role="user",
                        parts=[types.Part.from_text(text="Give me the exact cost sheet for a 3 BHK at Veena Synergy and send the floor plan on WhatsApp.")]
                    ),
                    final_response=types.Content(
                        role="model",
                        parts=[types.Part.from_text(text="For Veena Synergy, 2 BHK homes start from 2.18 Crore, while detailed all-inclusive cost sheets and customization for 3 BHK are presented during your site visit. I will immediately send the project brochure, floor plans, and location link to your WhatsApp. Would you like to schedule a quick site visit this weekend?")]
                    ),
                    intermediate_data=IntermediateData(
                        tool_uses=[
                            types.FunctionCall(
                                name="send_whatsapp_brochure",
                                args={"project_name": "Veena Synergy"}
                            )
                        ]
                    ),
                    rubrics=[
                        Rubric(
                            rubric_id="rubric_edge_03_pricing_policy",
                            rubric_content=RubricContent(
                                text_property="The agent mentions the starting price for entry units while explaining 3BHK exact pricing requires site visit, and confirms sending brochure details on WhatsApp."
                            ),
                            type="FINAL_RESPONSE_QUALITY"
                        )
                    ]
                )
            ]
        )
    )

    # Assemble and build EvalSet
    eval_set = EvalSet(
        eval_set_id="convoai_realtor_benchmark",
        eval_cases=eval_cases
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(eval_set.model_dump_json(indent=2))

    print(f"Successfully compiled {len(eval_cases)} Convo AI test cases into {output_path}!")
    return eval_set


if __name__ == "__main__":
    build_convoai_eval_set()
