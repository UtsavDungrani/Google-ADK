"""
Runner script for Convo AI Voice Caller Evaluations.
Evaluates the benchmark calls and saves results to JSON and CSV.
"""

import os
import sys
import json
import csv
import time
from typing import List, Dict, Any

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from convoai_eval.eval_engine import ConvoAIEvaluator


def run_evals(
    input_calls_path: str = "convoai_data/parsed_calls.json",
    output_dir: str = "convoai_eval/results"
):
    print("=" * 75)
    print("  CONVO AI VOICE CALLER AUTOMATED EVALUATION PIPELINE")
    print("  Powered by Google Gemini 3.6 Flash Voice Evaluation Engine")
    print("=" * 75)

    if not os.path.exists(input_calls_path):
        print(f"Error: Input parsed calls file not found at {input_calls_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    json_out = os.path.join(output_dir, "convoai_eval_results.json")
    csv_out = os.path.join(output_dir, "convoai_eval_results.csv")

    with open(input_calls_path, "r", encoding="utf-8") as f:
        calls = json.load(f)

    print(f"Loaded {len(calls)} call recordings & transcripts for automated grading.\n")

    # Load cached results if available
    cached_map: Dict[int, Dict[str, Any]] = {}
    if os.path.exists(json_out):
        try:
            with open(json_out, "r", encoding="utf-8") as f:
                cached_list = json.load(f)
                for c in cached_list:
                    if "tab_id" in c and c.get("overall_confidence_score"):
                        cached_map[c["tab_id"]] = c
            print(f"Found {len(cached_map)} existing cached evaluations.")
        except Exception:
            pass

    evaluator = ConvoAIEvaluator(model_name="gemini-3.6-flash")
    results: List[Dict[str, Any]] = []

    start_time = time.time()
    for idx, call in enumerate(calls, 1):
        tab_id = call.get("tab_id", idx)
        turns_cnt = len(call.get("turns", []))
        wav_url = call.get("audio_url", "N/A")

        if tab_id in cached_map:
            cached_res = cached_map[tab_id]
            # ensure turns are present
            cached_res["turns"] = call.get("turns", [])
            results.append(cached_res)
            conf = cached_res.get("overall_confidence_score", 0)
            status = cached_res.get("status", "UNKNOWN")
            print(f"[{idx}/{len(calls)}] Call #{tab_id}: [CACHED] -> Conf: {conf}% | Status: {status}")
            continue

        print(f"[{idx}/{len(calls)}] Evaluating Call #{tab_id} ({turns_cnt} turns)...", end="", flush=True)

        eval_res = None
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                eval_res = evaluator.evaluate_call(call)
                break
            except Exception as e:
                if attempt < max_retries:
                    sleep_sec = attempt * 5
                    print(f" [Retrying in {sleep_sec}s due to: {e}]...", end="", flush=True)
                    time.sleep(sleep_sec)
                else:
                    print(f" FAILED after {max_retries} attempts! ({e})")

        if eval_res:
            eval_res["turns"] = call.get("turns", [])
            results.append(eval_res)
            conf = eval_res.get("overall_confidence_score", 0)
            status = eval_res.get("status", "UNKNOWN")
            project = eval_res.get("developer_project", "Real Estate")
            print(f" DONE! -> Conf: {conf}% | Status: {status} | Project: {project}")
            time.sleep(2)  # courteous pacing to avoid rate spikes

    # Sort results by tab_id
    results.sort(key=lambda x: x.get("tab_id", 0))
    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 75)
    print(f"Evaluation finished in {elapsed}s across {len(results)}/{len(calls)} calls.")

    # Save JSON
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved full evaluation JSON -> {json_out}")

    # Save CSV
    if results:
        fieldnames = [
            "tab_id", "developer_project", "caller_persona", "status",
            "overall_confidence_score", "lead_qualification", "site_visit_scheduling",
            "objection_and_boundary", "compliance_and_tone", "conversational_fluency",
            "turn_count", "intent", "configuration", "visit_datetime", "disclosed_pricing", "audio_url"
        ]
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                scores = r.get("scores", {})
                entities = r.get("extracted_entities", {})
                writer.writerow({
                    "tab_id": r.get("tab_id"),
                    "developer_project": r.get("developer_project"),
                    "caller_persona": r.get("caller_persona"),
                    "status": r.get("status"),
                    "overall_confidence_score": r.get("overall_confidence_score"),
                    "lead_qualification": scores.get("lead_qualification"),
                    "site_visit_scheduling": scores.get("site_visit_scheduling"),
                    "objection_and_boundary": scores.get("objection_and_boundary"),
                    "compliance_and_tone": scores.get("compliance_and_tone"),
                    "conversational_fluency": scores.get("conversational_fluency"),
                    "turn_count": r.get("turn_count"),
                    "intent": entities.get("intent"),
                    "configuration": entities.get("configuration"),
                    "visit_datetime": entities.get("visit_datetime"),
                    "disclosed_pricing": entities.get("disclosed_pricing"),
                    "audio_url": r.get("audio_url"),
                })
        print(f"Saved tabular metrics CSV -> {csv_out}")

    # Fleet summary stats
    if results:
        avg_conf = sum(r.get("overall_confidence_score", 0) for r in results) / len(results)
        passed_cnt = sum(1 for r in results if r.get("status") in ["EXCELLENT", "PASSED"])
        print("\n--- FLEET PERFORMANCE SUMMARY ---")
        print(f"• Overall Fleet Average Confidence: {avg_conf:.1f}%")
        print(f"• Overall Pass Rate               : {passed_cnt}/{len(results)} ({passed_cnt/len(results)*100:.1f}%)")
        print("=" * 75 + "\n")

    return results


if __name__ == "__main__":
    run_evals()
