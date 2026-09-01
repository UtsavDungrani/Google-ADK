"""
RAG & Diagnostic Knowledge Base Tools for Customer Care
Provides hybrid dense-sparse retrieval (RRF) across product user manuals,
diagnostic troubleshooting guides, and warranty/return policies.
"""

import os
import re
import math
from typing import Dict, List, Any, Optional

_INDEXED_CHUNKS: List[Dict[str, Any]] = []
_DOC_METADATA: Dict[str, Any] = {}


def _tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def _compute_tf_idf_vector(text: str, vocab: Dict[str, int]) -> List[float]:
    """Computes a normalized term-frequency vector."""
    tokens = _tokenize(text)
    tf: Dict[str, float] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1.0
    
    vec = [0.0] * len(vocab)
    for word, idx in vocab.items():
        if word in tf:
            vec[idx] = tf[word] / max(1, len(tokens))
    
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two unit vectors."""
    return sum(a * b for a, b in zip(vec1, vec2))


def index_customer_care_docs(docs_dir: Optional[str] = None) -> Dict[str, Any]:
    """Indexes all customer care product manuals and policy markdown documents."""
    global _INDEXED_CHUNKS, _DOC_METADATA
    _INDEXED_CHUNKS = []

    target_dir = docs_dir or os.path.join(os.path.dirname(__file__), "docs")
    if not os.path.exists(target_dir):
        return {"status": "error", "message": f"Directory '{target_dir}' does not exist."}

    doc_files = [f for f in os.listdir(target_dir) if f.endswith(".md") or f.endswith(".txt")]
    all_chunks = []
    chunk_counter = 1

    for filename in doc_files:
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        sections = re.split(r"(^##+\s+.+$)", content, flags=re.MULTILINE)
        current_heading = "General Overview"
        
        for part in sections:
            if part.startswith("#"):
                current_heading = part.strip("# ").strip()
            elif part.strip():
                text = part.strip()
                all_chunks.append({
                    "chunk_id": f"CARE_CHK_{chunk_counter:04d}",
                    "source": filename,
                    "heading": current_heading,
                    "text": text,
                    "tokens": _tokenize(text)
                })
                chunk_counter += 1

    # Build vocabulary
    all_text = " ".join([c["text"] for c in all_chunks])
    vocab_words = sorted(list(set(_tokenize(all_text))))
    vocab = {word: idx for idx, word in enumerate(vocab_words)}

    for c in all_chunks:
        c["dense_vector"] = _compute_tf_idf_vector(c["text"], vocab)

    _INDEXED_CHUNKS = all_chunks
    _DOC_METADATA = {
        "vocab_map": vocab,
        "total_chunks": len(all_chunks),
        "documents": doc_files
    }

    return {
        "status": "success",
        "total_documents": len(doc_files),
        "total_chunks": len(all_chunks),
        "documents": doc_files
    }


def search_product_guides(
    query: str,
    top_k: int = 2,
    retrieval_mode: str = "hybrid_rrf"
) -> Dict[str, Any]:
    """Retrieves product troubleshooting steps, error codes, and setup instructions from official manuals.

    Args:
        query: Problem description, error code (e.g. 'TV-NET-502', 'flashing orange light'), or product question.
        top_k: Number of relevant manual passages to return.
        retrieval_mode: 'hybrid_rrf', 'dense_vector', or 'sparse_bm25'.

    Returns:
        Dict with ranked diagnostic instructions and source citations.
    """
    global _INDEXED_CHUNKS, _DOC_METADATA
    if not _INDEXED_CHUNKS:
        index_customer_care_docs()

    if not _INDEXED_CHUNKS:
        return {"status": "error", "message": "Knowledge base index is empty."}

    vocab = _DOC_METADATA.get("vocab_map", {})
    query_vec = _compute_tf_idf_vector(query, vocab)
    query_tokens = _tokenize(query)

    # 1. Dense Scoring
    dense_scores = []
    for idx, c in enumerate(_INDEXED_CHUNKS):
        sim = _cosine_similarity(query_vec, c.get("dense_vector", []))
        dense_scores.append((idx, sim))
    dense_ranked = sorted(dense_scores, key=lambda x: x[1], reverse=True)

    # 2. BM25 Sparse Scoring
    sparse_scores = []
    avg_len = sum(len(c["tokens"]) for c in _INDEXED_CHUNKS) / max(1, len(_INDEXED_CHUNKS))
    k1, b = 1.5, 0.75

    for idx, c in enumerate(_INDEXED_CHUNKS):
        doc_tokens = c["tokens"]
        doc_len = len(doc_tokens)
        score = 0.0
        for qt in query_tokens:
            count = doc_tokens.count(qt)
            if count > 0:
                docs_with_t = sum(1 for chk in _INDEXED_CHUNKS if qt in chk["tokens"])
                idf = math.log((len(_INDEXED_CHUNKS) - docs_with_t + 0.5) / (docs_with_t + 0.5) + 1.0)
                tf_norm = (count * (k1 + 1)) / (count + k1 * (1 - b + b * (doc_len / avg_len)))
                score += idf * tf_norm
        sparse_scores.append((idx, score))
    sparse_ranked = sorted(sparse_scores, key=lambda x: x[1], reverse=True)

    # 3. Reciprocal Rank Fusion (RRF)
    rrf_k = 60
    dense_rank_dict = {doc_idx: rank for rank, (doc_idx, _) in enumerate(dense_ranked)}
    sparse_rank_dict = {doc_idx: rank for rank, (doc_idx, _) in enumerate(sparse_ranked)}

    combined = []
    for idx, c in enumerate(_INDEXED_CHUNKS):
        d_rank = dense_rank_dict.get(idx, 999)
        s_rank = sparse_rank_dict.get(idx, 999)
        rrf_score = (1.0 / (rrf_k + d_rank + 1)) + (1.0 / (rrf_k + s_rank + 1))
        
        combined.append({
            "chunk_id": c["chunk_id"],
            "source_doc": c["source"],
            "section_heading": c["heading"],
            "content": c["text"],
            "citation": f"*Source: docs/{c['source']} ({c['heading']})*",
            "relevance_score": round(rrf_score, 4)
        })

    sorted_results = sorted(combined, key=lambda x: x["relevance_score"], reverse=True)
    top_results = sorted_results[:top_k]

    return {
        "status": "success",
        "query": query,
        "retrieved_count": len(top_results),
        "results": top_results
    }


def troubleshoot_product_issue(
    product_name: str,
    issue_description: str
) -> Dict[str, Any]:
    """Synthesizes step-by-step diagnostic resolution and troubleshooting guide from official manuals.

    Args:
        product_name: Name or category of product (e.g. 'Smart TV', 'Wireless Headphones', 'Espresso Machine').
        issue_description: Specific error code, symptom, or malfunction.

    Returns:
        Dict with troubleshooting steps, citations, and resolution recommendations.
    """
    search_query = f"{product_name} {issue_description}"
    search_res = search_product_guides(query=search_query, top_k=2)
    results = search_res.get("results", [])

    if not results:
        return {
            "status": "warning",
            "message": f"No specific manual entries found for '{search_query}'. Please verify model name."
        }

    top_chunk = results[0]
    return {
        "status": "success",
        "product_name": product_name,
        "issue_detected": issue_description,
        "primary_source": top_chunk["citation"],
        "recommended_steps": top_chunk["content"],
        "all_citations": [r["citation"] for r in results]
    }
