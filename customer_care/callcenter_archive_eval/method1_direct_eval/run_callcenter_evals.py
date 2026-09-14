"""
Runner for Method 1: Direct Multilingual Call Center Evaluations.
Evaluates all 11 calls, outputs JSON and CSV metrics.
"""

import os
import sys
import json
import csv
import time
from typing import List, Dict, Any

# Ensure project root is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from callcenter_archive_eval.method1_direct_eval.eval_engine import CallCenterEvaluator


def run_callcenter_evals(
    input_calls_path: str = "callcenter_archive_eval/data/parsed_calls.json",
    output_dir: str = "callcenter_archive_eval/method1_direct_eval/results"
):
    print("=" * 80)
    print("  METHOD 1: DIRECT MULTILINGUAL CALL CENTER EVALUATION PIPELINE")
    print("  Evaluating Archive 1 Call Samples with Gemini 3.6 Flash LLM-as-a-Judge")
    print("=" * 80)

    if not os.path.exists(input_calls_path):
        raise FileNotFoundError(f"Input parsed calls file not found at {input_calls_path}")

    os.makedirs(output_dir, exist_ok=True)
    json_out = os.path.join(output_dir, "callcenter_eval_results.json")
    csv_out = os.path.join(output_dir, "callcenter_eval_results.csv")

    with open(input_calls_path, "r", encoding="utf-8") as f:
        calls = json.load(f)

    print(f"Loaded {len(calls)} calls for automated evaluation.\n")

    # Load cache if available
    cached_map: Dict[str, Dict[str, Any]] = {}
    if os.path.exists(json_out):
        try:
            with open(json_out, "r", encoding="utf-8") as f:
                cached_list = json.load(f)
                for c in cached_list:
                    if c.get("call_id") and c.get("overall_confidence_score") is not None:
                        cached_map[c["call_id"]] = c
            print(f"Found {len(cached_map)} existing cached evaluations.")
        except Exception:
            pass

    evaluator = CallCenterEvaluator(model_name="gemini-3.6-flash")
    results: List[Dict[str, Any]] = []

    start_time = time.time()
    for idx, call in enumerate(calls, 1):
        cid = call.get("call_id", str(idx))
        tag = call.get("call_tag", "Call")
        turns_cnt = call.get("turn_count", len(call.get("turns", [])))

        if cid in cached_map:
            cached_res = cached_map[cid]
            cached_res["turns"] = call.get("turns", [])
            cached_res["metadata"] = call.get("metadata", {})
            results.append(cached_res)
            conf = cached_res.get("overall_confidence_score", 0)
            status = cached_res.get("status", "UNKNOWN")
            print(f"[{idx}/{len(calls)}] Call #{cid} ({tag}): [CACHED] -> Conf: {conf}% | Status: {status}")
            continue

        print(f"[{idx}/{len(calls)}] Evaluating Call #{cid} ({tag} - {turns_cnt} turns)...", end="", flush=True)

        eval_res = None
        for attempt in range(1, 4):
            try:
                eval_res = evaluator.evaluate_call(call)
                break
            except Exception as e:
                if attempt < 3:
                    sleep_sec = attempt * 4
                    print(f" [Retry in {sleep_sec}s: {e}]...", end="", flush=True)
                    time.sleep(sleep_sec)
                else:
                    print(f" FAILED! ({e})")

        if eval_res:
            eval_res["turns"] = call.get("turns", [])
            eval_res["metadata"] = call.get("metadata", {})
            results.append(eval_res)
            conf = eval_res.get("overall_confidence_score", 0)
            status = eval_res.get("status", "UNKNOWN")
            domain = eval_res.get("domain", "General")
            print(f" DONE! -> Conf: {conf}% | Status: {status} | Domain: {domain}")
            time.sleep(1.5)

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 80)
    print(f"Evaluation complete in {elapsed}s across {len(results)}/{len(calls)} calls.")

    # Save full JSON
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Saved evaluation JSON -> {json_out}")

    # Save summary CSV
    if results:
        fieldnames = [
            "call_id", "call_tag", "domain", "language", "status",
            "overall_confidence_score", "resolution_and_effectiveness",
            "security_compliance_and_policy", "customer_empathy_and_tone",
            "conversational_fluency_and_clarity", "turn_count",
            "customer_core_issue", "risk_level", "call_outcome", "audio_file"
        ]
        with open(csv_out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                scores = r.get("scores", {})
                entities = r.get("extracted_entities", {})
                writer.writerow({
                    "call_id": r.get("call_id"),
                    "call_tag": r.get("call_tag"),
                    "domain": r.get("domain"),
                    "language": r.get("language"),
                    "status": r.get("status"),
                    "overall_confidence_score": r.get("overall_confidence_score"),
                    "resolution_and_effectiveness": scores.get("resolution_and_effectiveness"),
                    "security_compliance_and_policy": scores.get("security_compliance_and_policy"),
                    "customer_empathy_and_tone": scores.get("customer_empathy_and_tone"),
                    "conversational_fluency_and_clarity": scores.get("conversational_fluency_and_clarity"),
                    "turn_count": r.get("turn_count"),
                    "customer_core_issue": entities.get("customer_core_issue"),
                    "risk_level": entities.get("risk_level"),
                    "call_outcome": entities.get("call_outcome"),
                    "audio_file": r.get("audio_file")
                })
        print(f"Saved metrics CSV -> {csv_out}")

        avg_conf = sum(r.get("overall_confidence_score", 0) for r in results) / len(results)
        passed_cnt = sum(1 for r in results if r.get("status") in ["EXCELLENT", "PASSED"])
        print("\n--- FLEET QA METRICS SUMMARY ---")
        print(f"• Average Confidence Score : {avg_conf:.1f}%")
        print(f"• Compliance / Pass Rate   : {passed_cnt}/{len(results)} ({passed_cnt/len(results)*100:.1f}%)")
        print("=" * 80 + "\n")

    return results


if __name__ == "__main__":
    run_callcenter_evals()
