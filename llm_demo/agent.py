"""
LLM Engineering & Studio Agent (llm_demo)
Master ADK Agent integrating LLM Fine-Tuning, Hyperparameter Scaling, and Hybrid RAG.
"""

import os
import asyncio
import warnings
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

# Ensure Google API Key is loaded

from google.adk.agents import Agent

# Import Fine-Tuning tools
try:
    from .finetuning_tools import (
        prepare_dataset,
        configure_peft,
        run_finetuning_job,
        evaluate_finetuned_model,
        list_finetuned_models
    )
except (ImportError, ValueError):
    from finetuning_tools import (
        prepare_dataset,
        configure_peft,
        run_finetuning_job,
        evaluate_finetuned_model,
        list_finetuned_models
    )

# Import Hyperparameter Scaling tools
try:
    from .hyperparameter_tools import (
        calculate_scaling_laws,
        simulate_lr_schedules,
        scale_batch_size,
        run_hyperparameter_sweep
    )
except (ImportError, ValueError):
    from hyperparameter_tools import (
        calculate_scaling_laws,
        simulate_lr_schedules,
        scale_batch_size,
        run_hyperparameter_sweep
    )

# Import RAG tools
try:
    from .rag_tools import (
        index_knowledge_base,
        search_rag_documents,
        generate_rag_response_with_citations,
        evaluate_rag_pipeline
    )
except (ImportError, ValueError):
    from rag_tools import (
        index_knowledge_base,
        search_rag_documents,
        generate_rag_response_with_citations,
        evaluate_rag_pipeline
    )

MODEL_NAME = os.environ.get("DEFAULT_MODEL", "gemini-3.1-flash-lite")

# Specialized Sub-Agents
finetuning_agent = Agent(
    name="finetuning_specialist",
    model=MODEL_NAME,
    description="Specialist in LLM dataset formatting, LoRA/PEFT parameter allocation, training jobs, and adapter evaluation.",
    instruction="""You are an expert AI Engineer specializing in LLM Fine-Tuning and Parameter-Efficient Adaptation (PEFT/LoRA/QLoRA).
Your role:
1. Help users curate, format, and validate instruction-tuning (SFT) datasets using `prepare_dataset`.
2. Configure LoRA/PEFT parameters (rank r, alpha, target modules, memory estimates) using `configure_peft`.
3. Launch simulated fine-tuning runs with loss tracking and checkpoint creation using `run_finetuning_job`.
4. Compare and evaluate base model vs adapter performance using `evaluate_finetuned_model`.
Always explain parameter trade-offs, VRAM savings, and convergence metrics clearly.""",
    tools=[
        prepare_dataset,
        configure_peft,
        run_finetuning_job,
        evaluate_finetuned_model,
        list_finetuned_models
    ]
)

hyperparameter_agent = Agent(
    name="hyperparameter_specialist",
    model=MODEL_NAME,
    description="Specialist in Chinchilla compute scaling laws, learning rate schedulers, distributed batch sizing, and Optuna sweeps.",
    instruction="""You are an expert ML Systems and Scaling Laws Engineer.
Your role:
1. Compute optimal compute, parameter (N), and token (D) distributions using `calculate_scaling_laws` (Chinchilla/Kaplan).
2. Recommend and simulate learning rate schedules (Cosine Annealing with Warmup, Linear Decay) using `simulate_lr_schedules`.
3. Calculate multi-GPU gradient accumulation and batch size scaling rules using `scale_batch_size`.
4. Run automated hyperparameter sweeps and find Pareto optimal configurations using `run_hyperparameter_sweep`.
Provide concrete FLOPs, GPU-hours, and mathematical formulas in your responses.""",
    tools=[
        calculate_scaling_laws,
        simulate_lr_schedules,
        scale_batch_size,
        run_hyperparameter_sweep
    ]
)

rag_agent = Agent(
    name="rag_specialist",
    model=MODEL_NAME,
    description="Specialist in Document Chunking, Dense & Sparse BM25 Hybrid Retrieval, Reciprocal Rank Fusion (RRF), and RAG Evaluation.",
    instruction="""You are a production RAG Architect.
Your role:
1. Index knowledge base documents with semantic/recursive chunking using `index_knowledge_base`.
2. Perform Hybrid Retrieval combining Dense Vector Embeddings and Sparse BM25 via Reciprocal Rank Fusion (RRF) using `search_rag_documents`.
3. Synthesize grounded responses with strict in-text citations using `generate_rag_response_with_citations`.
4. Audit retrieval quality and faithfulness using the RAG Triad via `evaluate_rag_pipeline`.
Always cite your sources and verify claims against retrieved passages.""",
    tools=[
        index_knowledge_base,
        search_rag_documents,
        generate_rag_response_with_citations,
        evaluate_rag_pipeline
    ]
)

# Root Coordinator Agent
COORDINATOR_INSTRUCTIONS = """
You are the Lead LLM Systems Architect and Studio Coordinator for the LLM Demo Suite.
You have access to a comprehensive suite of tools and specialist sub-agents spanning three critical LLM engineering pillars:

### 1. LLM Fine-Tuning & PEFT:
- Dataset generation and schema validation (`prepare_dataset`)
- LoRA/QLoRA parameter calculation and VRAM estimation (`configure_peft`)
- Fine-tuning execution with telemetry loss curves (`run_finetuning_job`)
- Model evaluation and Base vs Fine-tuned comparison (`evaluate_finetuned_model`)

### 2. Hyperparameter Scaling & Optimization:
- Chinchilla/Kaplan compute-optimal parameter & token allocations (`calculate_scaling_laws`)
- Learning rate warmup & cosine schedules (`simulate_lr_schedules`)
- Multi-GPU distributed batch sizing & gradient accumulation (`scale_batch_size`)
- Multi-objective Bayesian hyperparameter sweeps (`run_hyperparameter_sweep`)

### 3. Hybrid RAG (Retrieval-Augmented Generation):
- Document indexing and chunking strategies (`index_knowledge_base`)
- Hybrid Dense Vector + BM25 Sparse Search with Reciprocal Rank Fusion (`search_rag_documents`)
- Grounded citation generation (`generate_rag_response_with_citations`)
- RAG Triad metrics assessment: Faithfulness, Relevance, Context Precision (`evaluate_rag_pipeline`)

### Operational Guidelines:
- Coordinate tasks smoothly. You can call tools directly or delegate to your specialized sub-agents (`finetuning_specialist`, `hyperparameter_specialist`, `rag_specialist`).
- Format outputs with markdown tables, formulas, and structured code blocks.
- When answering questions from docs, always cite the retrieved sources.
"""

root_agent = Agent(
    name="llm_studio_coordinator",
    model=MODEL_NAME,
    description="Comprehensive AI Studio Agent for LLM Fine-Tuning, Hyperparameter Scaling, and Hybrid RAG.",
    instruction=COORDINATOR_INSTRUCTIONS,
    sub_agents=[
        finetuning_agent,
        hyperparameter_agent,
        rag_agent
    ],
    tools=[
        # Direct access to all core tools
        prepare_dataset,
        configure_peft,
        run_finetuning_job,
        evaluate_finetuned_model,
        list_finetuned_models,
        calculate_scaling_laws,
        simulate_lr_schedules,
        scale_batch_size,
        run_hyperparameter_sweep,
        index_knowledge_base,
        search_rag_documents,
        generate_rag_response_with_citations,
        evaluate_rag_pipeline
    ]
)
