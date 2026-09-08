"""
Unit and Integration Tests for ADK Evaluation HTML Report Generator.
Validates CSV parsing, run boundary detection, markdown rendering, tool call extraction,
HTML generation with minimal CSS, and FastAPI reporting endpoints.
"""

import os
import sys
import tempfile
import unittest
from fastapi.testclient import TestClient

# Ensure customer_care directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from evals.eval_reporter import (
    parse_csv_runs,
    _format_markdown_snippet,
    _parse_tool_calls,
    _human_metric_name,
    _human_case_title,
    generate_html_report,
    generate_html_content
)
from server import app


class TestEvalReport(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        self.csv_path = os.path.join(current_dir, "evals", "eval_results.csv")
        self.evalset_path = os.path.join(current_dir, "evals", "customer_care.evalset.json")

    def test_01_parse_existing_csv_runs(self):
        """Ensures the real eval_results.csv is parsed into runs and test cases."""
        self.assertTrue(os.path.exists(self.csv_path), "evals/eval_results.csv must exist.")
        runs = parse_csv_runs(self.csv_path)
        self.assertGreaterEqual(len(runs), 1, "Should detect at least 1 evaluation run.")
        
        latest = runs[-1]
        self.assertIn(latest["total_cases"], [6, 9], "Customer care benchmark has 6 or 9 test cases.")
        self.assertGreaterEqual(latest["total_metrics"], 18, "At least 18 metric rows per run.")
        self.assertIn("metric_pass_rate", latest)
        self.assertIn("case_pass_rate", latest)

    def test_02_markdown_snippet_formatting(self):
        """Tests that markdown formatting renders bold, code, bullets, and paragraphs."""
        raw_md = "**Bold Step**: Try `rebooting` the router.\n* Bullet 1\n* Bullet 2"
        html_out = _format_markdown_snippet(raw_md)
        self.assertIn("<strong>Bold Step</strong>", html_out)
        self.assertIn("<code class='inline-code'>rebooting</code>", html_out)
        self.assertIn("<ul class='cell-list'>", html_out)
        self.assertIn("<li>Bullet 1</li>", html_out)

    def test_03_tool_calls_parsing(self):
        """Tests parsing of single and multiple ADK FunctionCall strings."""
        # Empty tool calls
        self.assertEqual(_parse_tool_calls(""), [])
        self.assertEqual(_parse_tool_calls(None), [])

        # Single call
        raw_call = "id='call_01' args={'order_id': 'ORD-10021'} name='track_shipment' partial_args=None will_continue=None"
        parsed = _parse_tool_calls(raw_call)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["name"], "track_shipment")
        self.assertEqual(parsed[0]["call_id"], "call_01")
        self.assertIn("ORD-10021", parsed[0]["args_formatted"])

        # Multiple calls across newlines
        multi_calls = (
            "id=None args={'agent_name': 'order_logistics_specialist'} name='transfer_to_agent' partial_args=None will_continue=None\n"
            "id='call_02' args={'order_id': 'ORD-10021'} name='track_shipment' partial_args=None will_continue=None"
        )
        parsed_multi = _parse_tool_calls(multi_calls)
        self.assertEqual(len(parsed_multi), 2)
        self.assertEqual(parsed_multi[0]["name"], "transfer_to_agent")
        self.assertEqual(parsed_multi[1]["name"], "track_shipment")

    def test_04_generate_html_report(self):
        """Tests end-to-end HTML report generation to a temporary file."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            out_path = generate_html_report(
                csv_path=self.csv_path,
                output_html_path=tmp_path,
                evalset_path=self.evalset_path
            )
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("Tabular Results Report", content)
            self.assertIn("eval_status", content)
            self.assertIn("metric_name", content)
            self.assertIn("expected_tool_calls", content)
            self.assertIn("actual_tool_calls", content)
            self.assertIn("case_01_order_tracking", content)
            self.assertIn("case_03_hardware_troubleshooting", content)
            self.assertIn("adk-table", content)
            self.assertIn("filterTableRows", content)
            self.assertIn("searchTables", content)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_05_fastapi_eval_report_endpoints(self):
        """Tests GET /evals and GET /api/evals/report return 200 and text/html."""
        res1 = self.client.get("/evals")
        self.assertEqual(res1.status_code, 200)
        self.assertIn("text/html", res1.headers["content-type"])
        self.assertIn("Tabular Results Report", res1.text)

        res2 = self.client.get("/api/evals/report")
        self.assertEqual(res2.status_code, 200)
        self.assertIn("text/html", res2.headers["content-type"])
    def test_06_multiturn_evalset_and_turn_badges(self):
        """Tests multi-turn evalset structure and turn badge rendering in HTML."""
        import json
        with open(self.evalset_path, "r", encoding="utf-8") as f:
            evalset_data = json.load(f)

        cases_map = {c["eval_id"]: c for c in evalset_data.get("eval_cases", [])}
        self.assertEqual(len(cases_map), 9, "Evalset should define 9 benchmark cases.")
        
        # Verify turn counts for multi-turn cases
        self.assertEqual(len(cases_map["case_07_multiturn_rma_journey"]["conversation"]), 3)
        self.assertEqual(len(cases_map["case_08_multiturn_diagnostics_to_ticket"]["conversation"]), 2)
        self.assertEqual(len(cases_map["case_09_multiturn_delay_escalation"]["conversation"]), 2)

        # Synthetic multi-turn rows
        synthetic_rows = [
            "eval_set_id,eval_id,metric_name,threshold,score,eval_status,prompt,expected_response,actual_response,expected_tool_calls,actual_tool_calls",
            "customer_care_evals,case_07_multiturn_rma_journey,rubric_turn1_rma_ask_id_quality,1.0,1.0,PASSED,I want to return an item,What is your order ID?,Could you share your order ID?,,",
            "customer_care_evals,case_07_multiturn_rma_journey,rubric_turn2_rma_eligibility_response,1.0,1.0,PASSED,My order is ORD-10021,Your order is eligible,Eligible for full refund,name='check_return_eligibility' args={'order_id': 'ORD-10021'},name='check_return_eligibility' args={'order_id': 'ORD-10021'}",
            "customer_care_evals,case_07_multiturn_rma_journey,rubric_turn3_rma_create_response,1.0,1.0,PASSED,Generate return label,RMA created,RMA-10021 created,name='create_rma_return' args={'order_id': 'ORD-10021'},name='create_rma_return' args={'order_id': 'ORD-10021'}"
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", mode="w", delete=False, encoding="utf-8") as tf:
            tf.write("\n".join(synthetic_rows))
            synth_csv = tf.name

        try:
            runs = parse_csv_runs(synth_csv)
            self.assertEqual(len(runs), 1)
            run = runs[0]
            self.assertEqual(run["total_cases"], 1)
            self.assertEqual(len(run["rows"]), 3)
            self.assertEqual(run["rows"][0]["turn_idx"], 1)
            self.assertEqual(run["rows"][0]["total_turns"], 3)
            self.assertEqual(run["rows"][1]["turn_idx"], 2)
            self.assertEqual(run["rows"][2]["turn_idx"], 3)

            html_content = generate_html_content(runs, {"eval_set_id": "customer_care_evals"})
            self.assertIn(".badge-turn", html_content)
            self.assertIn("Turn 1/3", html_content)
            self.assertIn("Turn 2/3", html_content)
            self.assertIn("Turn 3/3", html_content)
        finally:
            if os.path.exists(synth_csv):
                os.remove(synth_csv)


if __name__ == "__main__":
    unittest.main()

