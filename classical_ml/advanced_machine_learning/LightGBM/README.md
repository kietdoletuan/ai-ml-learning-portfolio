# LightGBM Titanic Survival Classifier

Predicts passenger survival (0/1) on the Kaggle Titanic dataset using LGBM.

**How it was built:** Trained LGBMClassifier on cleaned Titanic data with engineered features (Family, IsAlone, log-Fare). Used default settings throughout with computed SHAP values, which show per-prediction attribution, and interpreted the results

**The result:** Test accuracy: 82.1%, marginally below tuned XGBoost. Despite its speed advantage, it only appears at scale so a small dataset such as this could actually make it slower than XGBoost's exact method.

**What I learned:** 
- According to SHAP, Sex is more important than Pclass. Sex produces SHAP values ranging from -2 to +4 while Pclass ranges from -2 to +1.5. Fare shows a positive relationship with survival but with high variance due to its correlation with Pclass.

- Plot 1 (correctly predicted survived): Age (+2.66) and female Sex (+2.09) were the dominant survival signals, with Pclass 2 adding further positive contribution — a young female in second class had overwhelming survival probability.

- Plot 2 (correctly predicted died): Male Sex (-1.79) was the single dominant factor pushing toward death, partially offset by Age (+0.83) and Family (+0.24) — the model correctly identified this passenger as high mortality risk despite some mitigating features.

- Plot 3 (incorrectly predicted — model predicted died, actual survived): Sex (-1.26) and Fare (-1.0) both pushed strongly toward death prediction, while Embarked_C (+0.59) partially offset — the model failed because this passenger's profile (male, low-ish fare, 3rd class) statistically maps to low survival, but they were an exception.
