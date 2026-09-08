"""
Dynamic Few-Shot RAG Service for Post-Purchase Customer Care
Provides intelligent, context-sensitive retrieval of gold-standard human resolution
exemplars to guide multi-agent responses via in-context learning.

Features:
1. Hybrid Semantic Retrieval: Sublinear TF-IDF Cosine Similarity + BM25 Lexical Keyword Overlap
2. Dynamic In-Context Prompt Injection: Selectively enriches agent prompts when relevance threshold is met
3. Dual-Store Persistence: Primary in MongoDB `gold_exemplars`, resilient offline fallback in `.adk/gold_exemplars.json`
4. Precedent Management: CRUD capabilities to curate, inspect, and benchmark gold-standard human cases
"""

import os
import re
import json
import math
import uuid
import logging
from typing import Dict, List, Any, Optional, Tuple

try:
    from .db import (
        is_mongo_connected,
        get_exemplars_collection,
        serialize_doc,
        serialize_docs,
        SEED_EXEMPLARS
    )
except (ImportError, ValueError):
    from db import (
        is_mongo_connected,
        get_exemplars_collection,
        serialize_doc,
        serialize_docs,
        SEED_EXEMPLARS
    )

logger = logging.getLogger("customer_care.few_shot_rag")

EXEMPLARS_FILE_PATH = os.path.join(os.path.dirname(__file__), ".adk", "gold_exemplars.json")

_FALLBACK_SEED_EXEMPLARS: List[Dict[str, Any]] = list(SEED_EXEMPLARS)

STOP_WORDS = {
    "a", "about", "above", "after", "again", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "could", "did", "do", "does", "doing", "down", "during", "each",
    "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here",
    "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it",
    "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not",
    "now", "of", "off", "on", "once", "only", "or", "other", "our", "ours", "ourselves",
    "out", "over", "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will", "with",
    "you", "your", "yours", "yourself", "yourselves", "please", "hello", "hi", "help"
}


def _ensure_exemplars_fallback_file():
    """Ensures fallback JSON file exists in .adk directory for offline resilience."""
    os.makedirs(os.path.dirname(EXEMPLARS_FILE_PATH), exist_ok=True)
    if not os.path.exists(EXEMPLARS_FILE_PATH):
        try:
            with open(EXEMPLARS_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(_FALLBACK_SEED_EXEMPLARS, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to initialize exemplars fallback file: {e}")


def _load_fallback_exemplars() -> List[Dict[str, Any]]:
    """Loads gold exemplars from local fallback JSON file."""
    _ensure_exemplars_fallback_file()
    try:
        with open(EXEMPLARS_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception:
        pass
    return list(_FALLBACK_SEED_EXEMPLARS)


def _save_fallback_exemplars(exemplars: List[Dict[str, Any]]):
    """Saves gold exemplars to local fallback JSON file."""
    _ensure_exemplars_fallback_file()
    try:
        with open(EXEMPLARS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(exemplars, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to write to exemplars fallback file: {e}")


# -------------------------------------------------------------
# Data Retrieval & Persistence
# -------------------------------------------------------------

def list_all_exemplars(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches all curated exemplars from MongoDB or fallback store."""
    col = get_exemplars_collection()
    if col is not None:
        try:
            query = {}
            if category and category.lower() != "all":
                query["category"] = {"$regex": f"^{category}$", "$options": "i"}
            docs = list(col.find(query))
            if docs:
                return serialize_docs(docs)
        except Exception as e:
            logger.warning(f"MongoDB query failed for exemplars, falling back to JSON: {e}")

    # Offline fallback
    all_ex = _load_fallback_exemplars()
    if category and category.lower() != "all":
        return [ex for ex in all_ex if ex.get("category", "").lower() == category.lower()]
    return all_ex


def get_exemplar(exemplar_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single exemplar by ID."""
    col = get_exemplars_collection()
    if col is not None:
        try:
            doc = col.find_one({"exemplar_id": exemplar_id})
            if doc:
                return serialize_doc(doc)
        except Exception:
            pass

    for ex in _load_fallback_exemplars():
        if ex.get("exemplar_id") == exemplar_id:
            return ex
    return None


def add_curated_exemplar(
    title: str,
    category: str,
    situation: str,
    customer_inquiry: str,
    expert_thought: str,
    expert_response: str,
    policy_citation: str = "",
    tags: Optional[List[str]] = None,
    exemplar_id: Optional[str] = None
) -> Dict[str, Any]:
    """Adds or updates a gold-standard exemplar across MongoDB and offline fallback store."""
    if not exemplar_id:
        prefix = "EXEMP-" + "".join([w[:3].upper() for w in category.split()[:2]])
        exemplar_id = f"{prefix}-{uuid.uuid4().hex[:4].upper()}"

    doc = {
        "exemplar_id": exemplar_id,
        "title": title.strip(),
        "category": category.strip(),
        "situation": situation.strip(),
        "customer_inquiry": customer_inquiry.strip(),
        "expert_thought": expert_thought.strip(),
        "expert_response": expert_response.strip(),
        "policy_citation": policy_citation.strip() or "*Source: Standard Operating Procedures*",
        "tags": [t.strip().lower() for t in (tags or []) if t.strip()]
    }

    # Upsert in MongoDB
    col = get_exemplars_collection()
    if col is not None:
        try:
            col.update_one({"exemplar_id": exemplar_id}, {"$set": doc}, upsert=True)
        except Exception as e:
            logger.warning(f"Failed to upsert exemplar in MongoDB: {e}")

    # Upsert in Fallback JSON
    fallback_data = _load_fallback_exemplars()
    updated = False
    for i, ex in enumerate(fallback_data):
        if ex.get("exemplar_id") == exemplar_id:
            fallback_data[i] = doc
            updated = True
            break
    if not updated:
        fallback_data.append(doc)
    _save_fallback_exemplars(fallback_data)

    return doc


def delete_curated_exemplar(exemplar_id: str) -> bool:
    """Deletes an exemplar from both MongoDB and fallback store."""
    deleted = False
    col = get_exemplars_collection()
    if col is not None:
        try:
            res = col.delete_one({"exemplar_id": exemplar_id})
            if res.deleted_count > 0:
                deleted = True
        except Exception as e:
            logger.warning(f"Failed to delete exemplar from MongoDB: {e}")

    fallback_data = _load_fallback_exemplars()
    initial_len = len(fallback_data)
    fallback_data = [ex for ex in fallback_data if ex.get("exemplar_id") != exemplar_id]
    if len(fallback_data) < initial_len:
        deleted = True
        _save_fallback_exemplars(fallback_data)

    return deleted


# -------------------------------------------------------------
# NLP Tokenization & TF-IDF Vectorization
# -------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """Extracts normalized, alphanumeric terms filtering out common stop words."""
    if not text:
        return []
    raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
    clean_tokens = []
    for t in raw_tokens:
        clean = t.strip(".-_")
        if len(clean) >= 2 and clean not in STOP_WORDS:
            clean_tokens.append(clean)
            if "-" in clean:
                subparts = clean.split("-")
                for sp in subparts:
                    if len(sp) >= 2 and sp not in STOP_WORDS:
                        clean_tokens.append(sp)
    return clean_tokens


def _compute_document_text(exemplar: Dict[str, Any]) -> str:
    """Builds a weighted representation of an exemplar for vectorization."""
    title = (exemplar.get("title", "") + " ") * 2
    category = (exemplar.get("category", "") + " ") * 2
    situation = exemplar.get("situation", "") + " "
    inquiry = (exemplar.get("customer_inquiry", "") + " ") * 3
    tags = " ".join(exemplar.get("tags", [])) + " "
    tags_boosted = (tags + " ") * 3
    thought = exemplar.get("expert_thought", "")
    return f"{title} {category} {situation} {inquiry} {tags_boosted} {thought}"


def _build_tf_vector(tokens: List[str]) -> Dict[str, float]:
    """Computes sublinear term-frequency weights (1 + ln(count))."""
    counts: Dict[str, int] = {}
    for tok in tokens:
        counts[tok] = counts.get(tok, 0) + 1
    tf: Dict[str, float] = {}
    for tok, c in counts.items():
        tf[tok] = 1.0 + math.log(c)
    return tf


def _compute_cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Computes normalized cosine similarity between two sparse vector representations."""
    if not vec_a or not vec_b:
        return 0.0

    dot_product = 0.0
    for term, weight_a in vec_a.items():
        if term in vec_b:
            dot_product += weight_a * vec_b[term]

    norm_a = math.sqrt(sum(w * w for w in vec_a.values()))
    norm_b = math.sqrt(sum(w * w for w in vec_b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


# -------------------------------------------------------------
# Dynamic Semantic Retrieval Algorithm
# -------------------------------------------------------------

def retrieve_dynamic_exemplars(
    query: str,
    category: Optional[str] = "All",
    top_k: int = 2,
    min_relevance: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Retrieves the most semantically and contextually relevant gold-standard exemplars
    using a hybrid ranking model:
    - 60% Dense TF-IDF Cosine Similarity
    - 25% Sparse Keyword & Tag Overlap
    - 15% Exact Keyword/ID Presence Boost
    
    Args:
        query: Customer's current query or interaction text.
        category: Optional domain filter ("Returns & Warranty", "Product Diagnostics", etc.).
        top_k: Maximum number of exemplars to return (default 2).
        min_relevance: Cutoff threshold (0.0 - 1.0) to prevent injecting irrelevant exemplars.
    """
    exemplars = list_all_exemplars(category=category)
    if not exemplars:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # 1. Compute Corpus Document Frequencies for IDF
    corpus_size = len(exemplars)
    doc_freqs: Dict[str, int] = {}
    tokenized_docs: List[List[str]] = []

    for ex in exemplars:
        doc_str = _compute_document_text(ex)
        tokens = _tokenize(doc_str)
        tokenized_docs.append(tokens)
        unique_tokens = set(tokens)
        for u in unique_tokens:
            doc_freqs[u] = doc_freqs.get(u, 0) + 1

    # 2. Build Query TF-IDF Vector
    query_tf = _build_tf_vector(query_tokens)
    query_tfidf: Dict[str, float] = {}
    for term, tf_val in query_tf.items():
        df = doc_freqs.get(term, 0)
        idf = math.log(1.0 + (corpus_size - df + 0.5) / (df + 0.5)) + 1.0
        query_tfidf[term] = tf_val * idf

    # 3. Score Each Exemplar
    scored_exemplars: List[Tuple[float, Dict[str, Any]]] = []

    for i, ex in enumerate(exemplars):
        doc_tokens = tokenized_docs[i]
        doc_tf = _build_tf_vector(doc_tokens)
        doc_tfidf: Dict[str, float] = {}
        for term, tf_val in doc_tf.items():
            df = doc_freqs.get(term, 1)
            idf = math.log(1.0 + (corpus_size - df + 0.5) / (df + 0.5)) + 1.0
            doc_tfidf[term] = tf_val * idf

        # Dense TF-IDF Cosine
        cosine_sim = _compute_cosine_similarity(query_tfidf, doc_tfidf)

        # Sparse Keyword Coverage against tags & title
        ex_tags = [t.lower() for t in ex.get("tags", [])]
        ex_title_tokens = set(_tokenize(ex.get("title", "")))
        
        overlap_count = 0
        tag_match_count = 0
        for q_tok in set(query_tokens):
            if q_tok in ex_tags:
                tag_match_count += 1
            if q_tok in ex_title_tokens:
                overlap_count += 1
            elif any(q_tok in t for t in ex_tags):
                tag_match_count += 0.5

        keyword_coverage = min(1.0, (overlap_count * 0.25 + tag_match_count * 0.45))

        # Direct string presence check for critical identifiers
        q_lower = query.lower()
        exact_id_boost = 0.0
        for tag in ex_tags:
            if tag in q_lower and len(tag) >= 3:
                exact_id_boost += 0.15
        exact_id_boost = min(0.30, exact_id_boost)

        # Hybrid Score
        hybrid_score = (0.60 * cosine_sim) + (0.25 * keyword_coverage) + (0.15 * exact_id_boost)
        hybrid_score = round(min(1.0, hybrid_score), 4)

        if hybrid_score >= min_relevance:
            ex_copy = dict(ex)
            ex_copy["relevance_score"] = hybrid_score
            scored_exemplars.append((hybrid_score, ex_copy))

    # 4. Sort descending by relevance score
    scored_exemplars.sort(key=lambda x: x[0], reverse=True)

    results = [item[1] for item in scored_exemplars[:top_k]]
    return results


# -------------------------------------------------------------
# Dynamic Prompt Formatting for Gemini ADK Agent Runner
# -------------------------------------------------------------

def format_dynamic_few_shot_prompt(
    query: str,
    category: Optional[str] = "All",
    top_k: int = 2,
    min_relevance: float = 0.18
) -> Optional[str]:
    """
    Finds matching gold-standard exemplars for the incoming query and formats them
    into a structured in-context few-shot demonstration prompt.
    Returns None if no exemplars meet the relevance threshold.
    """
    exemplars = retrieve_dynamic_exemplars(
        query=query,
        category=category,
        top_k=top_k,
        min_relevance=min_relevance
    )

    if not exemplars:
        return None

    lines = [
        "=== GOLD-STANDARD RESOLUTION PRECEDENTS (DYNAMIC FEW-SHOT IN-CONTEXT GUIDANCE) ===",
        "The following verified human supervisor cases demonstrate the tone, accuracy, policy citations,",
        "and step-by-step diagnostic structure required for resolving this customer inquiry:\n"
    ]

    for idx, ex in enumerate(exemplars, 1):
        rel_percent = int(ex.get("relevance_score", 0.0) * 100)
        lines.append(f"--- [PRECEDENT #{idx}: {ex.get('title')} | Category: {ex.get('category')} (Relevance: {rel_percent}%)] ---")
        lines.append(f"• Situation: {ex.get('situation')}")
        lines.append(f"• Customer Inquiry: \"{ex.get('customer_inquiry')}\"")
        lines.append(f"• Expert Thought Process: {ex.get('expert_thought')}")
        lines.append(f"• Gold-Standard Agent Response:\n{ex.get('expert_response')}")
        if ex.get("policy_citation"):
            lines.append(f"• Official Policy Citation: {ex.get('policy_citation')}")
        lines.append("")

    lines.append("--- INSTRUCTION FOR CURRENT CASE ---")
    lines.append("Adopt the empathy, structured diagnostic clarity, and policy citation adherence")
    lines.append("demonstrated in the precedents above when resolving the customer's inquiry.")
    lines.append("================================================================================")

    return "\n".join(lines)
