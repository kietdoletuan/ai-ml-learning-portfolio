# Mall Customer Segmentation
- Segments 200 mall customers into behavioral clusters using from-scratch K-Means.
- Dataset: Mall_Customers.csv — 200 rows. Dropped CustomerID and Gender. Features: Age, Annual Income, Spending Score.
- Implementation: Random centroid initialization, assign-update loop (max 200 iterations, early stop on convergence). Distance computed via vectorized NumPy broadcasting. WCSS tracked via inertia().
- Results: Elbow at k=5. Five segments map to premium, conservative, mid-tier, impulsive, and budget customer types.