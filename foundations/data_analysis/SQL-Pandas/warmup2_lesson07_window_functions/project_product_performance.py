import pandas as pd
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df_path = os.path.join(BASE_DIR, 'data/Sales.csv')

df_raw = pd.read_csv(df_path)
df = df_raw.copy().drop_duplicates()

df['Parsed_Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
df['Period'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')


df = df.drop(columns = ['Date'])


df = df.sort_values(["Parsed_Date"])


# Fix dirty product categories
dominant_category = (
    df.groupby(['Product', 'Product_Category'])
    .size()
    .reset_index(name='count')
    .sort_values('count', ascending=False)
    .drop_duplicates(subset='Product', keep='first')
    .set_index('Product')['Product_Category']
)
df['Product_Category'] = df['Product'].map(dominant_category)

df_monthly = df.groupby(['Product', 'Product_Category', 'Period']).agg(
    Total_Revenue = ('Revenue', 'sum'),
    Total_Profit =  ('Profit', 'sum'),
    Total_Quantity =  ('Order_Quantity', 'sum')
).reset_index()

df_monthly = df_monthly.sort_values(['Product', 'Period'])

df_monthly["Row_Num"] = df_monthly.groupby(['Product', 'Product_Category']).cumcount() + 1

df_monthly['Previous_Revenue'] = df_monthly.groupby(['Product', 'Product_Category'])['Total_Revenue'].shift(1)

df_monthly['Revenue_Delta'] = df_monthly['Total_Revenue'] - df_monthly['Previous_Revenue']

df_monthly['MA3_Revenue'] = (df_monthly
    .groupby(['Product', 'Product_Category'])['Total_Revenue']
    .rolling(3, min_periods=1)
    .mean()
    .reset_index(level = [0, 1], drop = True)
)

df_monthly['Running_Total_Revenue'] = df_monthly.groupby(['Product', 'Product_Category'])['Total_Revenue'].cumsum()

df_monthly['Rank'] = (df_monthly
    .groupby(['Product_Category', 'Period'])['Total_Revenue']
    .rank(ascending = False, method = 'min')
)
print("Top 2 per category")
product_total = (
    df_monthly.groupby(['Product', 'Product_Category'])['Total_Revenue']
    .sum()
    .reset_index(name='Lifetime_Revenue')
)

top2_products = (
    product_total
    .sort_values(['Product_Category', 'Lifetime_Revenue'], ascending=[True, False])
    .groupby('Product_Category', group_keys=False)
    .head(2)
)

print(top2_products)

top2_list = top2_products['Product'].tolist()

trend = (
    df_monthly[df_monthly['Product'].isin(top2_list)]
    .sort_values(['Product', 'Period'])
    .groupby('Product')
    .last()
    .reset_index()
    [['Product', 'Product_Category', 'Period', 'Revenue_Delta']]
)

trend['Trend'] = trend['Revenue_Delta'].apply(lambda x: 'Growing' if x > 0 else 'Declining')

print(trend[['Product', 'Product_Category', 'Trend', 'Revenue_Delta']])

