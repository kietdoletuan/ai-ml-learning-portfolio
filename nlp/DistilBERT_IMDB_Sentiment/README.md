# DistilBERT Fine-Tuning — IMDB Sentiment Classification

Fine-tuned distilbert-base-uncased on 25,000 movie reviews to classify 
sentiment as positive or negative.

## What it does

Given any English text, predicts sentiment as positive or negative with a 
confidence score.

## How it was built

**Stack:** HuggingFace Transformers, Datasets, Evaluate, PyTorch (CUDA)

**Pipeline:** IMDB via HuggingFace Hub. WordPiece tokenization, truncation 
at 512 tokens. CLS token output feeds a linear classification head (768 → 2). 
Fine-tuned with Trainer API at lr=2e-5, batch_size=16, 3 epochs.

## Result

| Metric | Epoch 1 | Epoch 2 | Epoch 3 |
|--------|---------|---------|---------|
| Val Accuracy | 0.921 | 0.930 | 0.932 |
| AUC | 0.978 | 0.980 | 0.980 |
| Val Loss | 0.207 | 0.240 | 0.284 |

## What I learned

Val loss and accuracy can disagree on best checkpoint — val loss bottomed 
at epoch 1 while accuracy peaked at epoch 3. Set metric_for_best_model 
explicitly, never rely on loss as an accuracy proxy.

**Hardware:** RTX 3080 10GB, CUDA 12.8 | **Training time:** ~18 min