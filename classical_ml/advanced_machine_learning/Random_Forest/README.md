# Titanic Survivor Classifier 

- Predicts passenger survival using a  Random Forest Tree classifier.

- Dataset: Kaggle Titanic train.csv — 891 rows. Dropped Cabin/Ticket/Name. Filled missing Age with median, Embarked with mode. Binary-encoded Sex, one-hot encoded Embarked. Engineered Family = SibSp + Parch.
- Result: Best configuration is 200 trees at max_depth 5 achieved 88% test accuracy, outperforming the single Decision Tree by 1% probably due to the simplicity of the dataset. OOB error stabilised at approximately 100 trees. Sex ranked first for both models, but RF surfaced Fare as second most important — a feature the Decision Tree largely ignored.
- What I learned: RF's random feature subsetting forces trees to explore secondary features that greedy single-tree selection ignores. Averaging across diverse trees reveals importance patterns invisible to any individual tree. OOB error provides a free generalisation estimate without sacrificing training data to a validation set.
