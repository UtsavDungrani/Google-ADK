"""
Unit & Integration Test Suite for Multilingual NLP & Cross-Lingual RAG Engine
Tests Language Identification (LID), Script Detection, Hinglish Code-Mixing,
mNER Entity Shielding, Cross-Lingual Query Alignment (CLIR), and FastAPI endpoints.
"""

import unittest
from fastapi.testclient import TestClient

import multilingual_nlp as nlp
import few_shot_rag
from server import app


class TestMultilingualNLP(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_language_identification_languages(self):
        """Tests fast sub-millisecond language and script identification across supported languages."""
        # 1. Spanish
        es_res = nlp.detect_language("¿Cómo puedo devolver mi televisor si estuve en el hospital?")
        self.assertEqual(es_res["language"], "es")
        self.assertEqual(es_res["name"], "Spanish")
        self.assertEqual(es_res["script"], "Latin")

        # 2. Hindi (Devanagari)
        hi_res = nlp.detect_language("मेरे 65 इंच टीवी पर एरर कोड TV-NET-502 आ रहा है")
        self.assertEqual(hi_res["language"], "hi")
        self.assertEqual(hi_res["name"], "Hindi")
        self.assertEqual(hi_res["script"], "Devanagari")

        # 3. German
        de_res = nlp.detect_language("Mein Fernseher hat schwarze horizontale Linien auf dem Bildschirm")
        self.assertEqual(de_res["language"], "de")
        self.assertEqual(de_res["name"], "German")

        # 4. French
        fr_res = nlp.detect_language("Bonjour, mon colis a du retard et je voudrais un remboursement")
        self.assertEqual(fr_res["language"], "fr")
        self.assertEqual(fr_res["name"], "French")

        # 5. Japanese
        ja_res = nlp.detect_language("ヘッドホンをMacBookとiPhoneに同時に接続する方法を教えてください")
        self.assertEqual(ja_res["language"], "ja")
        self.assertEqual(ja_res["name"], "Japanese")

        # 6. English
        en_res = nlp.detect_language("Where is my order ORD-10021 and when will it arrive?")
        self.assertEqual(en_res["language"], "en")
        self.assertEqual(en_res["name"], "English")

    def test_02_hinglish_code_mixing(self):
        """Tests that Latin-scripted Hindi mixed with English is classified as Hinglish code-mixed."""
        hinglish_query = "Mera order ORD-10023 delay ho gaya hai, delivery status track kardo please"
        res = nlp.detect_language(hinglish_query)
        self.assertTrue(res["is_code_mixed"])
        self.assertIn(res["language"], ["hinglish", "hi-Latn"])

    def test_03_mner_entity_shielding(self):
        """Tests that mNER shields critical IDs and serial numbers so translations do not mutate them."""
        raw_text = "Tengo problemas con el pedido ORD-10021 y el error TV-NET-502 en mi reclamo CLM-TV-98214"
        shielded, slot_map = nlp.shield_entities(raw_text)

        # Ensure raw IDs are replaced by slots
        self.assertNotIn("ORD-10021", shielded)
        self.assertNotIn("TV-NET-502", shielded)
        self.assertNotIn("CLM-TV-98214", shielded)
        self.assertIn("__ORDER_ID_", shielded)
        self.assertIn("__ERROR_CODE_", shielded)
        self.assertIn("__CLAIM_ID_", shielded)

        # Ensure unshielding restores exact original values
        restored = nlp.unshield_entities(shielded, slot_map)
        self.assertEqual(restored, raw_text)

    def test_04_cross_lingual_query_alignment(self):
        """Tests cross-lingual query alignment transforms foreign symptoms into English search concepts."""
        # Spanish TV error
        align_es = nlp.align_cross_lingual_query("Mi televisor tiene error TV-NET-502 y se desconecta del wifi")
        self.assertFalse(align_es["is_english"])
        self.assertEqual(align_es["source_language"], "es")
        self.assertIn("tv-net-502", align_es["aligned_english_query"].lower())
        self.assertIn("mesh", align_es["aligned_english_query"].lower())

        # Hindi Espresso Descaling
        align_hi = nlp.align_cross_lingual_query("कॉफी मशीन की ऑरेंज लाइट चमक रही है और प्रेशर कम हो गया")
        self.assertFalse(align_hi["is_english"])
        self.assertEqual(align_hi["source_language"], "hi")
        self.assertIn("espresso", align_hi["aligned_english_query"].lower())
        self.assertIn("descaling", align_hi["aligned_english_query"].lower())

    def test_05_cross_lingual_exemplar_retrieval(self):
        """Tests that Spanish and Hindi queries retrieve English gold-standard precedents via CLIR."""
        # Spanish query retrieves Error TV-NET-502 precedent
        align_es = nlp.align_cross_lingual_query("Mi televisor tiene error TV-NET-502 en la red wifi")
        matches = few_shot_rag.retrieve_dynamic_exemplars(align_es["aligned_english_query"], top_k=1)
        self.assertGreaterEqual(len(matches), 1)
        self.assertEqual(matches[0]["exemplar_id"], "EXEMP-DIAG-01")

        # Hindi query retrieves Espresso Descaling precedent
        align_hi = nlp.align_cross_lingual_query("कॉफी मशीन की ऑरेंज लाइट चमक रही है और प्रेशर कम हो गया")
        matches_hi = few_shot_rag.retrieve_dynamic_exemplars(align_hi["aligned_english_query"], top_k=1)
        self.assertGreaterEqual(len(matches_hi), 1)
        self.assertEqual(matches_hi[0]["exemplar_id"], "EXEMP-ESP-01")

    def test_06_cultural_pragmatics_politeness(self):
        """Tests that pragmatic politeness directives contain correct honorific guidelines."""
        # Spanish: Usted
        es_directive = nlp.get_pragmatic_politeness_directive("es")
        self.assertIn("Usted", es_directive)

        # German: Sie
        de_directive = nlp.get_pragmatic_politeness_directive("de")
        self.assertIn("Sie", de_directive)

        # Hindi: Aap
        hi_directive = nlp.get_pragmatic_politeness_directive("hi")
        self.assertIn("आप", hi_directive)

        # Japanese: Keigo
        ja_directive = nlp.get_pragmatic_politeness_directive("ja")
        self.assertIn("丁寧語", ja_directive)

    def test_07_fastapi_multilingual_endpoints(self):
        """Tests the Multilingual NLP REST API endpoints in server.py."""
        # 1. POST /api/nlp/detect-language
        resp = self.client.post("/api/nlp/detect-language", json={
            "text": "Mi televisor se apaga solo y tiene líneas horizontales"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["analysis"]["language"], "es")
        self.assertIn("Usted", data["politeness_directive"])

        # 2. POST /api/nlp/cross-lingual-search
        resp = self.client.post("/api/nlp/cross-lingual-search", json={
            "query": "auriculares bluetooth multipunto dos dispositivos"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["matches_count"], 1)
        self.assertEqual(data["exemplars"][0]["exemplar_id"], "EXEMP-HP-01")

        # 3. GET /api/nlp/supported-languages
        resp = self.client.get("/api/nlp/supported-languages")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("es", data["languages"])
        self.assertIn("hi", data["languages"])
        self.assertIn("hinglish", data["languages"])


if __name__ == "__main__":
    unittest.main()
