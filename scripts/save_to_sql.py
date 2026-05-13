import pandas as pd
import sqlite3

# Read Excel
df = pd.read_excel("../data/expenses.xlsx")

# Clean column names
df.columns = df.columns.str.strip()

# Connect database
conn = sqlite3.connect("../database/finance.db")

# Save table
df.to_sql("transactions", conn, if_exists="replace", index=False)

print("Data saved successfully to SQL database!")

# Close connection
conn.close()