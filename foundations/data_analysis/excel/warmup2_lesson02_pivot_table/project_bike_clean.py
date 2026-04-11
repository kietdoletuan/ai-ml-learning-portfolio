import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sales_data_path = os.path.join(BASE_DIR, "data/europe_bike_sales.csv")

output_excel_path = os.path.join(BASE_DIR,"europe_bike_sales_cleaned.xlsx")

try:
    sales_df = pd.read_csv(sales_data_path)

    print("-" * 100)
    print("Basic information and first 5 rows")
    print(sales_df.head(5))
    print(sales_df.info())

    print("-" * 100)
    print("Checking for incorrect format values")
    print(sales_df["Country"].unique())
    print(sales_df["Month"].unique())

    print("-" * 100)
    print("Checking for nulls")
    print(sales_df.isnull().sum())

    print(f'\nNumber of rows for Revenue that is negative: {sales_df[sales_df["Revenue"] < 0].shape[0]}\n')
    print(f'\nNumber of rows for Cost that is negative: {sales_df[sales_df["Cost"] < 0].shape[0]}\n')

    print("Checking for duplicates:")
    print(sales_df.duplicated().sum())

    sales_df.to_excel(output_excel_path, sheet_name = "Sales", index = False)

except FileNotFoundError:
    print(f"Error: The file was not found at {sales_data_path}")
    exit()
