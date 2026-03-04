import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Corporate Data Intelligence Suite | Denis",
    page_icon="📊",
    layout="wide"
)

# ---------------- PREMIUM HEADER ----------------
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
        Executive Analytics • Automated Insights • PDF Reporting<br>
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

        st.subheader("📄 Data Preview")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Statistical Summary")
        st.write(df.describe())

        # -------- AI COMMENTARY --------
        st.subheader("🧠 AI Executive Commentary")

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        if not numeric_df.empty:
            highest_mean = numeric_df.mean().idxmax()
            lowest_mean = numeric_df.mean().idxmin()

            commentary = f"""
            The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.
            The strongest performing metric appears to be '{highest_mean}',
            showing the highest average value across the dataset.
            Conversely, '{lowest_mean}' reflects the lowest average,
            which may require deeper operational review.
            Overall data structure appears stable for executive analysis.
            """

            st.info(commentary)
        else:
            commentary = "No numeric data available for executive insights."
            st.warning(commentary)

        # -------- PDF GENERATION --------
        if st.button("📄 Generate Executive PDF Report"):

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []

            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            normal_style = styles["Normal"]

            elements.append(Paragraph("Corporate Data Intelligence Report", title_style))
            elements.append(Spacer(1, 0.5 * inch))

            elements.append(Paragraph(f"Total Rows: {df.shape[0]}", normal_style))
            elements.append(Paragraph(f"Total Columns: {df.shape[1]}", normal_style))
            elements.append(Paragraph(f"Missing Values: {df.isnull().sum().sum()}", normal_style))
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(Paragraph("Executive Commentary:", styles["Heading2"]))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(commentary, normal_style))
            elements.append(Spacer(1, 0.5 * inch))

            # Add small data preview table (first 5 rows)
            preview_data = [df.columns.tolist()] + df.head().values.tolist()
            table = Table(preview_data)
            table.setStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
            ])
            elements.append(table)

            doc.build(elements)
            buffer.seek(0)

            st.download_button(
                label="⬇ Download PDF Report",
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
            st.warning("No numeric columns available for visualization.")

    # ================================
    # PAGE 3 — DATA CLEANING
    # ================================
    if menu == "Data Cleaning":

        st.subheader("🧹 Data Cleaning Tools")

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
st.caption("🚀 Corporate Data Intelligence Suite | Executive Reporting Tool | Built by Denis")
