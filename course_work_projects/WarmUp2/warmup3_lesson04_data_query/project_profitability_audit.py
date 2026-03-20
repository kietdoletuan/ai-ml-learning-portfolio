import os
import sqlite3
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(BASE_DIR, 'data/Sales.csv')

df_raw = pd.read_csv(df_path)
df = df_raw.copy()

conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index = False, if_exists = 'replace')

print("=== QUERY 1: LOSS-MAKING TRANSACTIONS ===")
print("pandas:\n")
print(df[df['Profit'] < 0])

print("SQL:\n")
print(pd.read_sql("""
    SELECT  *
    FROM sales
    WHERE   PROFIT < 0
""", conn))
print("Observation: losses are concentrated in Yveline, France. Only two products are making a loss throughout the years (AWC Logo Cap and Short-Sleeve Classic Jersey of various sizes) belonging to the sub category Caps and Jerseys respectively")

print("\n=== QUERY 2: Profit-Margin - Top 5 vs Bot 5 ===")

df["profit_margin"] = df["Profit"] / df["Revenue"]

margin_by_sub = (df
    .groupby('Sub_Category')
    .agg(
        total_profit_margin = ('profit_margin', 'mean')
    )
    .reset_index()
    .sort_values('total_profit_margin', ascending = False)
)

print("=== pandas top 5")
print(margin_by_sub.head(5))
print("=== pandas bot 5")
print(margin_by_sub.tail(5))

print("=== SQL top 5")
print(pd.read_sql("""
    SELECT  Sub_Category,
            AVG(1.0 * Profit / Revenue) AS profit_margin
    FROM sales
    GROUP BY Sub_Category
    ORDER BY profit_margin 
    LIMIT 5  
""", conn))

print("=== SQL bot 5")
print(pd.read_sql("""
    SELECT  Sub_Category,
            AVG(1.0 * Profit / Revenue) AS profit_margin
    FROM sales
    GROUP BY Sub_Category
    ORDER BY profit_margin ASC
    LIMIT 5  
""", conn))

print("\n=== QUERY 3: BIKE vs NON-BIKE REVENUE ===")

bike = df[df['Sub_Category'].str.contains('Bike')]
non_bike = df[~df['Sub_Category'].str.contains('Bike')]

print(f"Bike transactions: {len(bike)} | Total revenue: {bike['Revenue'].sum():,}")
print(f"Non-Bike:          {len(non_bike)} | Total revenue: {non_bike['Revenue'].sum():,}")

print(pd.read_sql("""
    SELECT
        CASE WHEN Sub_Category LIKE '%Bike%' THEN 'Bike' ELSE 'Non-Bike' END AS classification,
        COUNT(*) AS transactions,
        SUM(Revenue) AS total_revenue
    FROM sales
    GROUP BY classification
""", conn))

print("=== QUERY 4: AUSTRALIA 2015 SPIKE ===")
au_2014 = (
    df[(df['Country'] == 'Australia') & (df['Year'] == 2014)]
    .groupby('Sub_Category')
    .agg(rev_2014=('Revenue', 'sum'))
    .reset_index()
)

au_2015 = (
    df[(df['Country'] == 'Australia') & (df['Year'] == 2015)]
    .groupby('Sub_Category')
    .agg(rev_2015=('Revenue', 'sum'))
    .reset_index()
)

side_by_side = (
    au_2014
    .merge(au_2015, on='Sub_Category', how='outer')
    .sort_values('rev_2015', ascending=False)
)
print(side_by_side)
print("\n\n")
print(pd.read_sql("""
    WITH au_2014 AS (
        SELECT  Sub_Category,
                SUM(Revenue) as rev_2014
        FROM sales
        WHERE Year = 2014 AND Country = 'Australia'
        GROUP BY Sub_Category 
    ),
    au_2015 AS (
        SELECT  Sub_Category,
                SUM(Revenue) as rev_2015
        FROM sales
        WHERE Year = 2015 AND Country = 'Australia'
        GROUP BY Sub_Category 
    )
    SELECT  au_2014.Sub_Category,
            rev_2014,
            rev_2015
    FROM au_2014
    JOIN au_2015 ON au_2014.Sub_Category = au_2015.Sub_Category
    ORDER BY rev_2014 DESC, rev_2015 DESC 
""", conn))

print("=== QUERY 5: SENIOR HIGH-REVENUE TRANSACTIONS ===")
seniors = (
    df[(df['Age_Group'] == 'Seniors (64+)') & (df['Revenue'] > 500)]
    [['Country', 'Sub_Category', 'Revenue', 'Profit', 'Customer_Gender']]
)

seniors['revenue_band'] = np.where(seniors['Revenue'] >= 1000, 'High', 'Standard')
print(seniors.sort_values('Revenue', ascending=False))


print(pd.read_sql("""
    SELECT Country,
           Sub_Category,
           Revenue,
           Profit,
           Customer_Gender,
           CASE WHEN Revenue >= 1000 THEN 'High' ELSE 'Standard' END AS revenue_band
    FROM sales
    WHERE Age_Group = 'Seniors (64+)'
    AND Revenue > 500
    ORDER BY Revenue DESC
""", conn))