# Titanic Survivor Classifier 

- Predicts passenger survival using a from-scratch Decision Tree classifier, validated against sklearn.

- Dataset: Kaggle Titanic train.csv — 891 rows. Dropped Cabin/Ticket/Name. Filled missing Age with median, Embarked with mode. Binary-encoded Sex, one-hot encoded Embarked. Engineered Family = SibSp + Parch.
- Implementation: Entropy-based information gain splits, max_depth and min_sample stopping, majority-class leaf nodes. Matched against sklearn's DecisionTreeClassifier (max_depth=5, min_samples_split=6).
- Results: Custom 79.89% — sklearn 79.89% — naive baseline ~61.6%. Overfitting visible past depth 5.
