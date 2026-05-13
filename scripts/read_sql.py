import pandas as pd
import sqlite3

# Connect database
conn = sqlite3.connect("../database/finance.db")

# Read SQL table
df = pd.read_sql("SELECT * FROM transactions", conn)

# Show data
print(df)

# Total expense
print("\nTotal Expense =", df["Amount"].sum())

# Category-wise expense
print("\nCategory Wise Expense:")
print(df.groupby("Category")["Amount"].sum())

# Close connection
conn.close()