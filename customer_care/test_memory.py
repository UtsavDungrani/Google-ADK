"""
Unit and Integration Tests for Cross-Session Long-Term Memory
Tests memory retrieval, context formatting, note persistence, episodic timeline,
ADK tool functions, session consolidation, and FastAPI endpoints.
"""

import sys
import unittest
from fastapi.testclient import TestClient

from memory_service import (
    get_customer_profile,
    list_all_profiles,
    save_customer_profile,
    add_customer_note,
    record_customer_episode,
    get_customer_episodes,
    format_cross_session_context,
    consolidate_session_memory
)
from care_tools import (
    recall_customer_memory,
    save_customer_fact,
    get_cross_session_timeline,
    lookup_order
)
from server import app


class TestCrossSessionMemory(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_profile_retrieval(self):
        """Tests that customer profiles can be found by ID, email, name, or order ID."""
        # By customer ID
        p1 = get_customer_profile("CUST-9921")
        self.assertIsNotNone(p1)
        self.assertEqual(p1["customer_name"], "Alex Mercer")

        # By email
        p2 = get_customer_profile("s.connor@example.com")
        self.assertIsNotNone(p2)
        self.assertEqual(p2["customer_id"], "CUST-8812")

        # By name
        p3 = get_customer_profile("David Kim")
        self.assertIsNotNone(p3)
        self.assertEqual(p3["customer_id"], "CUST-7741")

        # By Order ID
        p4 = get_customer_profile("ORD-10021")
        self.assertIsNotNone(p4)
        self.assertEqual(p4["customer_name"], "Alex Mercer")

    def test_02_context_synthesizer(self):
        """Tests that synthesized context contains customer traits, devices, and episodes."""
        ctx = format_cross_session_context("CUST-9921")
        self.assertIn("Alex Mercer", ctx)
        self.assertIn("UltraHD 65\" 4K Smart TV", ctx)
        self.assertIn("TCK-10021-VND", ctx)
        self.assertIn("CROSS-SESSION LONG-TERM CUSTOMER MEMORY RECALL", ctx)

    def test_03_note_persistence(self):
        """Tests learning and persisting new facts into customer long-term profile."""
        test_note = "Prefers French communication when discussing billing"
        add_customer_note("CUST-8812", test_note)
        p = get_customer_profile("CUST-8812")
        self.assertIn(test_note, p.get("persistent_notes", []))

    def test_04_episodic_memory(self):
        """Tests creating and querying chronological interaction episodes."""
        ep = record_customer_episode(
            customer_id="CUST-9921",
            session_id="test_sess_001",
            summary="Customer inquired about Smart TV HDMI 2.1 gaming port.",
            topics=["HDMI eARC", "Gaming Port"],
            sentiment="Satisfied",
            resolved=True
        )
        self.assertIsNotNone(ep)
        self.assertTrue(ep["episode_id"].startswith("EPS-"))

        episodes = get_customer_episodes("CUST-9921", limit=5)
        self.assertGreaterEqual(len(episodes), 1)

    def test_05_adk_care_tools(self):
        """Tests ADK tools: recall_customer_memory, save_customer_fact, get_cross_session_timeline."""
        recall_res = recall_customer_memory("CUST-7741")
        self.assertEqual(recall_res["status"], "success")
        self.assertEqual(recall_res["customer_name"], "David Kim")
        self.assertIn("BaristaPro Espresso Machine", str(recall_res["owned_devices"]))

        fact_res = save_customer_fact("CUST-7741", "Lives in high-altitude region requiring hotter boiler temp")
        self.assertEqual(fact_res["status"], "success")

        timeline_res = get_cross_session_timeline("CUST-7741")
        self.assertEqual(timeline_res["status"], "success")
        self.assertGreater(timeline_res["total_recorded_episodes"], 0)

    def test_06_session_consolidation(self):
        """Tests that active session turns distill properly into episodic memory."""
        messages = [
            {"role": "user", "text": "Hi, I have a problem with my TV error TV-NET-502 from order ORD-10021."},
            {"role": "assistant", "text": "I can help with error TV-NET-502. Thank you, the label has been generated."}
        ]
        state = {"active_ticket_id": "TCK-10021-VND", "customer_id": "CUST-9921"}

        result = consolidate_session_memory(
            session_id="test_consol_session",
            user_id="CUST-9921",
            messages=messages,
            session_state=state
        )
        self.assertEqual(result["status"], "consolidated")
        self.assertEqual(result["customer_id"], "CUST-9921")
        self.assertTrue(result["resolved"])

    def test_07_fastapi_memory_endpoints(self):
        """Tests REST API endpoints for customer profiles, notes, and episodes."""
        # GET /api/customer/profiles
        r1 = self.client.get("/api/customer/profiles")
        self.assertEqual(r1.status_code, 200)
        data1 = r1.json()
        self.assertGreaterEqual(data1["count"], 3)

        # GET /api/customer/profile
        r2 = self.client.get("/api/customer/profile?user_id=CUST-9921")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["profile"]["customer_name"], "Alex Mercer")

        # POST /api/customer/note
        r3 = self.client.post("/api/customer/note", json={
            "user_id": "CUST-9921",
            "note": "Verified 5GHz Wi-Fi band functions normally"
        })
        self.assertEqual(r3.status_code, 200)

        # GET /api/customer/episodes
        r4 = self.client.get("/api/customer/episodes?user_id=CUST-9921")
        self.assertEqual(r4.status_code, 200)
        data4 = r4.json()
        self.assertGreater(data4["count"], 0)

        # GET /api/stats/system includes memory engine
        r5 = self.client.get("/api/stats/system")
        self.assertEqual(r5.status_code, 200)
        self.assertIn("cross_session_memory_engine", r5.json())


if __name__ == "__main__":
    unittest.main()
