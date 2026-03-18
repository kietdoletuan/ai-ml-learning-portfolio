import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(BASE_DIR, 'data/Sales.csv')

df = pd.read_csv(df_path)

conn = sqlite3.connect(':memory:')
df.to_sql('sales', conn, index = False, if_exists = 'replace')


#Computed Field - Profit Margin

df["profit_margin"] = df["Profit"] / df["Revenue"]

#OVERALL SUMMARY
print('\n=== Step 3: OVERALL SUMMARY ===')
print('\n= Pandas =')
#pandas
print(df[['Revenue', 'Profit']]
      .agg(['count', 'mean', 'min', 'max']))

#SQL
print('\n= SQL =')
print(pd.read_sql("""
    SELECT COUNT(*) as n,
           AVG(Revenue) as avg_revenue,
           MIN(Revenue) as min_revenue,
           MAX(Revenue) as max_revenue,
           AVG(Profit) as avg_profit,
           MIN(Profit) as min_profit,
           MAX(Profit) as max_profit
    FROM sales;
""", conn))

#GROUP BY PRODUCT_CATEGORY
print('\n=== Step 4: BY PRODUCT_CATEGORY ===')
print('\n= Pandas =')
print(df
      .groupby('Product_Category')
      .agg(
          total_revenue = ('Revenue', 'sum'),
          total_profit = ('Profit', 'sum'),
          total_orders_count = ('Order_Quantity', 'sum'),
          average_profit_margin = ('profit_margin', 'mean')
      )
      .query(
          'average_profit_margin > 0'
      )
      .sort_values('total_revenue', ascending = False)
)

print('\n= SQL =')
print(pd.read_sql("""
    SELECT  Product_Category,
            SUM(Revenue) as total_revenue,
            SUM(Profit) as total_profit,
            SUM(Order_Quantity) as total_orders_count,
            AVG(Profit * 1.0 / Revenue) as average_profit_margin
    FROM sales
    GROUP BY Product_Category
    HAVING AVG(Profit * 1.0 / Revenue) > 0
    ORDER BY total_revenue DESC;
""", conn))


#GROUP BY COUNTRY 
print('\n=== Step 5: BY COUNTRY ===')
print('\n= Pandas =')
print(df
      .groupby('Country')
      .agg(
          total_revenue = ('Revenue', 'sum'),
          total_profit = ('Profit', 'sum'),
          total_orders_count = ('Order_Quantity', 'sum')
      )
      .sort_values('total_revenue', ascending = False)
)

print('\n= SQL =')
print(pd.read_sql("""
    SELECT  Country,
            SUM(Revenue) as total_revenue,
            SUM(Profit) as total_profit,
            SUM(Order_Quantity) as total_orders_count
    FROM sales
    GROUP BY Country
    ORDER BY total_revenue DESC;
""", conn))

#YEAR TREND
print('\n=== Step 6: YEAR TREND ===')
print('\n= Pandas =')
print(df
      .groupby('Year')
      .agg(
          average_revenue = ('Revenue', 'mean'),
          average_profit = ('Profit', 'mean')
      )
      .sort_values('Year')
)

print('\n= SQL =')
print(pd.read_sql("""
    SELECT  Year,
            AVG(Revenue) as average_revenue,
            AVG(Profit) as average_profit
    FROM sales
    GROUP BY Year
    ORDER BY YEAR ASC;
""", conn))

#GROUP BY PRODUCT_CATEGORY + YEAR
print('\n=== Step 7: PRODUCT_CATEGORY X YEAR ===')
print('\n= Pandas =')
print(df
      .groupby(['Year', 'Product_Category'])
      .agg(
          total_revenue = ('Revenue', 'sum'),
      )
      .sort_values(by = ['Year', 'total_revenue'], ascending = [True, False])
)

print('\n= SQL =')
print(pd.read_sql("""
    SELECT  Year,
            Product_Category,
            SUM(Revenue) as total_revenue
    FROM sales
    GROUP BY Year, Product_Category
    ORDER BY YEAR ASC, total_revenue DESC
""", conn))

conn.close()