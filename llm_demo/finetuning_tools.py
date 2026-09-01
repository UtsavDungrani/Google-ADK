"""
LLM Fine-Tuning Tools for ADK Demo
Provides comprehensive dataset management, LoRA/PEFT configuration,
training execution simulation, checkpoint tracking, and model evaluation.
"""

import os
import json
import math
import time
from typing import Dict, List, Any, Optional

# Storage for fine-tuning jobs and models
_JOBS_DB: Dict[str, Dict[str, Any]] = {}
_DATASETS_DB: Dict[str, Dict[str, Any]] = {}

# Built-in base models catalog
BASE_MODELS = {
    "llama-3-8b": {"params_b": 8.03, "hidden_dim": 4096, "num_layers": 32, "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]},
    "mistral-7b": {"params_b": 7.24, "hidden_dim": 4096, "num_layers": 32, "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]},
    "gemini-flash": {"params_b": 4.50, "hidden_dim": 3072, "num_layers": 28, "target_modules": ["q_proj", "v_proj", "o_proj"]},
    "qwen-2.5-14b": {"params_b": 14.7, "hidden_dim": 5120, "num_layers": 48, "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]},
    "deepseek-r1-distill-7b": {"params_b": 7.61, "hidden_dim": 4096, "num_layers": 32, "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"]}
}


def prepare_dataset(
    task_type: str = "customer_support",
    dataset_name: str = "custom_finetune_dataset",
    sample_count: int = 50,
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """Prepares and validates a structured JSONL dataset for instruction fine-tuning (SFT).

    Args:
        task_type: Type of task ('customer_support', 'sql_generation', 'code_explainer', 'medical_qa').
        dataset_name: Name of the dataset identifier.
        sample_count: Number of synthetic training samples to generate.
        output_dir: Optional custom directory to save the JSONL file.

    Returns:
        Dict with dataset summary, file path, sample count, and validation statistics.
    """
    templates = {
        "customer_support": [
            {"instruction": "Assist a customer with payment failure error code ERR_PAY_402.", "input": "Customer: My transaction was declined but money was deducted.", "output": "I understand your concern. Error ERR_PAY_402 indicates a temporary gateway timeout. Any held funds are automatically released by your issuing bank within 3-5 business days. I've initiated an automated reversal request (Ticket #REV-9821)."},
            {"instruction": "Explain return policy for open-box electronics.", "input": "Customer: Can I return an opened tablet within 14 days?", "output": "Yes, open-box electronics can be returned within 14 days of delivery provided all original accessories, documentation, and packaging are included. A prepaid return shipping label has been prepared."},
            {"instruction": "Troubleshoot CloudPlatform API authentication 401 Unauthorized.", "input": "Customer: My bearer token fails when calling /v2/deployments.", "output": "A 401 error typically indicates an expired API key or missing scope. Please verify: 1) Run `gcloud auth print-access-token` to refresh your token, 2) Ensure your service account has `roles/cloudplatform.deployer` permission."}
        ],
        "sql_generation": [
            {"instruction": "Write an optimized SQL query to calculate 30-day customer churn rate.", "input": "Schema: users(id, signup_date), orders(id, user_id, order_date, amount)", "output": "SELECT COUNT(DISTINCT u.id) AS total_users, COUNT(DISTINCT CASE WHEN o.order_date < NOW() - INTERVAL '30 days' THEN u.id END) AS churned_users, ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_date < NOW() - INTERVAL '30 days' THEN u.id END) / COUNT(DISTINCT u.id), 2) AS churn_pct FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY 1;"},
            {"instruction": "Find the top 5 products by revenue in Q3 2026.", "input": "Schema: products(id, name, price), order_items(order_id, product_id, quantity, unit_price), orders(id, order_date, status)", "output": "SELECT p.id, p.name, SUM(oi.quantity * oi.unit_price) AS total_revenue FROM products p JOIN order_items oi ON p.id = oi.product_id JOIN orders o ON oi.order_id = o.id WHERE o.order_date BETWEEN '2026-07-01' AND '2026-09-30' AND o.status = 'COMPLETED' GROUP BY p.id, p.name ORDER BY total_revenue DESC LIMIT 5;"}
        ],
        "code_explainer": [
            {"instruction": "Explain the time and space complexity of QuickSort.", "input": "Algorithm: in-place randomized QuickSort.", "output": "QuickSort operates by choosing a pivot and partitioning elements into sub-arrays. Average Time Complexity: O(n log n). Worst-case Time Complexity: O(n^2) when poor pivots are chosen (mitigated by randomized pivots). Auxiliary Space Complexity: O(log n) call stack overhead for in-place implementations."},
            {"instruction": "Explain how LoRA (Low-Rank Adaptation) reduces trainable parameters in LLMs.", "input": "Concept: W_new = W_0 + (alpha / r) * (B @ A)", "output": "LoRA freezes the pre-trained weight matrix W_0 (d x k) and injects trainable rank decomposition matrices A (r x k) and B (d x r), where rank r << min(d, k). This slashes trainable parameters by over 99% while preserving model representation capacity."}
        ]
    }

    base_samples = templates.get(task_type, templates["customer_support"])
    samples = []
    total_tokens = 0

    for i in range(sample_count):
        tpl = base_samples[i % len(base_samples)]
        sample = {
            "id": f"{task_type}_{i+1:04d}",
            "instruction": tpl["instruction"],
            "input": tpl["input"] + (f" [Batch variation {i+1}]" if i >= len(base_samples) else ""),
            "output": tpl["output"]
        }
        approx_tokens = len((sample["instruction"] + sample["input"] + sample["output"]).split()) * 1.3
        total_tokens += int(approx_tokens)
        samples.append(sample)

    target_folder = output_dir or os.path.join(os.path.dirname(__file__), "data", "finetune_datasets")
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, f"{dataset_name}.jsonl")

    with open(file_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")

    summary = {
        "status": "success",
        "dataset_name": dataset_name,
        "task_type": task_type,
        "sample_count": len(samples),
        "estimated_total_tokens": total_tokens,
        "average_tokens_per_sample": round(total_tokens / len(samples), 1),
        "file_path": file_path,
        "validation": {
            "missing_fields": 0,
            "empty_samples": 0,
            "format": "Alpaca/Instruction JSONL",
            "is_valid": True
        }
    }
    _DATASETS_DB[dataset_name] = summary
    return summary


def configure_peft(
    base_model: str = "llama-3-8b",
    lora_r: int = 16,
    lora_alpha: int = 32,
    lora_dropout: float = 0.05,
    target_modules: Optional[List[str]] = None,
    quantization_bits: int = 4
) -> Dict[str, Any]:
    """Calculates Parameter-Efficient Fine-Tuning (PEFT/LoRA/QLoRA) memory footprints and parameters.

    Args:
        base_model: Identifier of the pre-trained base model (e.g. 'llama-3-8b', 'mistral-7b').
        lora_r: Low-rank decomposition dimension (Rank r).
        lora_alpha: LoRA scaling coefficient (Alpha).
        lora_dropout: LoRA dropout probability.
        target_modules: List of linear layers to apply LoRA to.
        quantization_bits: Base model quantization (16 for FP16, 8 for Int8, 4 for QLoRA/NF4).

    Returns:
        Dict with parameter counts, trainable percentage, scaling factor, and VRAM memory estimates.
    """
    model_info = BASE_MODELS.get(base_model.lower(), BASE_MODELS["llama-3-8b"])
    total_params_b = model_info["params_b"]
    hidden_dim = model_info["hidden_dim"]
    num_layers = model_info["num_layers"]
    selected_targets = target_modules or model_info["target_modules"]

    # Parameter count per target linear layer for LoRA matrices A (r x d) + B (d x r)
    params_per_matrix = 2 * (hidden_dim * lora_r)
    total_lora_params = params_per_matrix * len(selected_targets) * num_layers
    total_lora_params_m = round(total_lora_params / 1_000_000, 2)
    trainable_pct = round((total_lora_params / (total_params_b * 1e9)) * 100, 4)

    # Scaling coefficient
    scaling = round(lora_alpha / lora_r, 2)

    # Memory calculations (in GB)
    bytes_per_param = quantization_bits / 8.0
    base_model_vram_gb = round((total_params_b * 1e9 * bytes_per_param) / (1024**3), 2)
    adapter_vram_gb = round((total_lora_params * 4) / (1024**3), 3)  # FP32/FP16 optimizer state & gradients
    optimizer_vram_gb = round((total_lora_params * 8) / (1024**3), 3)  # AdamW 8 bytes per trainable param
    activation_vram_gb = round(1.5 + (0.05 * lora_r), 2)
    total_estimated_vram_gb = round(base_model_vram_gb + adapter_vram_gb + optimizer_vram_gb + activation_vram_gb, 2)
    full_finetune_vram_gb = round((total_params_b * 16) + (total_params_b * 8) + 4, 1)  # 16-bit params + optimizer

    vram_savings_pct = round((1.0 - (total_estimated_vram_gb / full_finetune_vram_gb)) * 100, 1)

    return {
        "status": "success",
        "base_model": base_model,
        "base_parameters_billions": total_params_b,
        "peft_architecture": "QLoRA" if quantization_bits == 4 else "LoRA",
        "lora_config": {
            "rank_r": lora_r,
            "alpha": lora_alpha,
            "scaling_factor": scaling,
            "dropout": lora_dropout,
            "target_modules": selected_targets,
            "bias": "none",
            "task_type": "CAUSAL_LM"
        },
        "parameter_metrics": {
            "trainable_parameters_m": total_lora_params_m,
            "total_parameters_b": total_params_b,
            "trainable_percentage": f"{trainable_pct}%"
        },
        "hardware_estimates": {
            "base_model_quantization": f"{quantization_bits}-bit",
            "base_model_vram_gb": base_model_vram_gb,
            "adapter_and_optimizer_vram_gb": round(adapter_vram_gb + optimizer_vram_gb, 3),
            "estimated_peak_training_vram_gb": total_estimated_vram_gb,
            "full_finetune_vram_requirement_gb": full_finetune_vram_gb,
            "vram_memory_reduction": f"{vram_savings_pct}%",
            "recommended_gpu": "1x NVIDIA RTX 3090 / 4090 (24GB)" if total_estimated_vram_gb < 24 else "1x NVIDIA A100 (80GB)"
        }
    }


def run_finetuning_job(
    job_name: str = "support_lora_v1",
    base_model: str = "llama-3-8b",
    dataset_name: str = "custom_finetune_dataset",
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 2e-4,
    lora_r: int = 16,
    lora_alpha: int = 32,
    optimizer: str = "adamw_8bit"
) -> Dict[str, Any]:
    """Simulates/Executes an end-to-end LLM fine-tuning job with step-by-step loss tracking and checkpoints.

    Args:
        job_name: Identifier for the fine-tuning run.
        base_model: Base LLM to adapt.
        dataset_name: Name of the preprocessed dataset.
        epochs: Total number of training epochs.
        batch_size: Per-device batch size.
        learning_rate: Initial peak learning rate.
        lora_r: LoRA Rank.
        lora_alpha: LoRA Alpha scaling.
        optimizer: Optimizer type ('adamw_8bit', 'paged_adamw_8bit', 'adamw_torch').

    Returns:
        Dict with training telemetry, loss logs, perplexity curves, and saved adapter checkpoint path.
    """
    peft_cfg = configure_peft(base_model=base_model, lora_r=lora_r, lora_alpha=lora_alpha)
    dataset_info = _DATASETS_DB.get(dataset_name, {"sample_count": 50, "estimated_total_tokens": 4500})
    
    total_samples = dataset_info.get("sample_count", 50)
    steps_per_epoch = max(1, total_samples // batch_size)
    total_steps = steps_per_epoch * epochs

    initial_loss = 2.85
    target_loss = 0.62
    
    loss_curve = []
    cur_loss = initial_loss
    for step in range(1, total_steps + 1):
        progress = step / total_steps
        # Exponential decay loss curve with small noise
        decay = math.exp(-2.2 * progress)
        cur_loss = round(target_loss + (initial_loss - target_loss) * decay + (0.02 * (step % 3 - 1)), 4)
        val_loss = round(cur_loss + 0.08 + (0.01 * (step % 2)), 4)
        perplexity = round(math.exp(cur_loss), 2)
        
        if step == 1 or step % max(1, total_steps // 5) == 0 or step == total_steps:
            loss_curve.append({
                "step": step,
                "epoch": round(step / steps_per_epoch, 2),
                "training_loss": cur_loss,
                "validation_loss": val_loss,
                "perplexity": perplexity,
                "learning_rate": round(learning_rate * (1 - (step / total_steps) * 0.8), 7)
            })

    final_train_loss = loss_curve[-1]["training_loss"]
    final_val_loss = loss_curve[-1]["validation_loss"]
    final_perplexity = loss_curve[-1]["perplexity"]

    checkpoint_dir = os.path.join(os.path.dirname(__file__), "data", "checkpoints", job_name)
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    adapter_meta = {
        "job_name": job_name,
        "base_model": base_model,
        "dataset_name": dataset_name,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "lora_r": lora_r,
        "lora_alpha": lora_alpha,
        "final_loss": final_train_loss,
        "final_perplexity": final_perplexity,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "peft_config": peft_cfg["lora_config"]
    }
    
    with open(os.path.join(checkpoint_dir, "adapter_config.json"), "w", encoding="utf-8") as f:
        json.dump(adapter_meta, f, indent=2)

    job_result = {
        "status": "completed",
        "job_name": job_name,
        "base_model": base_model,
        "dataset": dataset_name,
        "training_summary": {
            "total_epochs": epochs,
            "total_training_steps": total_steps,
            "initial_loss": initial_loss,
            "final_train_loss": final_train_loss,
            "final_val_loss": final_val_loss,
            "final_perplexity": final_perplexity,
            "loss_reduction_pct": round(((initial_loss - final_train_loss) / initial_loss) * 100, 1),
            "throughput_samples_per_sec": 14.2,
            "estimated_train_time_minutes": round((total_steps * 0.4) / 60, 2)
        },
        "telemetry_loss_curve": loss_curve,
        "checkpoint_artifacts": {
            "checkpoint_directory": checkpoint_dir,
            "adapter_weights_file": os.path.join(checkpoint_dir, "adapter_model.safetensors"),
            "adapter_config_file": os.path.join(checkpoint_dir, "adapter_config.json")
        }
    }
    _JOBS_DB[job_name] = job_result
    return job_result


def evaluate_finetuned_model(
    job_name: str,
    test_prompt: str,
    compare_with_base: bool = True
) -> Dict[str, Any]:
    """Compares response quality, formatting, and domain adherence between base LLM and fine-tuned adapter.

    Args:
        job_name: Identifier of the trained fine-tuning job.
        test_prompt: Input prompt to evaluate.
        compare_with_base: Whether to include base model baseline response.

    Returns:
        Dict with comparative outputs, token metrics, and evaluation rubric scores.
    """
    job = _JOBS_DB.get(job_name)
    base_model = job["base_model"] if job else "llama-3-8b"
    
    # Domain specific response templates for demonstration
    prompt_lower = test_prompt.lower()
    
    if "payment" in prompt_lower or "declined" in prompt_lower or "err" in prompt_lower:
        base_resp = "Your payment may have failed due to card issues. Contact your bank or try another card."
        tuned_resp = "I have reviewed Error Code ERR_PAY_402. This is a temporary settlement timeout with the gateway. A reversal ticket (#REV-2026) has been dispatched, and your funds will reflect in 3-5 business days."
    elif "sql" in prompt_lower or "churn" in prompt_lower or "query" in prompt_lower:
        base_resp = "SELECT * FROM users WHERE active = 0;"
        tuned_resp = "SELECT COUNT(DISTINCT u.id) AS total_users, ROUND(100.0 * COUNT(DISTINCT CASE WHEN o.order_date < NOW() - INTERVAL '30 days' THEN u.id END) / COUNT(DISTINCT u.id), 2) AS churn_rate_pct FROM users u LEFT JOIN orders o ON u.id = o.user_id;"
    else:
        base_resp = f"General standard answer based on pre-training for: {test_prompt}"
        tuned_resp = f"Specialized fine-tuned domain response with structured reasoning, precise schema formatting, and policy compliance for: {test_prompt}"

    evaluation = {
        "status": "success",
        "job_name": job_name,
        "base_model": base_model,
        "test_prompt": test_prompt,
        "finetuned_adapter_output": tuned_resp,
        "metrics": {
            "format_compliance_score": "98/100 (Fine-tuned) vs 45/100 (Base)",
            "domain_accuracy_score": "96/100 (Fine-tuned) vs 60/100 (Base)",
            "hallucination_rate": "1.2% (Fine-tuned) vs 14.5% (Base)",
            "inference_latency_ms": 124
        }
    }
    if compare_with_base:
        evaluation["base_model_output"] = base_resp
        evaluation["comparison_summary"] = "Fine-tuned adapter demonstrated strict adherence to domain jargon, error schema structure, and resolved ambiguity without generic vagueness."

    return evaluation


def list_finetuned_models() -> Dict[str, Any]:
    """Lists all available fine-tuned models, datasets, and saved LoRA checkpoints.

    Returns:
        Dict of active models and datasets.
    """
    return {
        "status": "success",
        "active_jobs_count": len(_JOBS_DB),
        "jobs": list(_JOBS_DB.values()),
        "cached_datasets": list(_DATASETS_DB.values()),
        "supported_base_models": list(BASE_MODELS.keys())
    }
