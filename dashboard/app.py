import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("Personal Finance Tracker")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Transaction"]
)

if not os.path.exists("database"):
    os.makedirs("database")

conn = sqlite3.connect("database/finance.db")

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

df = pd.read_sql("SELECT * FROM transactions", conn)

# ---------------- ADD TRANSACTION ----------------

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

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.subheader("Transaction Data")

    if df.empty:
        st.warning("No transactions added yet.")

    else:

        st.dataframe(df)

        income = df[df["Type"] == "Income"]["Amount"].sum()

        expense = df[df["Type"] == "Expense"]["Amount"].sum()

        savings = income - expense

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Income", f"₹{income}")

        with col2:
            st.metric("Total Expense", f"₹{expense}")

        with col3:
            st.metric("Total Savings", f"₹{savings}")

        # Category Expense
        category_expense = df.groupby("Category")["Amount"].sum()

        st.subheader("Category Wise Expense")

        st.bar_chart(category_expense)

        st.subheader("Delete Transaction")

        transaction_index = st.selectbox(
            "Select Transaction Index",
            df.index
        )

        if st.button("Delete Transaction"):

            conn.execute(
                "DELETE FROM transactions WHERE rowid = ?",
                (transaction_index + 1,)
            )

            conn.commit()

            st.success("Transaction Deleted Successfully!")

            st.rerun()