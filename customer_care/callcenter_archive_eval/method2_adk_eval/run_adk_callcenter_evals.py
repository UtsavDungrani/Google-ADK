"""
Dedicated Runner for Method 2: Google ADK Native AgentEvaluator for Call Center Archive Benchmark.
Evaluates the EvalSet using AgentEvaluator and generates CSV and rich HTML reports.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure customer_care directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_config import EvalConfig
from evals.eval_reporter import generate_html_report


async def run_callcenter_adk_evals(
    eval_set_path: str = "callcenter_archive_eval/method2_adk_eval/callcenter.evalset.json",
    config_path: str = "callcenter_archive_eval/method2_adk_eval/eval_config_callcenter.json",
    agent_module: str = "callcenter_archive_eval.method2_adk_eval.callcenter_agent",
    output_csv: str = "callcenter_archive_eval/method2_adk_eval/callcenter_adk_results.csv",
    output_html: str = "callcenter_archive_eval/method2_adk_eval/callcenter_adk_results.html"
):
    print("=" * 80)
    print("  METHOD 2: GOOGLE ADK NATIVE AGENT EVALUATOR PIPELINE")
    print("  Evaluating Archive 1 Benchmark with Google ADK EvalSet & Rubrics")
    print("=" * 80)
    print(f"• Target Agent Module : {agent_module}")
    print(f"• EvalSet File        : {eval_set_path}")
    print(f"• Eval Config         : {config_path}")
    print(f"• Output CSV          : {output_csv}")
    print(f"• Output HTML         : {output_html}")
    print("=" * 80 + "\n")

    if not os.path.exists(eval_set_path):
        raise FileNotFoundError(f"EvalSet not found at {eval_set_path}")

    with open(eval_set_path, "r", encoding="utf-8") as f:
        eval_set = EvalSet.model_validate_json(f.read())

    print(f"Loaded {len(eval_set.eval_cases)} evaluation cases:")
    for i, case in enumerate(eval_set.eval_cases, 1):
        print(f"  [{i:02d}] {case.eval_id} ({len(case.conversation)} turns)")
    print()

    eval_config = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            eval_config = EvalConfig.model_validate_json(f.read())

    print("Running Google ADK AgentEvaluator.evaluate_eval_set()...\n")
    eval_exception = None

    try:
        await AgentEvaluator.evaluate_eval_set(
            agent_module=agent_module,
            eval_set=eval_set,
            eval_config=eval_config,
            num_runs=1,
            print_detailed_results=True,
            output_file=output_csv
        )
    except Exception as e:
        eval_exception = e

    print("\nCompiling rich HTML dashboard from ADK CSV results...")
    if os.path.exists(output_csv):
        try:
            generate_html_report(
                csv_path=output_csv,
                output_html_path=output_html,
                evalset_path=eval_set_path
            )
            print(f"Successfully generated ADK HTML Report -> {output_html}")
        except Exception as err:
            print(f"[Warning] Failed to generate HTML report: {err}")

    print("\n" + "=" * 80)
    if eval_exception:
        print(f" ADK Evaluation finished with notices: {eval_exception}")
    else:
        print(" ADK Evaluation successfully completed!")
    print(f"• CSV Report  : {output_csv}")
    print(f"• HTML Report : {output_html}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_callcenter_adk_evals())
