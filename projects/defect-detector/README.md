# Manufacturing Defect Detector

A computer vision system that inspects a photo of a manufactured part and flags whether it is defective, and shows where the defect is as a heatmap overlay. It learns what a normal, defect-free part looks like from training images alone, then flags anything that deviates from that learned normal distribution. Trained and benchmarked on MVTec AD, the standard academic dataset for industrial inspection.

---

## Architectural Decision Record

Decisions locked before any model code was written — 2026-06-17.

### Decision 1: Anomaly detection as the primary approach (not supervised multi-class classification)

The original framing for this project was supervised multi-class defect classification — train a CNN to distinguish scratch vs dent vs contamination vs crack. This was rejected for two compounding reasons.

First, MVTec AD's `train/` folder contains only defect-free ("good") images for every category. There are no defect labels at training time. A supervised classifier would have to train on the `test/` folder, which is data leakage and disqualifies the approach entirely.

Second, even setting aside leakage, the test set contains roughly 6 to 10 defect images per subtype per category. A supervised classifier trained on 6 examples of one class does not learn that class — it memorises those 6 images and fails on any variation. This is per-class data starvation, and it makes supervised multi-class structurally unsolvable on this benchmark.

The correct framing is one-class unsupervised anomaly detection: model the distribution of normal images, then score deviations at test time. This is what MVTec AD was designed for and what every paper in the field uses it for.

### Decision 2: PaDiM as the starting model

PaDiM (Patch Distribution Modeling) was chosen as the baseline anomaly detection model for the following reasons. It trains in a single forward pass over normal images — no gradient updates, no loss function, no hyperparameter tuning required for the core method. It produces interpretable outputs: a per-spatial-location multivariate Gaussian (mean vector + covariance matrix) fit over pretrained CNN features, scored at test time via Mahalanobis distance to produce a pixel-level anomaly heatmap. It is fast and lightweight enough to run on a local GPU for a single category in under a minute. It serves as a clean baseline before deciding whether PatchCore (sharper heatmaps via nearest-neighbour memory bank, higher memory cost) is worth the tradeoff.

The backbone is a pretrained ResNet18 or WideResNet — the same architecture used in the transfer learning session the day before, so the feature extraction mechanism is already understood.

### Decision 3: Supervised binary ResNet18 comparison as a deliberate secondary track

On one category, a supervised binary good-vs-defect classifier will be built using ResNet18 transfer learning. This is not a fallback and not scope creep. It exists for a specific purpose: to demonstrate concretely why supervised classification is data-starved on MVTec AD, and to produce a direct quantitative comparison between the anomaly detection result and the supervised result on identical data.


---

## Dataset

**MVTec AD** — 5,354 high-resolution images across 15 industrial categories, 73 defect types. Each category's `train/` folder contains only defect-free images. The `test/` folder contains both normal and defective images with pixel-level ground-truth segmentation masks.

License: CC BY-NC-SA 4.0 (research and educational use only).

Dataset is not committed to this repository. Download from [mvtec.com/company/research/datasets/mvtec-ad](https://www.mvtec.com/company/research/datasets/mvtec-ad) and place in `data/mvtec_anomaly_detection/`. The `data/` directory is gitignored.

---

## Tech Stack

- **anomalib** — industrial anomaly detection library (open-edge-platform). Ships PaDiM, PatchCore, EfficientAD, and others. Built-in MVTec AD dataloader, Gradio inference, and ONNX/OpenVINO export.
- **PyTorch + torchvision** — supervised comparison track (ResNet18 transfer learning).
- **MLFlow** — experiment logging for all runs (sqlite backend at repo root).
- **Gradio + HuggingFace Spaces** — live demo deployment.

---

## Metrics

**Anomaly detection track:** image-level AUROC (detection), pixel-level AUROC and AU-PRO (localisation). Reported per category, not averaged — averaged numbers hide per-category failure modes that are the actual story.

**Supervised comparison track:** precision, recall, F1, AUROC on the binary good-vs-defect classification task.

Macro F1 is not used as a primary metric on the anomaly track. It is threshold-dependent (computed at one operating point), while AUROC summarises performance across all thresholds. It also presupposes discrete class labels at training time, which do not exist in MVTec AD training data.

---

## Results

*To be filled after training. Per-category image AUROC, pixel AUROC, and AU-PRO will be logged here with MLFlow run links.*

---

## What I Learned

*To be filled after the project completes.*

---

## Live Demo

*HuggingFace Spaces URL — to be added after deployment (target Summer Week 5).*
