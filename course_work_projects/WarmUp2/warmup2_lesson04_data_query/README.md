## Retail Profitability Audit

**What it does:** Audits 113k bike store transactions to expose real
profitability contradictions: Caps and Jerseys are loss-making despite
low prices; Road Bikes drive 33M revenue but sit at only 29% margin;
accessories like Socks earn 63% margins at a fraction of the volume.
Five targeted queries investigate losses, margin gaps, product category
splits, a 2015 Australia revenue spike, and demographic revenue patterns.

**How it was built:** Python with pandas and sqlite3. Each query runs
in both engines for direct comparison. Covers: IS NULL, BETWEEN, LIKE,
DISTINCT, LIMIT/OFFSET, COALESCE, and CASE WHEN. Computed field
(profit_margin = Profit / Revenue) used throughout.

**Result:** 58 loss-making transactions identified, all from Caps and
Jerseys. Margin range: 13% (Caps) to 63% (Socks). Australia 2015
revenue doubled vs 2014. Senior customers transact at half the average
revenue of Young Adults.

- Dataset: Kaggle - Bike Sales in Europe
https://www.kaggle.com/datasets/prepinstaprime/europe-bike-store-sales
(CSV not committed)
