# LoRA Rank-8 from Scratch

## What it does

Implements Low-Rank Adaptation (LoRA) from the original paper (arxiv.org/abs/2106.09685) by hand in PyTorch, then wires it into a real attention module instead of a toy linear layer. A frozen pretrained weight matrix W stays untouched. Two small matrices, B (out_features × r) and A (r × in_features), are trained instead, and their product BA is added to W's output. This is the mechanism that makes fine-tuning large models cheap: instead of updating every parameter in W, you update a rank-r bottleneck with far fewer parameters, and B starts at zero so the adapter is a no-op at initialization.

The exercise has six phases. This README documents phases 1 through 3, which were built and verified. Phases 4 through 6 were closed by cold recall check, not executed, and that distinction is stated explicitly below rather than implied.

## How built

**Phase 1 — LoRALinear module.** Frozen base `nn.Linear` wrapped with a LoRA adapter: `B` (out_features × r) and `A` (r × in_features), shapes derived from scratch to make sure BA matches W and not W.T. `B` initialized to zero, `A` to small Gaussian, so the adapter starts as an exact identity relative to the frozen base. Forward pass returns `base(x) + scaling * (x @ A.T @ B.T)`.

**Phase 2 — Identity-start proof.** Verified with `torch.allclose` that model output at initialization is numerically identical to the frozen base alone, not just shape-checked. A shape-only check was caught mid-session as insufficient before this proof was written.

**Phase 3 — SingleHeadAttention integration.** Built a real attention module from scratch (Wq, Wk, Wv, Wo as separate `nn.Linear` layers, not the NumPy formula-only version from the June 6 self-attention build). Wq and Wv swapped for `LoRALinear` behind a `use_lora` flag; Wk and Wo left untouched, following the paper's own ablation showing Q and V adaptation matters more than K. Integration-level identity proof required a second attempt: the first attempt compared two separately-initialized instances, which is meaningless since two random inits never match. Corrected by reconstructing the frozen-only forward path from the same LoRA instance's own base layers and comparing against its real forward pass. Came back `True`.

**Phases 4 and 5 — closed by recall check, not run.** No training loop was executed and no rank sweep was run. Verification method for phase 4 stated cold: check `optimizer.param_groups` directly, since `requires_grad` only encodes intent before training and does not prove what the optimizer actually updates — a bug that puts all of `model.parameters()` into the optimizer would pass a `requires_grad` check clean while still updating frozen weights. The actual proof is empirical: clone Wk, Wo, and base Wq/Wv before training, run a step, compare after with `torch.equal` or `torch.allclose`. For phase 5, expected pattern stated cold: trainable parameter count for the adapter scales linearly in r as r × (in_features + out_features), and performance shows diminishing returns as r increases, with rank 1 or 2 already capturing most useful update directions for many fine-tuning tasks per the paper's own findings.

## Result

Frozen-base identity-start confirmed via `torch.allclose` at both the module level and the integration level inside real attention. No numerical training result exists for this exercise since phases 4 and 5 were not executed.

## What I learned

The most useful bug wasn't conceptual, it was a typo: `requires_grad` written as `required_grad` produced no crash and silently left the base layer fully trainable. It only surfaced through a trainable-parameter-count comparison (300 vs 2838), which is now a standing check before any training run, not just for LoRA. Separately, the two failed identity checks (shape-only, then two-separate-instances) reinforced the same lesson twice: a check that doesn't actually rule out the failure mode it's supposed to catch is worse than no check, because it produces false confidence. The Q/V-over-K adaptation choice was accepted as a plausible mechanism from the paper (Q and V more task-specific, K closer to stable token identity) rather than derived from first principles, and is flagged as such rather than presented as fully understood.
