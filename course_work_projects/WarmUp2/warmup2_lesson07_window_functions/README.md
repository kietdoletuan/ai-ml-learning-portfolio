## What it does: 
Aggregates 113k raw bike store transactions into a product-month table, then applies five window function patterns — row numbering, lag/delta, moving average, running total, and within-category ranking — to track per-product revenue performance over time.

## How it was built: 
Pandas groupby aggregation reduces raw transaction grain to monthly product-level data. Window operations use groupby combined with cumcount, shift, rolling with reset_index, cumsum, and rank with method="min". Stretch goal replicates all window logic in SQLite and validates output parity using pd.testing.assert_frame_equal.

## The result: 
Each product-month row carries six derived features. Top-2 products per category are filtered with correct tie handling. Each product in the top-2 is flagged as revenue-growing or revenue-declining based on its most recent month-over-month delta.