# California Housing Price Regressor 
- Predicts median house prices using a from-scratch Decision Tree regressor, validated against sklearn.
- Dataset: housing.csv — 20,640 rows, first 2,000 used (80/20 split). Filled missing total_bedrooms with median. One-hot encoded ocean_proximity. Engineered RoomPerPerson, IncPerAge, RoomPerHouse, BedroomPercentage.
- Implementation: Variance reduction (MSE) as the split criterion. Leaf nodes output partition mean. Matched against sklearn's DecisionTreeRegressor (max_depth=5).
- Results: Custom RMSE ~47,773 / MAE ~35,463 — sklearn RMSE ~47,580 / MAE ~35,679. Median income dominant feature. Overfitting gap widens past depth 5.
