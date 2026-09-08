"""
Evaluation Runner for Customer Care Multi-Agent System.
Runs Google ADK native evaluations using AgentEvaluator and EvalSet.
"""

import os
import sys
import asyncio
import argparse
from typing import Optional
from dotenv import load_dotenv

# Ensure customer_care directory is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

load_dotenv()

from google.adk.evaluation.agent_evaluator import AgentEvaluator
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.eval_config import EvalConfig
from google.adk.evaluation.local_eval_sets_manager import load_eval_set_from_file

try:
    from evals.eval_reporter import generate_html_report
except ImportError:
    from eval_reporter import generate_html_report


async def run_evaluations(
    eval_set_path: str = "evals/customer_care.evalset.json",
    config_path: str = "evals/eval_config.json",
    num_runs: int = 1,
    output_file: str = "evals/eval_results.csv",
    html_output_file: Optional[str] = None,
    generate_html: bool = True
):
    if not html_output_file:
        html_output_file = output_file.replace(".csv", ".html")
        if not html_output_file.endswith(".html"):
            html_output_file += ".html"

    print("=" * 70)
    print("  GOOGLE ADK CUSTOMER CARE AGENT EVALUATION")
    print("=" * 70)
    print(f"• Target Agent Module : customer_care.agent (root_agent)")
    print(f"• Eval Dataset Path   : {eval_set_path}")
    print(f"• Config File Path    : {config_path}")
    print(f"• Iteration Runs      : {num_runs}")
    print(f"• Output CSV Path     : {output_file}")
    if generate_html:
        print(f"• Output HTML Report  : {html_output_file}")
    print("=" * 70 + "\n")

    if not os.path.exists(eval_set_path):
        print(f"Error: EvalSet file '{eval_set_path}' not found.")
        print("Please generate it first by running: python evals/build_eval_set.py")
        sys.exit(1)

    eval_set_id = os.path.basename(eval_set_path).replace(".evalset.json", "")
    with open(eval_set_path, "r", encoding="utf-8") as f:
        eval_set = EvalSet.model_validate_json(f.read())
    print(f"Loaded {len(eval_set.eval_cases)} evaluation cases:")
    for i, case in enumerate(eval_set.eval_cases, 1):
        print(f"  [{i}] {case.eval_id}")
    print()

    eval_config = None
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            eval_config = EvalConfig.model_validate_json(f.read())

    print("Starting evaluation execution with ADK AgentEvaluator...\n")
    eval_exception = None

    try:
        await AgentEvaluator.evaluate_eval_set(
            agent_module="agent",
            eval_set=eval_set,
            eval_config=eval_config,
            num_runs=num_runs,
            print_detailed_results=True,
            output_file=output_file
        )
    except Exception as e:
        eval_exception = e

    # Generate rich HTML dashboard report from the CSV results
    generated_html_path = None
    if generate_html and output_file and os.path.exists(output_file):
        try:
            generated_html_path = generate_html_report(
                csv_path=output_file,
                output_html_path=html_output_file,
                evalset_path=eval_set_path
            )
        except Exception as report_err:
            print(f"\n[Warning] HTML report compilation encountered an issue: {report_err}")

    print("\n" + "=" * 70)
    if eval_exception is None:
        print(" Evaluation completed successfully! All criteria passed.")
    else:
        print(" Evaluation finished with failures or warnings:")
        print(f"   {eval_exception}")

    if output_file and os.path.exists(output_file):
        print(f"• CSV Results  : {output_file}")
    if generated_html_path and os.path.exists(generated_html_path):
        file_uri = "file:///" + os.path.abspath(generated_html_path).replace("\\", "/")
        print(f"• HTML Report  : {generated_html_path}")
        print(f"• Browser Link : {file_uri}")
    print("=" * 70)

    if eval_exception:
        raise eval_exception


def main():
    parser = argparse.ArgumentParser(description="Run ADK Agent Evaluations for Customer Care")
    parser.add_argument(
        "--eval-set",
        default=os.path.join(current_dir, "evals", "customer_care.evalset.json"),
        help="Path to .evalset.json file"
    )
    parser.add_argument(
        "--config",
        default=os.path.join(current_dir, "evals", "eval_config.json"),
        help="Path to eval_config.json"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per test case"
    )
    parser.add_argument(
        "--output",
        default=os.path.join(current_dir, "evals", "eval_results.csv"),
        help="CSV output report file"
    )
    parser.add_argument(
        "--html-output",
        default=None,
        help="HTML output report file (defaults to matching .html filename in evals/)"
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Disable automatic HTML report generation"
    )

    args = parser.parse_args()
    asyncio.run(run_evaluations(
        eval_set_path=args.eval_set,
        config_path=args.config,
        num_runs=args.runs,
        output_file=args.output,
        html_output_file=args.html_output,
        generate_html=not args.no_html
    ))


if __name__ == "__main__":
    main()
