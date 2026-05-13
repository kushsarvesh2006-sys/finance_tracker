import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Connect database
conn = sqlite3.connect("../database/finance.db")

# Read data
df = pd.read_sql("SELECT * FROM transactions", conn)

# Category-wise expense
category_expense = df.groupby("Category")["Amount"].sum()

# Create pie chart
plt.pie(category_expense, labels=category_expense.index, autopct='%1.1f%%')

# Title
plt.title("Expense Distribution")

# Show chart
plt.show()

# Close database
conn.close()