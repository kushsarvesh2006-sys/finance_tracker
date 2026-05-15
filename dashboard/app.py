import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# Title
st.title("Personal Finance Tracker")

# Sidebar Navigation

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Transaction"]
)

# Create database folder if not exists
if not os.path.exists("../database"):
    os.makedirs("../database")

# Database connection
conn = sqlite3.connect("../database/finance.db")

# Create table if not exists
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    Date TEXT,
    Category TEXT,
    Amount REAL,
    Payment_Mode TEXT,
    Type TEXT
)
""")

conn.commit()

# Read data
df = pd.read_sql("SELECT * FROM transactions", conn)

if df.empty:
    st.warning("No transactions added yet.")
    

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"], format="mixed")

# Create Month column
df["Month"] = df["Date"].dt.month_name()

# Month Selection

selected_month = st.selectbox(
    "Select Month",
    df["Month"].unique()
)

# Filter data by month
df = df[df["Month"] == selected_month]


# Show table
if page == "Dashboard":
    st.subheader("Transaction Data")
    st.dataframe(df)

# Income and Expense Calculation

income = df[df["Type"] == "Income"]["Amount"].sum()

expense = df[df["Type"] == "Expense"]["Amount"].sum()

savings = income - expense

# Show metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Income", f"₹{income}")

with col2:
    st.metric("Total Expense", f"₹{expense}")

with col3:
    st.metric("Total Savings", f"₹{savings}")

# Savings Goal Tracker

savings_goal = 100000

progress = max(0, savings / savings_goal)

st.subheader("Savings Goal Progress")

st.progress(min(progress, 1.0))

st.write(f"Goal: ₹{savings_goal}")

st.write(f"Current Savings: ₹{savings}")

st.write(f"Progress: {progress:.0%}")

# Budget Warning

budget_limit = 10000

if expense > budget_limit:
    st.error("⚠️ Warning: Monthly budget exceeded!")

else:
    st.success("✅ Budget is under control")

# Category-wise expense
category_expense = df.groupby("Category")["Amount"].sum()

# Pie chart
fig, ax = plt.subplots()
ax.pie(category_expense, labels=category_expense.index, autopct='%1.1f%%')
ax.set_title("Expense Distribution")

# Show chart
st.pyplot(fig)


# Bar Chart

st.subheader("Category Wise Expense")

fig2, ax2 = plt.subplots()

ax2.bar(
    category_expense.index,
    category_expense.values
)

ax2.set_xlabel("Category")

ax2.set_ylabel("Amount")

ax2.set_title("Expenses by Category")

st.pyplot(fig2)


if page == "Add Transaction":
    st.subheader("Add New Transaction")

    date = st.date_input("Select Date")

    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Shopping", "Bills"]
    )

    amount = st.number_input(
        "Amount",
        min_value=0
    )

    payment = st.selectbox(
        "Payment Mode",
        ["UPI", "Cash", "Card"]
    )

    transaction_type = st.selectbox(
        "Type",
        ["Expense", "Income"]
    )

    if st.button("Add Transaction"):

        new_data = pd.DataFrame({
            "Date": [str(date)],
            "Category": [category],
            "Amount": [amount],
            "Payment_Mode": [payment],
            "Type": [transaction_type]
        })

        new_data.to_sql(
            "transactions",
            conn,
            if_exists="append",
            index=False
        )

        st.success("Transaction Added Successfully!")
 # Download Excel Report

excel_data = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Excel Report",
    data=excel_data,
    file_name='finance_report.csv',
    mime='text/csv'
)

# Delete Transaction

st.subheader("Delete Transaction")

transaction_list = df.index.tolist()

selected_index = st.selectbox(
    "Select Transaction Index to Delete",
    transaction_list
)

# Edit Transaction

st.subheader("Edit Transaction")

edit_index = st.selectbox(
    "Select Transaction Index to Edit",
    df.index.tolist()
)

new_amount = st.number_input(
    "New Amount",
    min_value=0,
    key="edit_amount"
)

if st.button("Update Transaction"):

    conn.execute(
        "UPDATE transactions SET Amount = ? WHERE rowid = ?",
        (new_amount, edit_index + 1)
    )

    conn.commit()

    st.success("Transaction Updated Successfully!")


if st.button("Delete Transaction"):

    conn.execute(
        "DELETE FROM transactions WHERE rowid = ?",
        (selected_index + 1,)
    )

    conn.commit()

    st.success("Transaction Deleted Successfully!")