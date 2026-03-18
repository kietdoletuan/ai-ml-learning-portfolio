## Supply Chain Performance Analysis

**What it does:** Analyzes 113,000+ bike store transactions across 6 countries
and 6 years using pandas and SQL (sqlite3), producing grouped summaries by
product category, country, year, and category-year combinations.

**How it was built:** Python with pandas and sqlite3. Computed field
(profit_margin = Profit / Revenue) created before aggregation. Each of the 5
analysis steps runs twice - once in pandas groupby/agg, once in raw SQL via
pd.read_sql() - outputs compared side by side. Stretch goal adds a HAVING
filter removing segments with negative average profit margin.

**Result:** 5 paired output tables. Bikes drive the highest total revenue.
United States and Australia lead by country. Clear upward revenue trend from
2011 to 2016. Some sub-segments show negative profit margins.

Dataset: Kaggle - Bike Sales in Europe
https://www.kaggle.com/datasets/prepinstaprime/europe-bike-store-sales
(CSV not committed - download Sales.csv and place in data/ folder)
