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
st.set_page_config(
    page_title="Data Intelligence Platform",
    page_icon="📊",
    layout="wide"
)

# ---------------- CLEAN UI STYLING ----------------
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}
.sub-title {
    color: #6b7280;
    margin-bottom: 30px;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #111827;
}
</style>
""", unsafe_allow_html=True)

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

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="main-title">🚀 Data Intelligence Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Professional Analytics • Automated Reports</div>', unsafe_allow_html=True)

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

menu = st.sidebar.radio("Navigation", ["Dashboard", "Report History"])

# ---------------- HEADER ----------------
st.markdown('<div class="main-title">📊 Executive Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload data. Get instant insights. Generate executive reports.</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":

    uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # KPI CARDS
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.divider()

        st.subheader("Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        if not numeric_df.empty:

            # AUTO SELECT BEST COLUMN
            best_column = numeric_df.mean().idxmax()

            st.subheader("Key Performance Visualization")
            fig = px.bar(df, x=best_column)
            st.plotly_chart(fig, use_container_width=True)

            commentary = f"""
Executive Summary:

This dataset contains {df.shape[0]} records across {df.shape[1]} variables.
The strongest performing metric appears to be '{best_column}',
indicating it holds the highest average value.
Data structure is suitable for strategic reporting and executive review.
"""

            st.subheader("AI Executive Commentary")
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
                    label="Download Executive PDF",
                    data=buffer,
                    file_name="Executive_Report.pdf",
                    mime="application/pdf"
                )

        else:
            st.warning("No numeric columns available for visualization.")

# ---------------- REPORT HISTORY ----------------
if menu == "Report History":

    st.subheader("Your Generated Reports")

    reports = get_reports(st.session_state.user)

    if reports:
        for r in reports:
            st.write("• Generated on:", r[0])
    else:
        st.info("No reports generated yet.")

st.caption("Enterprise Ready | Clean UI | Built by Denis")
