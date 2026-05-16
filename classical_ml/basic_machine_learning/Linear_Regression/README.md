# Linear Regression from Scratch

## What it does
- Predicts continuous value by fitting a line of best fit to the data provided.
- Deployed the model on California Housing Prices Dataset, measuring its RMSE.

## How it was built
- Weight and Bias are initialized to 0 before being used to calculate an initial prediction and loss. By converging the loss function through gradient descent, the line of best fit is found

## Results:
- Model's RMSE was roughly 0.7447, while sklearn's linear regression model's RMSE was 0.7456


## What I learned:
- How gradient descent reduces loss
- Importance of normalization and risks of data leakage associated with it
- Further understanding of matrices operations with numpy