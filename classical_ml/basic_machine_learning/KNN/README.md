# Iris Species Classifier
- Classifies iris flowers into three species using a from-scratch KNN classifier.
- Dataset: Iris.csv — 150 rows, 4 features. 80/20 split. Features standardized on training statistics only.
- Implementation: Euclidean distance to all training points, sorted via argsort, majority label among k=5 neighbors. Decision boundary visualized on petal features via mesh grid.
- Results: 100% accuracy on test set. Accuracy-vs-k plotted for k=1–29. Setosa cleanly isolated; versicolor/virginica boundary fuzzy but correctly classified at k=5.