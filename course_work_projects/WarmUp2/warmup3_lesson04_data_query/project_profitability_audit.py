import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(BASE_DIR, 'data/Sales.csv')

df = pd.read_csv(df_path)
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

print("pandas top 5")
print(df
    .sort_values('profit_margin', ascending = False)
    .head(5)      
)
print("pandas bot 5")
print(df
    .sort_values('profit_margin', ascending = True)
    .head(5)      
)

