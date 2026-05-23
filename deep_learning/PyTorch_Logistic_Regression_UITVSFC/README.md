# PyTorch Logistic Regression on UIT-VSFC Vietnamese Sentiment

## What does this project do?

Binary sentiment classifier on Vietnamese student feedback. Takes a Vietnamese sentence and predicts positive or negative sentiment. Built as my first PyTorch training loop on real data, replacing the v3 plan of running Titanic again.

## How was it built?

UIT-VSFC dataset (Vietnamese Students' Feedback Corpus) filtered to binary (neutral dropped). Text converted to numerical features using TF-IDF vectorization from sklearn. Model is a single nn.Linear layer inside a custom nn.Module class, trained with BCEWithLogitsLoss and SGD (lr=1.0, 1000 epochs, full batch). No sigmoid in the model since BCEWithLogitsLoss handles it internally.

Dataset: [UIT-VSFC on Kaggle](https://www.kaggle.com/datasets/toreleon/synthetic-vietnamese-students-feedback-corpus?resource=download&select=synthetic_val.csv)

## What is the result?

PyTorch validation accuracy: 95.8%. Sklearn LogisticRegression on identical features: 96.9%. The ~1% gap is expected since sklearn uses L-BFGS (a more advanced optimizer) and runs until full convergence, while this model uses SGD with a fixed epoch count.

## What did I learn?

Knowing the training loop from drills and knowing it from building are different things. The 5-step loop itself had no bugs thanks to failure mode training earlier this week, but everything around it (data preprocessing, shape matching, sparse-to-dense conversion, loss.item() vs loss for tracking) required decisions the drills never surfaced. The biggest catch was reshaping y from (N,) to (N,1) to avoid the silent broadcasting trap with BCEWithLogitsLoss.