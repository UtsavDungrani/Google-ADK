"""
Unit & Integration Test Suite for Dynamic Few-Shot RAG Service
Tests semantic retrieval, hybrid ranking, prompt formatting, CRUD, and FastAPI endpoints.
"""

import os
import unittest
from fastapi.testclient import TestClient

import few_shot_rag
from few_shot_rag import (
    retrieve_dynamic_exemplars,
    format_dynamic_few_shot_prompt,
    list_all_exemplars,
    get_exemplar,
    add_curated_exemplar,
    delete_curated_exemplar,
    _tokenize,
    _build_tf_vector,
    _compute_cosine_similarity
)
from server import app


class TestDynamicFewShotRAG(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_exemplars_store_has_seeds(self):
        """Ensures the repository contains the curated gold-standard exemplars."""
        exemplars = list_all_exemplars()
        self.assertGreaterEqual(len(exemplars), 6)
        ids = [ex.get("exemplar_id") for ex in exemplars]
        self.assertIn("EXEMP-RET-01", ids)
        self.assertIn("EXEMP-DIAG-01", ids)
        self.assertIn("EXEMP-ESC-01", ids)
        self.assertIn("EXEMP-CLM-01", ids)
        self.assertIn("EXEMP-HP-01", ids)
        self.assertIn("EXEMP-ESP-01", ids)

    def test_tokenization_and_vectorization(self):
        """Tests that text preprocessing cleans stop words and splits hyphens."""
        tokens = _tokenize("My UltraHD TV shows error TV-NET-502 on Wi-Fi mesh!")
        self.assertIn("tv-net-502", tokens)
        self.assertIn("mesh", tokens)
        self.assertIn("ultrahd", tokens)
        self.assertNotIn("on", tokens)
        self.assertNotIn("my", tokens)

        tf = _build_tf_vector(tokens)
        self.assertIn("tv-net-502", tf)
        self.assertGreater(tf["tv-net-502"], 0.0)

        # Cosine similarity between identical vectors should be ~1.0
        cos_sim = _compute_cosine_similarity(tf, tf)
        self.assertAlmostEqual(cos_sim, 1.0, places=4)

    def test_semantic_retrieval_returns_exception(self):
        """Querying about hospital stay and missed 30-day return should match Return Grace Exception."""
        query = "I was hospitalized for surgery and missed the 30-day return deadline. Can I still return my TV?"
        results = retrieve_dynamic_exemplars(query=query, top_k=2, min_relevance=0.15)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertEqual(top["exemplar_id"], "EXEMP-RET-01")
        self.assertIn("Grace", top["title"])
        self.assertGreater(top["relevance_score"], 0.25)

    def test_semantic_retrieval_error_502(self):
        """Querying about TV error TV-NET-502 should retrieve Wi-Fi Mesh Diagnostics."""
        query = "My TV is dropping off Wi-Fi and gives error TV-NET-502"
        results = retrieve_dynamic_exemplars(query=query, top_k=2, min_relevance=0.15)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertEqual(top["exemplar_id"], "EXEMP-DIAG-01")
        self.assertIn("502", top["title"])

    def test_semantic_retrieval_bluetooth_multipoint(self):
        """Querying about connecting headphones to MacBook and phone should match Multipoint exemplar."""
        query = "How do I pair my ProSound headphones with both my iPhone and MacBook laptop at once?"
        results = retrieve_dynamic_exemplars(query=query, top_k=2, min_relevance=0.15)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertEqual(top["exemplar_id"], "EXEMP-HP-01")
        self.assertIn("Multipoint", top["title"])

    def test_semantic_retrieval_espresso_descaling(self):
        """Querying about orange blinking light on espresso machine should match Descaling exemplar."""
        query = "The orange light is flashing on my BaristaPro coffee machine and pressure dropped"
        results = retrieve_dynamic_exemplars(query=query, top_k=2, min_relevance=0.15)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertEqual(top["exemplar_id"], "EXEMP-ESP-01")
        self.assertIn("Descaling", top["title"])

    def test_dynamic_prompt_formatter(self):
        """Ensures format_dynamic_few_shot_prompt generates properly structured in-context prompt."""
        query = "I have horizontal lines on my TV screen. Is it replaced under warranty?"
        prompt = format_dynamic_few_shot_prompt(query=query, top_k=1, min_relevance=0.15)
        self.assertIsNotNone(prompt)
        self.assertIn("=== GOLD-STANDARD RESOLUTION PRECEDENTS", prompt)
        self.assertIn("CLM-TV-98214", prompt)
        self.assertIn("Official Policy Citation", prompt)
        self.assertIn("INSTRUCTION FOR CURRENT CASE", prompt)

        # Unrelated query should yield None if threshold not met
        random_query = "xyz 9898 zzz"
        no_prompt = format_dynamic_few_shot_prompt(query=random_query, min_relevance=0.30)
        self.assertIsNone(no_prompt)

    def test_crud_curated_exemplar(self):
        """Tests adding, fetching, and deleting a custom exemplar."""
        test_id = "EXEMP-TEST-9999"
        created = add_curated_exemplar(
            title="Smart Thermostat Firmware Recovery",
            category="Product Diagnostics",
            situation="Thermostat screen frozen on loading logo during OTA update.",
            customer_inquiry="My Smart Thermostat screen is stuck on the boot logo after firmware update.",
            expert_thought="Frozen boot cycle requires hard capacitor drain followed by USB emergency recovery.",
            expert_response="Please unplug the faceplate for 2 minutes...",
            policy_citation="*Source: Thermostat Technical Manual*",
            tags=["thermostat", "frozen", "boot", "firmware", "screen"],
            exemplar_id=test_id
        )
        self.assertEqual(created["exemplar_id"], test_id)

        # Fetch
        fetched = get_exemplar(test_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["title"], "Smart Thermostat Firmware Recovery")

        # Delete
        deleted = delete_curated_exemplar(test_id)
        self.assertTrue(deleted)
        self.assertIsNone(get_exemplar(test_id))

    def test_fastapi_few_shot_endpoints(self):
        """Tests the REST API endpoints in server.py."""
        # 1. GET /api/few-shot/exemplars
        resp = self.client.get("/api/few-shot/exemplars")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["count"], 6)

        # 2. GET /api/few-shot/search
        resp = self.client.get("/api/few-shot/search?query=error TV-NET-502 Wi-Fi")
        self.assertEqual(resp.status_code, 200)
        search_data = resp.json()
        self.assertEqual(search_data["status"], "success")
        self.assertGreaterEqual(len(search_data["matches"]), 1)
        self.assertIsNotNone(search_data["prompt_preview"])

        # 3. GET /api/stats/system includes few-shot stats
        resp = self.client.get("/api/stats/system")
        self.assertEqual(resp.status_code, 200)
        stats = resp.json()
        self.assertIn("few_shot_rag_engine", stats)
        self.assertIn("curated_gold_exemplars", stats)
        self.assertGreaterEqual(stats["curated_gold_exemplars"], 6)


if __name__ == "__main__":
    unittest.main()
