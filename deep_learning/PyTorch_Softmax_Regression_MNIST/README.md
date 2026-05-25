# PyTorch Softmax Regression on MNIST

## What It Does

A multi-class classifier that identifies handwritten digits (0–9) from grayscale images. Given a 28x28 pixel image, the model outputs a prediction of which digit it represents. This is the same problem shape as multi-class defect detection: instead of asking "is this digit a 3 or a 7?", a factory version asks "is this defect a scratch, dent, crack, or contamination?" The architecture is identical, only the data changes.

## How It Was Built

**Stack:** PyTorch, torchvision, matplotlib, scikit-learn

**Architecture:** Single linear layer — `nn.Linear(784, 10)` — with no hidden layers and no activation function. Each 28x28 image is flattened into a 784-dimensional vector, passed through the linear layer, and the 10 raw output logits go directly into `CrossEntropyLoss`, which applies softmax internally.

**Data pipeline:** MNIST loaded via `torchvision.datasets.MNIST`, batched with `DataLoader` (batch_size=64, shuffle=True for training). `ToTensor()` transform scales pixel values from [0, 255] to [0, 1].

**Optimizer comparison:** SGD (lr=0.01) reached 90.93% accuracy. Switching to Adam (lr=0.01) pushed accuracy to 92.74%. Adam's adaptive per-parameter learning rates handle the varied feature scales across 784 pixel positions better than a single fixed learning rate.

**Training:** 10 epochs. Loss converged by epoch 10.

## Result

**Test accuracy: 92.74%** — beats the lecture benchmark of 91.97%.

**Confusion matrix analysis:** The most confused digit pairs are:
- True 2 predicted as 8 (39 errors) — both share curved strokes
- True 5 predicted as 3 (38 errors) — similar top-half structure
- True 9 predicted as 4 (30 errors) — both have vertical lines with upper features
- True 7 predicted as 9 (30 errors) — vertical stroke with a top element

These errors expose the model's fundamental limitation: a single linear layer has no spatial awareness. It treats each pixel independently and cannot learn local shape features like curves, edges, or loops. This is exactly what convolutional layers solve.

## What I Learned

**DataLoader mechanics.** First time working with PyTorch's data pipeline. The Dataset handles "what data exists," the DataLoader handles "how to serve it in batches." Batch processing was new — evaluation required accumulating predictions across all batches rather than scoring one batch.

**CrossEntropyLoss absorbs softmax.** Adding a softmax activation before CrossEntropyLoss would apply softmax twice, producing incorrect gradients. The loss function expects raw logits. This pairing (raw logits + CrossEntropyLoss for multi-class, raw logits + BCEWithLogitsLoss for binary) is a PyTorch convention that avoids numerical instability.

**Why this architecture hits a ceiling.** With no hidden layers, the model is a linear decision boundary in 784-dimensional space. Digits that share pixel-level features (2 vs 8, 5 vs 3) are linearly inseparable. Adding convolutional layers that detect local spatial patterns (edges, curves, corners) is the next step — and the foundation for the Manufacturing Defect Detector.