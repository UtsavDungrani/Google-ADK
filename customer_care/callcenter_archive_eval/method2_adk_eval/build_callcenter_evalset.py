"""
Builds and serializes a native Google ADK EvalSet for the Multilingual Call Center Benchmark.
Creates multi-turn Invocations, Golden Reference Outputs, and Domain Rubrics for all 11 calls.
"""

import os
import json
from typing import List
from google.genai import types
from google.adk.evaluation.eval_case import EvalCase, Invocation, IntermediateData
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_rubrics import Rubric, RubricContent


def build_callcenter_eval_set(
    parsed_calls_path: str = "callcenter_archive_eval/data/parsed_calls.json",
    output_path: str = "callcenter_archive_eval/method2_adk_eval/callcenter.evalset.json"
) -> EvalSet:
    print(f"Building Google ADK Call Center EvalSet from: {parsed_calls_path}")

    with open(parsed_calls_path, "r", encoding="utf-8") as f:
        calls = json.load(f)

    eval_cases: List[EvalCase] = []

    for call in calls:
        call_id = call.get("call_id", "")
        call_tag = call.get("call_tag", "call")
        turns = call.get("turns", [])
        metadata = call.get("metadata", {})

        clean_tag = call_tag.lower().replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
        eval_case_id = f"eval_call_{call_id[:10]}_{clean_tag}"

        invocations: List[Invocation] = []

        # Find customer turns followed by agent responses
        for i, turn in enumerate(turns):
            if turn.get("speaker_role") == "CUSTOMER":
                cust_msg = turn.get("text", "").strip()
                agent_msg = ""
                # Next turn by agent
                if i + 1 < len(turns) and turns[i + 1].get("speaker_role") == "AGENT":
                    agent_msg = turns[i + 1].get("text", "").strip()

                if cust_msg and agent_msg:
                    inv_id = f"inv_{call_id[:8]}_turn_{len(invocations) + 1}"

                    # Domain specific rubrics based on content & call tag
                    rubrics = []
                    lower_tag = call_tag.lower()
                    lower_cust = cust_msg.lower()

                    if "sale" in lower_tag:
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_sales_handling_{len(invocations)+1}",
                                rubric_content=RubricContent(
                                    text_property="The agent presents products/services clearly, addresses customer hesitations or objections courteously, and seeks to advance the commercial conversation."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    elif "billing" in lower_tag or "finance" in lower_tag:
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_financial_accuracy_{len(invocations)+1}",
                                rubric_content=RubricContent(
                                    text_property="The agent provides transparent financial or billing explanations, clarifies payment or withdrawal procedures, and adheres to payment safety standards."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )
                    else:
                        rubrics.append(
                            Rubric(
                                rubric_id=f"rubric_support_resolution_{len(invocations)+1}",
                                rubric_content=RubricContent(
                                    text_property="The agent patiently troubleshoots the customer problem, provides clear step-by-step guidance, and maintains a supportive and reassuring tone."
                                ),
                                type="FINAL_RESPONSE_QUALITY"
                            )
                        )

                    # General conversational quality rubric
                    rubrics.append(
                        Rubric(
                            rubric_id=f"rubric_professional_tone_{len(invocations)+1}",
                            rubric_content=RubricContent(
                                text_property="The agent communicates professionally, politely, and without offensive or misleading statements."
                            ),
                            type="FINAL_RESPONSE_QUALITY"
                        )
                    )

                    inv = Invocation(
                        invocation_id=inv_id,
                        user_content=types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=cust_msg)]
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
            # We take up to 4 key representative interaction turns per call to ensure balanced evaluation
            eval_cases.append(
                EvalCase(
                    eval_id=eval_case_id,
                    conversation=invocations[:4]
                )
            )

    eval_set = EvalSet(
        eval_set_id="multilingual_callcenter_archive1_benchmark",
        eval_cases=eval_cases
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(eval_set.model_dump_json(indent=2))

    print(f"Successfully compiled {len(eval_cases)} Call Center EvalCases into {output_path}!")
    return eval_set


if __name__ == "__main__":
    build_callcenter_eval_set()
