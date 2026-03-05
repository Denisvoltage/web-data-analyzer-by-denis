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

st.set_page_config(page_title="Corporate Data Analyzer by Denis", layout="wide")

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
        return bcrypt.checkpw(password.encode(), result[0])
    return False


def save_report(username):
    now = str(datetime.datetime.now())
    cursor.execute(
        "INSERT INTO reports (username, report_time) VALUES (?,?)",
        (username, now),
    )
    conn.commit()


def get_reports(username):
    cursor.execute("SELECT report_time FROM reports WHERE username=?", (username,))
    return cursor.fetchall()


# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "df" not in st.session_state:
    st.session_state.df = None

if "report" not in st.session_state:
    st.session_state.report = None


# ---------------- LOGIN PAGE ----------------

if not st.session_state.logged_in:

    st.title("🚀 Corporate Data Analyzer by Denis")

    option = st.radio("Choose Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Register":

        if st.button("Create Account"):

            if register_user(username, password):
                st.success("Account created successfully")
            else:
                st.error("Username already exists")

    if option == "Login":

        if st.button("Login"):

            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid login")

    st.stop()

# ---------------- SIDEBAR ----------------

st.sidebar.success(f"Logged in as: {st.session_state.user}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

menu = st.sidebar.radio(
    "Navigation",
    ["Executive Dashboard", "Interactive BI Tool", "Report History"],
)

# ====================================================
# EXECUTIVE DASHBOARD
# ====================================================

if menu == "Executive Dashboard":

    st.title("📊 Executive Analytics Dashboard")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel", type=["csv", "xlsx"]
    )

    if uploaded_file:

        df = (
            pd.read_csv(uploaded_file)
            if uploaded_file.name.endswith(".csv")
            else pd.read_excel(uploaded_file)
        )

        # KPI CARDS
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())
        col4.metric("Numeric Columns", len(df.select_dtypes(include=['int64','float64']).columns))

        st.divider()

        st.subheader("Dataset Preview")

        st.dataframe(df.head(), use_container_width=True)

        # AUTO DASHBOARD CHARTS

        numeric_cols = df.select_dtypes(include=['int64','float64']).columns
        text_cols = df.select_dtypes(include=['object']).columns

        if len(text_cols) > 0 and len(numeric_cols) > 0:

            chart_data = df.groupby(text_cols[0])[numeric_cols[0]].sum().reset_index()

            chart_data = chart_data.sort_values(by=numeric_cols[0], ascending=False).head(10)

            fig = px.bar(
                chart_data,
                x=text_cols[0],
                y=numeric_cols[0],
                title="Top Categories"
            )

            st.plotly_chart(fig, use_container_width=True)

        if len(numeric_cols) > 0:

            fig2 = px.histogram(
                df,
                x=numeric_cols[0],
                title="Value Distribution"
            )

            st.plotly_chart(fig2, use_container_width=True)

        commentary = f"""
Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.
"""

        st.info(commentary)

        if st.button("Generate Executive PDF Report"):

            buffer = BytesIO()

            doc = SimpleDocTemplate(buffer, pagesize=A4)

            elements = []

            styles = getSampleStyleSheet()

            elements.append(
                Paragraph("Executive Data Report", styles["Heading1"])
            )

            elements.append(Spacer(1, 20))

            elements.append(Paragraph(commentary, styles["Normal"]))

            doc.build(elements)

            buffer.seek(0)

            save_report(st.session_state.user)

            st.download_button(
                "Download PDF",
                buffer,
                "Executive_Report.pdf",
            )

# ====================================================
# INTERACTIVE BI TOOL
# ====================================================

if menu == "Interactive BI Tool":

    st.title("📊 Interactive BI Tool")

    uploaded_file = st.file_uploader(
        "Select CSV or Excel File", type=["csv", "xlsx"]
    )

    if st.button("Read File"):

        if uploaded_file is None:

            st.error("Please select a file")

        else:

            df = (
                pd.read_csv(uploaded_file)
                if uploaded_file.name.endswith(".csv")
                else pd.read_excel(uploaded_file)
            )

            # detect date columns
            for col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass

            st.session_state.df = df
            st.session_state.report = None

            st.success("File loaded successfully")

    if st.session_state.df is not None:

        df = st.session_state.df.copy()

        st.subheader("Dataset Overview")

        col1, col2 = st.columns(2)

        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])

        st.divider()

        # ---------------- FILTERS ----------------

        st.subheader("🔎 Filters")

        text_cols = df.select_dtypes(include="object").columns
        num_cols = df.select_dtypes(include=["int64", "float64"]).columns
        date_cols = df.select_dtypes(include=["datetime64"]).columns

        # TEXT FILTER
        for col in text_cols:

            options = df[col].dropna().unique()

            selected = st.multiselect(col, options)

            if selected:
                df = df[df[col].isin(selected)]

        # NUMERIC FILTER
        for col in num_cols:

            min_val = float(df[col].min())
            max_val = float(df[col].max())

            selected = st.slider(
                f"{col} Range",
                min_val,
                max_val,
                (min_val, max_val),
            )

            df = df[(df[col] >= selected[0]) & (df[col] <= selected[1])]

        # DATE FILTER
        for col in date_cols:

            valid = df[col].dropna()

            if not valid.empty:

                start = valid.min().date()
                end = valid.max().date()

                selected_dates = st.date_input(
                    f"{col} Range",
                    (start, end),
                )

                if isinstance(selected_dates, tuple):

                    start_d, end_d = selected_dates

                    df = df[
                        (df[col] >= pd.to_datetime(start_d))
                        & (df[col] <= pd.to_datetime(end_d))
                    ]

        st.divider()

        # ---------------- REPORT BUILDER ----------------

        st.subheader("📑 Report Builder")

        if len(text_cols) > 0 and len(num_cols) > 0:

            group_col = st.selectbox("Group By Column", text_cols)

            agg = st.selectbox(
                "Aggregation",
                ["sum", "mean", "max", "min", "count", "median"],
            )

            value_col = st.selectbox("Value Column", num_cols)

            if st.button("Preview Report"):

                report = df.groupby(group_col)[value_col].agg(agg).reset_index()

                report = report.sort_values(by=value_col, ascending=False)

                st.session_state.report = report

    if st.session_state.report is not None:

        report = st.session_state.report

        st.dataframe(report, use_container_width=True)

        # EXPORT

        export_type = st.selectbox("Export Format", ["Excel", "CSV"])

        buffer = BytesIO()

        if export_type == "Excel":
            report.to_excel(buffer, index=False)
            filename = "BI_Report.xlsx"
        else:
            report.to_csv(buffer, index=False)
            filename = "BI_Report.csv"

        buffer.seek(0)

        st.download_button(
            "Download Report",
            buffer,
            filename,
        )

        # CHARTS

        chart = st.selectbox("Chart Type", ["Bar", "Line", "Pie"])

        if st.button("Preview Chart"):

            if chart == "Bar":
                fig = px.bar(report, x=report.columns[0], y=report.columns[1])

            elif chart == "Line":
                fig = px.line(report, x=report.columns[0], y=report.columns[1])

            else:
                fig = px.pie(
                    report,
                    names=report.columns[0],
                    values=report.columns[1],
                )

            st.plotly_chart(fig, use_container_width=True)

# ====================================================
# REPORT HISTORY
# ====================================================

if menu == "Report History":

    st.title("📂 Report History")

    history = get_reports(st.session_state.user)

    if history:

        for r in history:
            st.write("Report generated:", r[0])

    else:

        st.info("No reports yet.")

st.caption("Enterprise Data Intelligence Platform • Built by Denis")
