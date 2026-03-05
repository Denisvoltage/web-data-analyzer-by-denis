import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import bcrypt
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Data Intelligence Platform", layout="wide")

# ---------------- DATABASE ----------------
conn = sqlite3.connect("data_platform.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password BLOB
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    report_time TEXT
)
""")

conn.commit()

# ---------------- AUTH FUNCTIONS ----------------
def register_user(username, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    if result:
        if bcrypt.checkpw(password.encode(), result[0]):
            return True
    return False

def save_report(username):
    now = str(datetime.datetime.now())
    cursor.execute("INSERT INTO reports (username, report_time) VALUES (?, ?)", (username, now))
    conn.commit()

def get_reports(username):
    cursor.execute("SELECT report_time FROM reports WHERE username=?", (username,))
    return cursor.fetchall()

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "bi_df" not in st.session_state:
    st.session_state.bi_df = None
if "bi_report" not in st.session_state:
    st.session_state.bi_report = None

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.logged_in:

    st.title("🚀 Data Intelligence Platform")

    option = st.radio("Choose Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register":
        if st.button("Create Account"):
            if register_user(username, password):
                st.success("Account created successfully.")
            else:
                st.error("Username already exists.")

    if option == "Login":
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials.")

    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.success(f"Logged in as: {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.radio(
    "Navigation",
    ["Executive Dashboard", "Interactive BI Tool", "Report History"]
)

# =====================================================
# ---------------- EXECUTIVE DASHBOARD ----------------
# =====================================================
if menu == "Executive Dashboard":

    st.title("📊 Executive Analytics Dashboard")

    uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        if not numeric_df.empty:

            best_column = numeric_df.mean().idxmax()

            st.subheader("Key Performance Visualization")
            fig = px.bar(df, x=best_column)
            st.plotly_chart(fig, use_container_width=True)

            commentary = f"""
This dataset contains {df.shape[0]} records and {df.shape[1]} columns.
The strongest metric appears to be '{best_column}' based on highest average.
"""

            st.subheader("Executive Commentary")
            st.info(commentary)

            if st.button("Generate Executive PDF Report"):

                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()

                elements.append(Paragraph("Executive Data Intelligence Report", styles["Heading1"]))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"Generated by: {st.session_state.user}", styles["Normal"]))
                elements.append(Paragraph(f"Date: {datetime.datetime.now()}", styles["Normal"]))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(commentary, styles["Normal"]))

                doc.build(elements)
                buffer.seek(0)

                save_report(st.session_state.user)

                st.download_button(
                    "Download Executive PDF",
                    buffer,
                    "Executive_Report.pdf",
                    mime="application/pdf"
                )

# =====================================================
# ---------------- INTERACTIVE BI TOOL ----------------
# =====================================================
if menu == "Interactive BI Tool":

    st.title("📊 Interactive BI Tool")

    uploaded_file = st.file_uploader("Select CSV or Excel File", type=["csv", "xlsx"])

    if st.button("Read File"):

        if uploaded_file is None:
            st.error("Please select a file first.")
        else:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.session_state.bi_df = df
                st.session_state.bi_report = None
                st.success("File read successfully.")

            except Exception as e:
                st.error(f"Error reading file: {e}")

    if st.session_state.bi_df is not None:

        df = st.session_state.bi_df

        col1, col2 = st.columns(2)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])

        st.write("### Column Headings")
        st.write(list(df.columns))

        text_columns = df.select_dtypes(include=["object"]).columns.tolist()
        numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()

        if text_columns and numeric_columns:

            group_col = st.selectbox("Group By Column", text_columns)
            agg_method = st.selectbox(
                "Aggregation Method",
                ["sum", "mean", "max", "min", "count", "median"]
            )
            value_col = st.selectbox("Value Column", numeric_columns)

            if st.button("Preview Report"):

                report = df.groupby(group_col)[value_col].agg(agg_method).reset_index()
                report = report.sort_values(by=value_col, ascending=False)

                st.session_state.bi_report = report
                st.success("Report generated successfully.")

    if st.session_state.bi_report is not None:

        report = st.session_state.bi_report

        st.subheader("Report Output")
        st.dataframe(report, use_container_width=True)

        export_format = st.selectbox("Select Export Format", ["Excel (.xlsx)", "CSV (.csv)"])

        if export_format == "Excel (.xlsx)":
            buffer = BytesIO()
            report.to_excel(buffer, index=False)
            buffer.seek(0)
            st.download_button("Download Excel", buffer, "BI_Report.xlsx")
        else:
            buffer = BytesIO()
            report.to_csv(buffer, index=False)
            buffer.seek(0)
            st.download_button("Download CSV", buffer, "BI_Report.csv")

        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart"])

        if st.button("Preview Chart"):

            if chart_type == "Bar Chart":
                fig = px.bar(report, x=report.columns[0], y=report.columns[1])
            elif chart_type == "Line Chart":
                fig = px.line(report, x=report.columns[0], y=report.columns[1])
            else:
                fig = px.pie(report, names=report.columns[0], values=report.columns[1])

            st.plotly_chart(fig, use_container_width=True)
            st.info("PNG export disabled in cloud version for stability.")

# =====================================================
# ---------------- REPORT HISTORY ----------------
# =====================================================
if menu == "Report History":

    st.title("📂 Report History")

    reports = get_reports(st.session_state.user)

    if reports:
        for r in reports:
            st.write("Generated on:", r[0])
    else:
        st.info("No reports generated yet.")

st.caption("Enterprise Ready | Built by Denis")
