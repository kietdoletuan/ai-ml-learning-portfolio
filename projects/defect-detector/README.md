# Manufacturing Defect Detector — PaDiM on MVTec AD

**Live demo:** https://huggingface.co/spaces/KietDo/leather-defect-detector

---

## What It Does

This system detects surface defects in leather by learning what a normal leather surface looks like, then flagging anything that deviates from that pattern. Upload a leather image and the model returns an anomaly score, a pass/fail decision, and a heatmap showing exactly where the defect is located.

This is anomaly detection, not classification. The model never sees a defective image during training. It learns the distribution of normal features and uses Mahalanobis distance at inference time to measure how far each spatial region deviates from that distribution. This is the correct paradigm for industrial inspection where defect types are unpredictable and labeled defect data is scarce.

The demo uses the leather category from the MVTec Anomaly Detection benchmark. PaDiM was benchmarked across all 15 MVTec categories during development. Leather was selected for the demo because it achieves near-perfect scores (Image AUROC 1.00, Pixel AUROC 0.99) and produces visually compelling heatmaps that clearly illustrate where defects are localized.

---

## How It Was Built

**Model: PaDiM (Patch Distribution Modeling)**

PaDiM uses a frozen pretrained ResNet18 backbone to extract patch-level features from normal training images. For each spatial location in the feature map, it fits a multivariate Gaussian (mean vector and covariance matrix) over the training set. At inference time, Mahalanobis distance between the test patch feature and the learned Gaussian produces a per-pixel anomaly score. The image-level score is the maximum across the spatial map.

This approach requires no defect labels, no defect images during training, and no segmentation annotations. The pixel-level anomaly map emerges directly from the distance computation — there is no separate segmentation head.

**Dataset: MVTec AD**

5,354 high-resolution images across 15 industrial categories covering textures and objects. Training split is normal images only. Test split includes both normal and defective images with ground-truth masks. The leather category has 245 training images and 92 test images across 5 defect types (cuts, folds, glue, poke, color).

**Tech stack:** PyTorch, anomalib 1.2.0, Lightning, Gradio, HuggingFace Spaces

**Training:** RTX 3080 10GB, CUDA 12.8, local training in under 5 minutes for the leather category. All 15 categories benchmarked in a single unattended run, results logged to MLflow (SQLite backend).

**Inference pipeline:**
1. User uploads PIL image via Gradio
2. Image saved to temp file, loaded via anomalib PredictDataset
3. engine.predict() runs the trained PaDiM model
4. anomaly_map extracted, normalized to [0,1], scaled to uint8
5. JET colormap applied via OpenCV
6. Heatmap resized to original image dimensions and blended (60/40) with original
7. pred_label (threshold applied during training on validation set) gives binary decision

**Heatmap pipeline note:** The threshold separating normal from anomalous is computed during training via F1-optimal adaptive thresholding on the validation set and stored inside the checkpoint. It is not a hardcoded value.

---

## Results

| Category | Image AUROC | Pixel AUROC |
|----------|-------------|-------------|
| Leather (demo) | **1.00** | **0.99** |
| Wood | 0.97 | 0.93 |
| Carpet | 0.95 | 0.96 |
| Tile | 0.92 | 0.93 |
| Bottle | 0.91 | 0.91 |
| Transistor | 0.89 | 0.80 |
| Metal Nut | 0.87 | 0.94 |
| Hazelnut | 0.66 | 0.97 |

Full 15-category benchmark results logged in MLflow. Notable pattern: Pixel AUROC stays consistently high (0.92-0.99) even for categories where Image AUROC is lower, meaning anomaly localization is more robust than image-level binary detection.

**On Hazelnut:** Image AUROC 0.66 despite Pixel AUROC 0.97 is not a bug — it reflects that some hazelnut defects are subtle enough that the maximum anomaly map score falls near the threshold, while the localization itself remains accurate. This is a known challenge with max-pooling for image-level scoring on small localized defects.

---

## What I Learned

**The gap between benchmark and real factory data is significant.** MVTec AD is unusually clean — controlled lighting, fixed camera position, plain backgrounds, consistent scale. Real factory images have motion blur, variable lighting, shadows, and surface variation from manufacturing tolerances that PaDiM will flag as anomalous. The demo shows what near-perfect-condition benchmark performance looks like. Deploying to a real factory line would require: (1) retraining on images captured under production conditions, (2) a domain-specific normal image dataset from that factory, and (3) recalibrating the threshold against production data.

**Anomaly detection requires the right framing.** The initial approach in this project was to build a supervised multi-class classifier — YOLO for defect detection, one class per defect type. This fails on MVTec because the training set provides only 6-10 defective images per defect subtype, which is not enough for supervised learning. More importantly, it would require labeling every possible defect type in advance, which is not feasible in practice. The anomaly detection framing (train on normal only, flag deviations) is the correct industrial approach.

**Deployment environment pinning matters.** The local training environment (Python 3.10, matplotlib 3.9.2, anomalib 1.2.0) worked correctly. Deploying to HuggingFace Spaces with a newer Python and matplotlib version broke anomalib's internal visualizer callback. The correct approach is to export and pin the full working environment from the start, not discover conflicts one deployment at a time.

---

## Real-World Application Notes

For teams considering adapting this for real factory use:

**Image capture requirements:** Fixed camera mount (handheld introduces position variance that changes the feature distribution), diffuse lighting (lightbox or dual 45-degree lights — no direct flash), plain contrasting background, consistent distance and zoom. Training and inference images must be captured under identical conditions.

**Training data requirements:** Minimum 200 normal images of the target component, 300+ preferred. PaDiM is sample-efficient relative to supervised methods. Test set needs at least 50 images with 10-15 defective examples per defect type to produce meaningful AUROC numbers.

**Scope:** One model per component type. Do not attempt to cover multiple components with a single model — PaDiM's normality distribution is component-specific. This matches the MVTec benchmark design where each category is trained and evaluated independently.

---

## Repository Structure

```
projects/defect-detector/
  gradio_demo/
    app.py
    requirements.txt
    README.md        (HuggingFace Spaces config)
  notebooks/
    01_data_exploration.ipynb
    02_padim_anomalib.ipynb
  README.md          (this file)
```

Dataset (MVTec AD, CC BY-NC-SA 4.0) is not committed. Add `data/` to `.gitignore` immediately — the dataset is 4.7GB.

Model checkpoint hosted at: https://huggingface.co/KietDo/padim-mvtec-leather
