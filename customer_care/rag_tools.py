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


try:
    from .db import (
        list_knowledge_chunks,
        insert_knowledge_chunk,
        delete_knowledge_chunk,
        list_faq_docs,
        insert_faq_doc,
        delete_faq_doc,
        is_mongo_connected
    )
except (ImportError, ValueError):
    from db import (
        list_knowledge_chunks,
        insert_knowledge_chunk,
        delete_knowledge_chunk,
        list_faq_docs,
        insert_faq_doc,
        delete_faq_doc,
        is_mongo_connected
    )


def index_customer_care_docs(docs_dir: Optional[str] = None) -> Dict[str, Any]:
    """Indexes 100% of product manuals, policy docs, and FAQs directly from MongoDB database."""
    global _INDEXED_CHUNKS, _DOC_METADATA
    _INDEXED_CHUNKS = []

    all_chunks = []
    chunk_counter = 1

    # Fetch 100% of knowledge documents directly from MongoDB database
    mongo_chunks = list_knowledge_chunks()
    
    for item in mongo_chunks:
        doc_id = item.get("doc_id", f"KNOW-DB-{chunk_counter:04d}")
        cat = item.get("category", "General Support")
        heading = item.get("heading", "General Information")
        content = item.get("content", "").strip()
        doc_title = item.get("doc_title", "MongoDB Knowledge Document")

        if heading and content:
            combined_text = f"{heading}\n{content}"
            all_chunks.append({
                "chunk_id": doc_id,
                "source": cat,
                "heading": heading,
                "text": combined_text,
                "storage_type": "mongodb",
                "category": cat,
                "tokens": _tokenize(combined_text)
            })
            chunk_counter += 1

    # Build vocabulary & TF-IDF dense vectors
    all_text = " ".join([c["text"] for c in all_chunks])
    vocab_words = sorted(list(set(_tokenize(all_text))))
    vocab = {word: idx for idx, word in enumerate(vocab_words)}

    for c in all_chunks:
        c["dense_vector"] = _compute_tf_idf_vector(c["text"], vocab)

    _INDEXED_CHUNKS = all_chunks
    _DOC_METADATA = {
        "vocab_map": vocab,
        "total_chunks": len(all_chunks),
        "documents": ["MongoDB Collection: knowledge_docs"],
        "mongodb_chunks_count": len(all_chunks)
    }

    return {
        "status": "success",
        "storage_mode": "100% MongoDB Database",
        "total_chunks": len(all_chunks),
        "mongodb_chunks_count": len(all_chunks)
    }


def _extract_key_sentences(query: str, text: str, max_sentences: int = 3) -> str:
    """Extracts top N query-relevant sentences from a text chunk using token overlap scoring."""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+|\n+', text) if s.strip()]
    if len(sentences) <= max_sentences:
        return text.strip()
    
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return " ".join(sentences[:max_sentences])
    
    scored_sentences = []
    for idx, s in enumerate(sentences):
        s_tokens = set(_tokenize(s))
        overlap = len(q_tokens.intersection(s_tokens))
        scored_sentences.append((overlap, -idx, s))
    
    scored_sentences.sort(key=lambda x: (x[0], x[1]), reverse=True)
    top_s = [item[2] for item in scored_sentences[:max_sentences]]
    
    ordered_top = [s for s in sentences if s in top_s]
    return " ".join(ordered_top)


def compress_retrieved_context(
    query: str,
    raw_results: List[Dict[str, Any]],
    min_score_threshold: float = 0.025,
    max_token_budget: int = 300
) -> Dict[str, Any]:
    """Applies relevance threshold pruning, sentence extraction, deduplication, and token budgeting."""
    filtered_results = [r for r in raw_results if r.get("relevance_score", 0) >= min_score_threshold]
    if not filtered_results:
        filtered_results = raw_results[:2]
    
    original_text = " ".join([r.get("content", r.get("answer", "")) for r in raw_results])
    original_tokens = len(_tokenize(original_text))
    
    compressed_items = []
    seen_texts = set()
    current_token_count = 0
    
    for item in filtered_results:
        content = item.get("content", item.get("answer", ""))
        extracted_content = _extract_key_sentences(query, content, max_sentences=3)
        
        if extracted_content in seen_texts:
            continue
        seen_texts.add(extracted_content)
        
        chunk_tokens = len(_tokenize(extracted_content))
        if current_token_count + chunk_tokens > max_token_budget and compressed_items:
            break
        
        item_copy = dict(item)
        item_copy["original_content"] = content
        item_copy["compressed_content"] = extracted_content
        item_copy["content"] = extracted_content
        compressed_items.append(item_copy)
        current_token_count += chunk_tokens
        
    reduced_text = " ".join([i["compressed_content"] for i in compressed_items])
    reduced_tokens = len(_tokenize(reduced_text))
    ratio = round((1.0 - (reduced_tokens / max(original_tokens, 1))) * 100, 1) if original_tokens > 0 else 0.0
    
    return {
        "status": "success",
        "original_tokens": original_tokens,
        "reduced_tokens": reduced_tokens,
        "tokens_saved": max(0, original_tokens - reduced_tokens),
        "compression_ratio_pct": ratio,
        "compressed_results": compressed_items
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
            "citation": f"*Source: {c['source']}*",
            "relevance_score": round(rrf_score, 4)
        })

    sorted_results = sorted(combined, key=lambda x: x["relevance_score"], reverse=True)
    top_results = sorted_results[:top_k]
    compression = compress_retrieved_context(query, top_results)

    return {
        "status": "success",
        "query": query,
        "retrieved_count": len(top_results),
        "results": compression["compressed_results"],
        "context_reduction": {
            "original_tokens": compression["original_tokens"],
            "reduced_tokens": compression["reduced_tokens"],
            "tokens_saved": compression["tokens_saved"],
            "compression_ratio_pct": compression["compression_ratio_pct"]
        }
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


def search_faq_knowledge_base(
    query: str,
    category: Optional[str] = None,
    top_k: int = 3
) -> Dict[str, Any]:
    """Searches store policy FAQs, shipping rules, return guidelines, warranty conditions, and account security.

    Args:
        query: Specific policy question (e.g., 'What is your return policy?', 'Do you ship internationally?').
        category: Optional category filter (e.g., 'Shipping', 'Returns', 'Warranty', 'Billing', 'Troubleshooting', 'Security').
        top_k: Number of relevant FAQ results to return.

    Returns:
        Dict containing top relevant Q&A matches with category, content, relevance score, and source citation.
    """
    global _INDEXED_CHUNKS
    if not _INDEXED_CHUNKS:
        index_customer_care_docs()

    res = search_product_guides(query=query, top_k=len(_INDEXED_CHUNKS) or 10)
    all_results = res.get("results", [])

    filtered = []
    for r in all_results:
        heading = r.get("section_heading", "").lower()
        content = r.get("content", "").lower()
        source = r.get("source_doc", "").lower()

        if category and category.lower() != "all":
            cat = category.lower()
            if cat not in heading and cat not in content and cat not in source:
                continue
        filtered.append(r)

    top_matches = filtered[:top_k]
    compression = compress_retrieved_context(query, top_matches)
    compressed_top = compression["compressed_results"]

    return {
        "status": "success",
        "query": query,
        "category_filter": category or "All",
        "match_count": len(compressed_top),
        "context_reduction": {
            "original_tokens": compression["original_tokens"],
            "reduced_tokens": compression["reduced_tokens"],
            "tokens_saved": compression["tokens_saved"],
            "compression_ratio_pct": compression["compression_ratio_pct"]
        },
        "faq_results": [
            {
                "topic": item["section_heading"],
                "source": item["source_doc"],
                "answer": item["content"],
                "citation": item["citation"],
                "relevance_score": item["relevance_score"]
            }
            for item in compressed_top
        ]
    }


def add_dynamic_faq(
    question: str,
    answer: str,
    category: str = "General Support"
) -> Dict[str, Any]:
    """Dynamically inserts a new FAQ into MongoDB database AND updates live RAG vector index.

    Args:
        question: Frequently asked question or title.
        answer: Detailed answer explanation or policy response.
        category: FAQ section category (e.g. 'Shipping', 'Returns', 'Promotions').

    Returns:
        Dict confirming database insertion and new RAG vector store metrics.
    """
    global _INDEXED_CHUNKS, _DOC_METADATA

    # 1. Insert 100% into MongoDB
    saved_doc = insert_faq_doc(question=question, answer=answer, category=category)

    # 2. Re-index live vector store from MongoDB
    index_customer_care_docs()

    return {
        "status": "success",
        "message": f"Successfully inserted FAQ '{question}' into MongoDB database (`knowledge_docs` collection).",
        "faq_id": saved_doc.get("faq_id"),
        "total_chunks": len(_INDEXED_CHUNKS)
    }


def delete_dynamic_faq(faq_id: str) -> Dict[str, Any]:
    """Deletes an FAQ entry from MongoDB database and re-indexes the RAG vector store."""
    success = delete_faq_doc(faq_id=faq_id)
    index_customer_care_docs()

    return {
        "status": "success" if success else "error",
        "message": f"FAQ '{faq_id}' deleted from MongoDB." if success else f"FAQ '{faq_id}' not found.",
        "total_chunks": len(_INDEXED_CHUNKS)
    }


def get_faq_summary_stats() -> Dict[str, Any]:
    """Returns 100% MongoDB RAG vector stats and indexed categories."""
    global _INDEXED_CHUNKS, _DOC_METADATA
    if not _INDEXED_CHUNKS:
        index_customer_care_docs()

    categories = set()
    for c in _INDEXED_CHUNKS:
        if c.get("category"):
            categories.add(c["category"])
        elif c.get("heading"):
            categories.add(c["heading"])

    return {
        "storage_engine": "100% MongoDB Database",
        "total_chunks": len(_INDEXED_CHUNKS),
        "total_documents": len(_DOC_METADATA.get("documents", [])),
        "mongodb_chunks_count": _DOC_METADATA.get("mongodb_chunks_count", len(_INDEXED_CHUNKS)),
        "documents": _DOC_METADATA.get("documents", []),
        "vocab_size": len(_DOC_METADATA.get("vocab_map", {})),
        "indexed_categories": sorted(list(categories))
    }



