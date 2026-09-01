# Transformer Compute Scaling Laws and Hyperparameter Schedulers

## 1. Chinchilla Compute-Optimal Frontier (Hoffmann et al.)
In 2020, Kaplan et al. proposed power-law scaling suggesting model parameters should scale faster than training tokens ($N \propto C^{0.73}, D \propto C^{0.27}$). However, DeepMind's Chinchilla study (2022) revealed that models like GPT-3 (175B parameters trained on 300B tokens) and Gopher (280B) were significantly under-trained.

### The Chinchilla Law:
$$C \approx 6 \cdot N \cdot D \quad (\text{FLOPs})$$
For compute-optimal performance, model parameters $N$ and training tokens $D$ should be scaled in equal proportions:
$$N_{\text{opt}} \propto \sqrt{C}, \quad D_{\text{opt}} \propto \sqrt{C}$$
Empirical rule of thumb: A compute-optimal model should be trained on approximately **20 tokens per model parameter**. For example, a 7B model requires at least 140 Billion tokens to be compute-optimal, while modern production models (LLaMA 3) push inference-optimality by training on over 15 Trillion tokens (over 1800 tokens/parameter).

---

## 2. Learning Rate Scheduling in Transformers
Large Language Models exhibit extreme sensitivity to initial gradients during early iterations:

1. **Warmup Phase**:
   - Linear ramp from $0$ to $\eta_{\text{max}}$ over the first 1% to 5% of training steps.
   - Prevents destabilization of LayerNorm and Attention matrix variances when gradients are large and noisy.

2. **Cosine Annealing Phase**:
   $$\eta_t = \eta_{\text{min}} + \frac{1}{2}(\eta_{\text{max}} - \eta_{\text{min}})\left(1 + \cos\left(\frac{t - T_{\text{warm}}}{T_{\text{total}} - T_{\text{warm}}}\pi\right)\right)$$
   - Smoothly decays learning rate towards $\eta_{\text{min}} \approx 0.1 \times \eta_{\text{max}}$.
   - Avoids abrupt plateaus and helps gradient descent escape sharp sub-optimal saddle points.

---

## 3. Batch Size Scaling Rules (Linear vs Square-Root)
When scaling training across multiple GPUs or clusters:
- **Linear Scaling Rule**: $\eta_{\text{new}} = \eta_{\text{base}} \times \frac{B_{\text{new}}}{B_{\text{base}}}$ (Common in SGD without momentum).
- **Square-Root Scaling Rule**: $\eta_{\text{new}} = \eta_{\text{base}} \times \sqrt{\frac{B_{\text{new}}}{B_{\text{base}}}}$ (Standard for Adaptive Optimizers like AdamW and Adafactor, maintaining variance of gradient updates).
