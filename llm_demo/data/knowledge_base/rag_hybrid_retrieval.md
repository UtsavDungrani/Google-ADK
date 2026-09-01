# Production RAG: Chunking, Hybrid Vector-BM25 Search, and Evaluation

## 1. Advanced Document Chunking Strategies
Retrieval quality depends critically on how text is partitioned:
1. **Fixed-Size Chunking with Overlap**:
   - Chunks text into fixed token windows (e.g. 512 tokens with 10% overlap).
   - Fast, but may split sentences or thematic concepts across boundaries.
2. **Recursive Character Splitting**:
   - Splits hierarchically by paragraph (`\n\n`), sentence (`\n`, `. `), and word space (` `).
   - Keeps logical paragraphs cohesive.
3. **Semantic Chunking**:
   - Analyzes embedding distance between consecutive sentences and places chunk boundaries where cosine similarity drops significantly.

---

## 2. Hybrid Retrieval with Reciprocal Rank Fusion (RRF)
Vector search alone struggles with exact keyword matching (part numbers, error codes like `ERR_PAY_402`, acronyms), while BM25 keyword search struggles with synonyms and conceptual intent.

### Reciprocal Rank Fusion (RRF):
$$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
where $M = \{\text{Dense Vector Search}, \text{Sparse BM25 Search}\}$, $r_m(d)$ is the rank of document $d$ in retrieval method $m$, and $k$ is a smoothing constant (typically $k=60$).
- Guarantees balanced weight between semantic understanding and exact keyword hits.

---

## 3. Cross-Encoder Re-Ranking
Bi-encoder vector search produces embeddings independently for query and document. Re-ranking applies a Cross-Encoder (e.g. `bge-reranker-large` or `cohere-rerank`) to score query-document token interactions jointly, boosting Top-1 accuracy by 15-25%.

---

## 4. The RAG Triad Evaluation Metrics
1. **Faithfulness**: Are all claims in the generated response strictly grounded in the retrieved context? (Prevents hallucinations).
2. **Answer Relevance**: Does the generated response directly answer the user query?
3. **Context Recall & Precision**: Did the retriever fetch the exact relevant passages needed to construct the complete answer?
