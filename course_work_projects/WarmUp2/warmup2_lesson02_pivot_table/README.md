## Europe Bike Store Sales — Validate + Pivot Dashboard

**What it does:** Two-part project. Python validation script confirms 
data quality on 113k-row Kaggle dataset. Excel Pivot Table dashboard 
answers 4 business questions on the validated data.

**Dataset:** Europe Bike Store Sales — Kaggle 
(prepinstaprime/europe-bike-store-sales). Pre-cleaned by uploader.

**Part 1 — Python:** pandas validation pipeline checking nulls, 
negative values, duplicates, and categorical format consistency 
across key columns. Zero nulls, zero negative revenue rows confirmed. 
~1000 duplicate rows flagged, likely legitimate repeat transactions 
given absence of unique transaction ID column.

**Part 2 — Excel:** 4 pivot tables using % of Parent Row Total, 
cross-tabulation, % of Row Total, and Difference From (previous) 
for MoM trend analysis. Slicer linked to country/year cross-tab.

Data Source: https://www.kaggle.com/datasets/prepinstaprime/europe-bike-store-sales
