# Comprehensive Guide to LLM Fine-Tuning and Parameter-Efficient Adaptation (PEFT)

## 1. Introduction to Supervised Fine-Tuning (SFT)
Supervised Fine-Tuning (SFT) is the process of taking a pre-trained base Large Language Model (such as LLaMA 3, Mistral, or Qwen) and training it on structured (Instruction, Input, Output) demonstration datasets to specialize the model for specific downstream tasks, adhere to exact output schemas (JSON/SQL), or embody a distinct conversational persona.

### Core Stages:
1. **Instruction Formatting**: Converting raw examples into prompt templates like Alpaca, ChatML, or ShareGPT.
2. **Loss Masking**: Computing cross-entropy loss exclusively on completion/target tokens rather than instruction prompt tokens.
3. **Weight Updating**: Modifying model parameters to minimize token-level cross-entropy loss $L = -\sum \log P(w_t \mid w_{<t})$.

---

## 2. Parameter-Efficient Fine-Tuning (PEFT) & LoRA / QLoRA
Full fine-tuning of multi-billion parameter models requires storing full optimizer states (16 bytes per parameter for FP32 AdamW), leading to exorbitant VRAM requirements (e.g. over 120 GB for a 7B model).

### Low-Rank Adaptation (LoRA):
- **Core Mechanism**: Freezes pre-trained weight matrix $W_0 \in \mathbb{R}^{d \times k}$ and decomposes the update matrix $\Delta W$ into two low-rank matrices:
  $$\Delta W = \frac{\alpha}{r} (B \cdot A)$$
  where $A \in \mathbb{R}^{r \times k}$ is initialized randomly with Gaussian distribution and $B \in \mathbb{R}^{d \times r}$ is initialized to zero.
- **Rank $r$**: Typically set to 8, 16, 32, or 64. Higher rank allows modeling more complex tasks but increases parameter count.
- **Scaling Factor $\alpha$**: Controls the weight of adapter updates; standard convention is $\alpha = 2 \times r$.
- **Target Modules**: Usually injected into attention projection layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`) and feed-forward MLP layers (`gate_proj`, `up_proj`, `down_proj`).

### QLoRA (Quantized LoRA):
- Quantizes the base model weights to 4-bit NormalFloat (NF4) with Double Quantization.
- Maintains 16-bit LoRA adapter weights, enabling a 70B parameter LLM to be fine-tuned on a single consumer GPU (24GB VRAM).

---

## 3. Training Dynamics and Catastrophic Forgetting
- **Learning Rate**: PEFT typically requires higher learning rates (e.g., $1\times 10^{-4}$ to $3\times 10^{-4}$) than full fine-tuning ($1\times 10^{-5}$ to $5\times 10^{-5}$).
- **Catastrophic Forgetting**: Fine-tuning aggressively on a narrow dataset can degrade general reasoning capabilities. Mitigation includes mixing 5-10% general instruction data (replay buffer) and keeping rank $r \le 32$.
