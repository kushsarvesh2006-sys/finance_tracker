import pandas as pd

# Excel file read
df = pd.read_excel("../data/expenses.xlsx")

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

# Show data
print(df)

# Total expense
print("\nTotal Expense =", df["Amount"].sum())