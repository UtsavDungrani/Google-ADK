"""
Hyperparameter Scaling & Optimization Tools for ADK Demo
Implements Chinchilla/Kaplan compute scaling laws, learning rate schedules,
batch size scaling rules, and multi-parameter hyperparameter sweeps.
"""

import math
import random
from typing import Dict, List, Any, Optional

# Pre-defined empirical constants from Kaplan / Chinchilla scaling law papers
CHINCHILLA_E = 1.69       # Irreducible entropy loss
CHINCHILLA_A = 406.4     # Parameter scaling coefficient
CHINCHILLA_B = 410.7     # Token scaling coefficient
CHINCHILLA_ALPHA = 0.34  # Parameter scaling power
CHINCHILLA_BETA = 0.28   # Token scaling power


def calculate_scaling_laws(
    compute_budget_pflops_days: Optional[float] = 10.0,
    model_params_b: Optional[float] = None,
    dataset_tokens_b: Optional[float] = None,
    target_loss: Optional[float] = None
) -> Dict[str, Any]:
    """Computes compute-optimal model size (N) and training tokens (D) using Chinchilla/Kaplan Scaling Laws.

    Formula: Compute C ≈ 6 * N * D (FLOPs).
    Chinchilla optimal: N_opt ∝ C^0.5, D_opt ∝ C^0.5 (equal compute scaling).

    Args:
        compute_budget_pflops_days: Total compute budget in PFLOPs-days (1 PFLOP-day = 8.64e19 FLOPs).
        model_params_b: Given model size in billions of parameters (if analyzing fixed model).
        dataset_tokens_b: Given dataset size in billions of tokens (if analyzing fixed tokens).
        target_loss: Desired cross-entropy validation loss target.

    Returns:
        Dict with compute-optimal parameters, tokens, FLOPs, predicted cross-entropy loss, and GPU-hours.
    """
    pflop_day_in_flops = 8.64e19
    
    if compute_budget_pflops_days:
        total_flops = compute_budget_pflops_days * pflop_day_in_flops
        # Optimal N and D according to Chinchilla (roughly equal scaling)
        # N_opt ≈ 0.6 * sqrt(C / 6), D_opt ≈ 1.6 * sqrt(C / 6)
        c_factor = math.sqrt(total_flops / 6.0)
        n_opt_params = 0.58 * c_factor
        d_opt_tokens = 1.72 * c_factor
        
        n_opt_b = round(n_opt_params / 1e9, 2)
        d_opt_b = round(d_opt_tokens / 1e9, 2)
    elif model_params_b and dataset_tokens_b:
        n_opt_params = model_params_b * 1e9
        d_opt_tokens = dataset_tokens_b * 1e9
        total_flops = 6.0 * n_opt_params * d_opt_tokens
        n_opt_b = model_params_b
        d_opt_b = dataset_tokens_b
    else:
        # Default fallback
        n_opt_b = 7.0
        d_opt_b = 140.0
        n_opt_params = n_opt_b * 1e9
        d_opt_tokens = d_opt_b * 1e9
        total_flops = 6.0 * n_opt_params * d_opt_tokens

    # Predicted Chinchilla loss L(N, D) = E + A/(N^alpha) + B/(D^beta)
    param_term = CHINCHILLA_A / (n_opt_params ** CHINCHILLA_ALPHA)
    token_term = CHINCHILLA_B / (d_opt_tokens ** CHINCHILLA_BETA)
    predicted_loss = round(CHINCHILLA_E + param_term + token_term, 4)
    predicted_perplexity = round(math.exp(predicted_loss), 2)

    # Hardware resource estimates: NVIDIA H100 (approx 1000 TFLOPS FP8/FP16 with MFU ~45%)
    effective_h100_tflops = 450.0 * 1e12
    seconds_required = total_flops / effective_h100_tflops
    gpu_hours_h100 = round(seconds_required / 3600.0, 1)
    estimated_cost_usd = round(gpu_hours_h100 * 3.50, 2)  # $3.50/hr H100 cloud pricing

    return {
        "status": "success",
        "compute_budget_flops": f"{total_flops:.2e}",
        "compute_budget_pflops_days": round(total_flops / pflop_day_in_flops, 2),
        "optimal_allocations": {
            "optimal_parameters_billions": n_opt_b,
            "optimal_training_tokens_billions": d_opt_b,
            "tokens_to_parameters_ratio": round(d_opt_b / max(0.1, n_opt_b), 1),
            "law_used": "Chinchilla Compute-Optimal Frontier (Hoffmann et al.)"
        },
        "performance_predictions": {
            "predicted_cross_entropy_loss": predicted_loss,
            "predicted_perplexity": predicted_perplexity,
            "irreducible_entropy_floor": CHINCHILLA_E
        },
        "hardware_cost_estimates": {
            "nvidia_h100_gpu_hours": gpu_hours_h100,
            "estimated_cluster_cost_usd": f"${estimated_cost_usd:,}",
            "assumed_model_flops_utilization_mfu": "45%"
        }
    }


def simulate_lr_schedules(
    schedule_type: str = "cosine_with_warmup",
    base_lr: float = 3e-4,
    min_lr: float = 3e-5,
    warmup_steps: int = 100,
    total_steps: int = 1000
) -> Dict[str, Any]:
    """Simulates learning rate trajectories across different scheduling strategies.

    Args:
        schedule_type: Type of schedule ('cosine_with_warmup', 'linear_decay', 'one_cycle', 'constant_warmup').
        base_lr: Maximum peak learning rate.
        min_lr: Final floor learning rate.
        warmup_steps: Number of initial warmup steps.
        total_steps: Total training steps.

    Returns:
        Dict with step-by-step LR trajectory, warmup ratio, decay characteristics, and recommendations.
    """
    trajectory = []
    sample_points = [0, warmup_steps // 2, warmup_steps, int(total_steps * 0.25), int(total_steps * 0.5), int(total_steps * 0.75), total_steps]
    sample_points = sorted(list(set([p for p in sample_points if 0 <= p <= total_steps])))

    for step in sample_points:
        if step < warmup_steps:
            # Linear warmup
            current_lr = (step / max(1, warmup_steps)) * base_lr
        else:
            progress = (step - warmup_steps) / max(1, (total_steps - warmup_steps))
            if schedule_type == "cosine_with_warmup":
                cosine_decay = 0.5 * (1.0 + math.cos(math.pi * progress))
                current_lr = min_lr + (base_lr - min_lr) * cosine_decay
            elif schedule_type == "linear_decay":
                current_lr = base_lr - progress * (base_lr - min_lr)
            elif schedule_type == "one_cycle":
                # Drops steeply near end
                current_lr = base_lr * (1.0 - progress**2) + min_lr * (progress**2)
            else:  # constant_warmup
                current_lr = base_lr

        trajectory.append({
            "step": step,
            "progress_pct": f"{round((step / total_steps) * 100, 1)}%",
            "learning_rate": round(current_lr, 8)
        })

    warmup_ratio = round((warmup_steps / total_steps) * 100, 1)
    
    recommendation = (
        "Cosine with Warmup is recommended for LLM pre-training and fine-tuning because it prevents early gradient explosion "
        "and smoothly anneals towards local minima without aggressive plateaus."
    )

    return {
        "status": "success",
        "schedule_type": schedule_type,
        "base_learning_rate": base_lr,
        "minimum_learning_rate": min_lr,
        "warmup_steps": warmup_steps,
        "warmup_ratio": f"{warmup_ratio}% of total steps",
        "total_steps": total_steps,
        "lr_trajectory_milestones": trajectory,
        "stability_analysis": {
            "initial_gradient_risk": "Low (Protected by warmup)" if warmup_steps > 0 else "High (Risk of early NaN divergence)",
            "final_annealing_rate": "Smooth (Asymptotic cosine decay)",
            "expert_recommendation": recommendation
        }
    }


def scale_batch_size(
    base_batch_size: int = 16,
    target_batch_size: int = 128,
    base_lr: float = 2e-4,
    gpu_count: int = 4,
    scaling_rule: str = "square_root"
) -> Dict[str, Any]:
    """Calculates scaled learning rates, gradient accumulation steps, and throughput for distributed training.

    Args:
        base_batch_size: Original verified batch size.
        target_batch_size: Desired global effective batch size.
        base_lr: Baseline learning rate for base_batch_size.
        gpu_count: Number of GPUs in the training cluster.
        scaling_rule: 'linear' (LR * k) or 'square_root' (LR * sqrt(k), recommended for AdamW/Adafactor).

    Returns:
        Dict with adjusted learning rate, gradient accumulation steps, and memory per GPU.
    """
    scale_factor = target_batch_size / max(1, base_batch_size)
    
    if scaling_rule == "linear":
        scaled_lr = base_lr * scale_factor
    else:  # square_root
        scaled_lr = base_lr * math.sqrt(scale_factor)

    per_device_batch_size = max(1, 16 // gpu_count)
    required_grad_accum = math.ceil(target_batch_size / (gpu_count * per_device_batch_size))
    actual_effective_batch = gpu_count * per_device_batch_size * required_grad_accum

    return {
        "status": "success",
        "base_configuration": {
            "batch_size": base_batch_size,
            "learning_rate": base_lr
        },
        "target_configuration": {
            "target_batch_size": target_batch_size,
            "actual_effective_batch_size": actual_effective_batch,
            "scaling_multiplier": round(scale_factor, 2),
            "scaling_rule_applied": f"{scaling_rule.capitalize()} Scaling Rule",
            "adjusted_learning_rate": round(scaled_lr, 7)
        },
        "distributed_execution_plan": {
            "gpu_count": gpu_count,
            "per_device_micro_batch_size": per_device_batch_size,
            "gradient_accumulation_steps": required_grad_accum,
            "effective_update_cadence": f"1 Optimizer Step every {required_grad_accum} forward passes",
            "communication_overhead": "Low (Gradients synchronized only after accumulation window)"
        }
    }


def run_hyperparameter_sweep(
    search_strategy: str = "bayesian_optimization",
    num_trials: int = 5,
    metric_to_optimize: str = "validation_loss"
) -> Dict[str, Any]:
    """Performs an automated Hyperparameter Sweep across learning rate, LoRA rank r, LoRA alpha, and weight decay.

    Args:
        search_strategy: Optimization method ('bayesian_optimization', 'grid_search', 'random_search').
        num_trials: Number of parameter combination trials to execute.
        metric_to_optimize: Metric to minimize ('validation_loss', 'perplexity', 'training_time').

    Returns:
        Dict with top trials, optimal parameter set, Pareto frontier, and parameter importance scores.
    """
    random.seed(42)  # For reproducible demo results
    
    trials = []
    
    # Candidate hyperparameter grid
    candidate_lrs = [5e-5, 1e-4, 2e-4, 3e-4, 5e-4]
    candidate_ranks = [8, 16, 32, 64]
    candidate_decays = [0.01, 0.05, 0.1]
    candidate_warmups = [0.03, 0.05, 0.1]

    for trial_id in range(1, num_trials + 1):
        lr = candidate_lrs[(trial_id - 1) % len(candidate_lrs)]
        rank = candidate_ranks[(trial_id * 2) % len(candidate_ranks)]
        alpha = rank * 2
        decay = candidate_decays[trial_id % len(candidate_decays)]
        warmup = candidate_warmups[trial_id % len(candidate_warmups)]

        # Objective function modeling with realistic convex loss bowl
        # Optimal around lr=2e-4, rank=16 or 32, warmup=0.05
        lr_penalty = abs(math.log10(lr) - math.log10(2e-4)) * 0.4
        rank_bonus = 0.05 if rank in [16, 32] else 0.12
        warmup_bonus = 0.02 if warmup == 0.05 else 0.07
        
        val_loss = round(0.58 + lr_penalty + rank_bonus + warmup_bonus + (random.uniform(-0.02, 0.02)), 4)
        val_ppl = round(math.exp(val_loss), 2)
        score = round(100.0 - (val_loss * 25.0), 1)

        trials.append({
            "trial_id": f"TRIAL_{trial_id:03d}",
            "learning_rate": lr,
            "lora_rank_r": rank,
            "lora_alpha": alpha,
            "weight_decay": decay,
            "warmup_ratio": warmup,
            "validation_loss": val_loss,
            "validation_perplexity": val_ppl,
            "quality_score": f"{score}/100"
        })

    # Sort by lowest validation loss
    sorted_trials = sorted(trials, key=lambda x: x["validation_loss"])
    best_trial = sorted_trials[0]

    return {
        "status": "completed",
        "search_strategy": search_strategy,
        "total_trials_evaluated": len(trials),
        "target_metric": metric_to_optimize,
        "best_hyperparameter_configuration": best_trial,
        "parameter_importance_ranking": [
            {"parameter": "learning_rate", "importance_pct": 52.4, "note": "Dominant factor for loss convergence and stability"},
            {"parameter": "lora_rank_r", "importance_pct": 24.1, "note": "Controls expressive capacity of the adaptation"},
            {"parameter": "warmup_ratio", "importance_pct": 14.8, "note": "Prevents catastrophic early gradient saturation"},
            {"parameter": "weight_decay", "importance_pct": 8.7, "note": "L2 regularization on adapter weights"}
        ],
        "all_trial_results": sorted_trials
    }
