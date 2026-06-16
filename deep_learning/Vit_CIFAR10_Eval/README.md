# ViT vs CNN — CIFAR-10 Accuracy Comparison

## What It Does
ViT splits images into fixed-size patches and applies self-attention across all patches, enabling global context from the first layer. This notebook evaluates a fine-tuned ViT checkpoint against the W1 CNN baseline on the CIFAR-10 test set. No training was performed.

## How It Was Built
Vanilla `vit-base-patch16-224` cannot be used directly on CIFAR-10: its classification head outputs 1000 ImageNet classes (not 10), and its patch embeddings were trained on 224×224 images while CIFAR-10 is 32×32. A CIFAR-10 fine-tuned checkpoint was loaded instead, resolving both issues.

**Model:** [nateraw/vit-base-patch16-224-cifar10](https://huggingface.co/nateraw/vit-base-patch16-224-cifar10)

A custom collate function was required because PyTorch's default collate cannot stack PIL images into tensors. The function returns images as a Python list for the processor and stacks labels as a tensor.

## Results
| Model | Test Accuracy |
|-------|--------------|
| ViT (fine-tuned) | 98.52% |
| CNN from scratch (W1) | 75.57% |

The gap reflects pretraining advantage, not architecture alone. The ViT was pretrained on ImageNet (1.2 million images, 1000 classes) before fine-tuning. The CNN was trained from scratch on CIFAR-10 only.

## What I Learned
Permutation invariance is a core limitation of self-attention: patches carry no positional information, so the model cannot distinguish patch at position 1 from patch at position 5 without explicit help. Positional encodings are added to patch embeddings to fix this. ViT also lacks CNN's inductive biases (local connectivity, translation equivariance), which is why it needs significantly more data to match CNN performance at small scales.