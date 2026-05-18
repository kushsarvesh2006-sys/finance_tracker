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
        conn.commit()
        st.success("Transaction Added Successfully!")
        st.rerun()

# ---------------- DASHBOARD ----------------

if page == "Dashboard":

    st.subheader("Transaction Data")

    if df.empty:
        st.warning("No transactions added yet.")

    else:

        df["Date"] = pd.to_datetime(df["Date"],errors="coerce")
        df["Month"] = df["Date"].dt.month_name()

        df = df.dropna(subset=["Month"])

        month_list = list(df["Month"].unique())

        selected_month = st.selectbox(
            "Select Month",
            month_list
        )

        df = df[df["Month"] == selected_month]
        

        category_list = ["All"]

        if not df.empty:
            category_list += list(df["Category"].dropna().unique())

        selected_category = st.selectbox(
            "Select Category",
            category_list
        )

        if selected_category != "All":
            df = df[df["Category"] == selected_category]

        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Report CSV",
            data=csv,
            file_name="finance_report.csv",
            mime="text/csv"
        )


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

        st.subheader("Savings Goal Progress")

        savings_goal = 50000

        progress = max(0,savings / savings_goal)

        st.progress(min(progress, 1.0))

        st.write(f"Goal: ₹{savings_goal}")

        st.write(f"Current Savings: ₹{savings}")

        st.write(f"Progress: {progress:.0%}")

        

        # Category Expense
        category_expense = df.groupby("Category")["Amount"].sum()

        st.subheader("Category Wise Expense")

        chart_data = category_expense.reset_index()

        chart_data.columns = ["Category", "Amount"]

        st.bar_chart(
            data=chart_data,
            x="Category",
            y="Amount"
        )

        st.subheader("Expense Distribution")

        pie_data = df[df["Type"] == "Expense"]

        if not pie_data.empty:

            pie_chart = pie_data.groupby("Category")["Amount"].sum()

            st.pyplot(
                pie_chart.plot.pie(
                    autopct="%1.1f%%",
                    figsize=(2.5, 2.5)
                ).figure
            )

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

        st.subheader("Edit Transaction")

        edit_index = st.selectbox(
            "Select Transaction To Edit",
            df.index,
            key="edit_select"
        )

        updated_amount = st.number_input(
            "Updated Amount",
            min_value=0,
            key="updated_amount"
        )

        if st.button("Update Transaction"):

            conn.execute(
                "UPDATE transactions SET Amount = ? WHERE rowid = ?",
                (updated_amount, edit_index + 1)
            )

            conn.commit()

            st.success("Transaction Updated Successfully!")

            st.rerun()