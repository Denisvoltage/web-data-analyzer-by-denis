import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import tempfile
import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Corporate Data Intelligence Suite | Denis",
    page_icon="📊",
    layout="wide"
)

# ---------------- HEADER ----------------
st.markdown("""
<style>
.hero-box {
    padding: 40px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    text-align: center;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.4);
    margin-bottom: 25px;
}
.hero-title {
    font-size: 48px;
    font-weight: 800;
    color: white;
}
.hero-subtitle {
    font-size: 18px;
    color: #cbd5e1;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">📊 Corporate Data Intelligence Suite</div>
    <div class="hero-subtitle">
        Executive Analytics • AI Commentary • PDF Reporting<br>
        Built by Denis
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📁 Navigation")
menu = st.sidebar.radio(
    "Select Module",
    ["Upload & Overview", "Visualizations", "Data Cleaning"]
)

st.sidebar.markdown("---")
logo_file = st.sidebar.file_uploader("Upload Company Logo (Optional)", type=["png","jpg"])
st.sidebar.caption("© 2026 Denis Analytics")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload Excel or CSV File (Max 200MB)",
    type=["csv", "xlsx"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------------- DATE FILTER ----------------
    date_columns = df.select_dtypes(include=["datetime64"]).columns

    if len(date_columns) > 0:
        selected_date_column = st.selectbox("Select Date Column for Filtering", date_columns)
        min_date = df[selected_date_column].min()
        max_date = df[selected_date_column].max()
        start_date, end_date = st.date_input(
            "Filter Date Range",
            [min_date, max_date]
        )
        df = df[(df[selected_date_column] >= pd.to_datetime(start_date)) &
                (df[selected_date_column] <= pd.to_datetime(end_date))]

    # ================================
    # PAGE 1 — OVERVIEW
    # ================================
    if menu == "Upload & Overview":

        st.success("File uploaded successfully ✅")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", df.shape[0])
        col2.metric("Total Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.divider()
        st.dataframe(df.head(), use_container_width=True)

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        # -------- AI COMMENTARY --------
        if not numeric_df.empty:
            highest_mean = numeric_df.mean().idxmax()
            lowest_mean = numeric_df.mean().idxmin()

            commentary = f"""
Executive Summary:
The dataset consists of {df.shape[0]} records across {df.shape[1]} variables.
The strongest performing metric is '{highest_mean}', demonstrating the highest average value.
The lowest average metric is '{lowest_mean}', which may require management review.
Overall data consistency appears suitable for strategic reporting.
"""
            st.info(commentary)
        else:
            commentary = "No numeric data available for executive insights."
            st.warning(commentary)

        # -------- CHART FOR PDF --------
        chart_column = None
        fig = None

        if len(numeric_df.columns) > 0:
            chart_column = st.selectbox("Select Column for Executive Chart", numeric_df.columns)
            fig = px.bar(df, x=chart_column)
            st.plotly_chart(fig, use_container_width=True)

        # -------- PDF GENERATION --------
        if st.button("📄 Generate Full Executive PDF Report"):

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            elements.append(Paragraph("Corporate Data Intelligence Report", styles["Heading1"]))
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph(f"Generated On: {datetime.datetime.now()}", styles["Normal"]))
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(Paragraph(commentary, styles["Normal"]))
            elements.append(Spacer(1, 0.5 * inch))

            if logo_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
                    tmp_logo.write(logo_file.getvalue())
                    elements.append(Image(tmp_logo.name, width=2*inch, height=1*inch))
                    elements.append(Spacer(1, 0.5 * inch))

            if fig:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_chart:
                    fig.write_image(tmp_chart.name)
                    elements.append(Image(tmp_chart.name, width=5*inch, height=3*inch))

            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                label="⬇ Download Executive PDF",
                data=buffer,
                file_name="Executive_Report.pdf",
                mime="application/pdf"
            )

    # ================================
    # PAGE 2 — VISUALIZATIONS
    # ================================
    if menu == "Visualizations":

        numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

        if len(numeric_columns) > 0:
            chart_type = st.selectbox(
                "Select Chart Type",
                ["Histogram", "Bar Chart", "Line Chart", "Pie Chart"]
            )

            column = st.selectbox("Select Column", numeric_columns)

            if chart_type == "Histogram":
                fig = px.histogram(df, x=column)
            elif chart_type == "Bar Chart":
                fig = px.bar(df, x=column)
            elif chart_type == "Line Chart":
                fig = px.line(df, y=column)
            elif chart_type == "Pie Chart":
                fig = px.pie(df, names=column)

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No numeric columns available.")

    # ================================
    # PAGE 3 — DATA CLEANING
    # ================================
    if menu == "Data Cleaning":

        if st.button("Remove Missing Values"):
            df = df.dropna()
            st.success("Missing values removed ✅")

        if st.button("Remove Duplicate Rows"):
            df = df.drop_duplicates()
            st.success("Duplicate rows removed ✅")

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

st.divider()
st.caption("🚀 Enterprise Executive Analytics Platform | Built by Denis")
