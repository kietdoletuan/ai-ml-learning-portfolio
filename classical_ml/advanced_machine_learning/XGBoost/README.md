# XGBoost Titanic Survival Classifier

Predicts passenger survival (0/1) on the Kaggle Titanic dataset using XGBoost gradient boosting.

**How it was built:** Trained XGBClassifier on cleaned Titanic data with engineered features (Family, IsAlone, log-Fare). Used early stopping with a 64/16/20 train/val/test split to find optimal tree count automatically. Conducted a 3×3 hyperparameter grid over learning_rate (0.01, 0.1, 0.3) and max_depth (3, 5, 7) with all experiments tracked in a results DataFrame.

**The result:** Best combination was lr=0.01, max_depth=7 with 193 trees (early stopping). Test accuracy 83.2%, marginally above tuned Random Forest (82.6%). The gap is small because Titanic is a low-complexity tabular dataset — both algorithms converge to similar decision boundaries given enough tuning.

**What I learned:** Lower learning rate requires significantly more trees but generalizes better; lr=0.01 needed 193 rounds vs 7 rounds at lr=0.3. Corrupted feature engineering (IsAlone defined incorrectly) produced exactly zero feature importance, not just low importance, demonstrating that XGBoost completely ignores non-signal features rather than assigning them small weights.