# Titanic Survivor Classifier

- Predicts passenger survival using an Adaboost classifier.

- Dataset: Kaggle Titanic `train.csv` (891 rows). Dropped `Cabin`, `Ticket`, and `Name`. Filled missing `Age` with median and `Embarked` with mode. Encoded `Sex`, one-hot encoded `Embarked`, and engineered `Family = SibSp + Parch`.

- Result: Best performance used `learning_rate=1.0`, with the model reaching peak accuracy early at `10` estimators. Test accuracy was `80.4%`, slightly below the Random Forest model, suggesting boosting offered limited gains on this small tabular dataset.

- What I learned: AdaBoost improves weak learners sequentially by focusing on previous mistakes, but more estimators did not improve results here. This indicates the Titanic dataset’s useful signal was captured quickly, while Random Forest remained more robust overall.