import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Corporate Data Intelligence Suite | Denis",
    page_icon="📊",
    layout="wide"
)

# ---------------- PREMIUM HEADER ----------------
st.markdown(
    """
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
        font-size: 52px;
        font-weight: 800;
        color: white;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #cbd5e1;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">📊 Corporate Data Intelligence Suite</div>
        <div class="hero-subtitle">
            Enterprise Analytics • Automated Insights • Executive Reporting<br>
            Designed & Built by Denis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

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

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ================================
    # 📊 PAGE 1 — OVERVIEW
    # ================================
    if menu == "Upload & Overview":

        st.success("File uploaded successfully ✅")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📌 Total Rows")
            st.metric("", df.shape[0])

        with col2:
            st.markdown("### 📊 Total Columns")
            st.metric("", df.shape[1])

        with col3:
            st.markdown("### ⚠ Missing Values")
            st.metric("", df.isnull().sum().sum())

        st.divider()

        st.subheader("📄 Data Preview")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Statistical Summary")
        st.write(df.describe())

        # -------- AUTO INSIGHTS --------
        st.subheader("🧠 Auto Insights")

        numeric_df = df.select_dtypes(include=["int64", "float64"])

        if not numeric_df.empty:
            highest_mean = numeric_df.mean().idxmax()
            lowest_mean = numeric_df.mean().idxmin()

            st.info(f"📈 Highest average column: **{highest_mean}**")
            st.info(f"📉 Lowest average column: **{lowest_mean}**")
        else:
            st.warning("No numeric data available for insights.")

    # ================================
    # 📈 PAGE 2 — VISUALIZATIONS
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
    # 🧹 PAGE 3 — DATA CLEANING
    # ================================
    if menu == "Data Cleaning":

        st.subheader("🧹 Data Cleaning Tools")

        if st.button("Remove Missing Values"):
            df = df.dropna()
            st.success("Missing values removed ✅")

        if st.button("Remove Duplicate Rows"):
            df = df.drop_duplicates()
            st.success("Duplicate rows removed ✅")

        st.divider()

        st.dataframe(df, use_container_width=True)

        # -------- DOWNLOAD CLEANED FILE --------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

# ---------------- FOOTER ----------------
st.divider()
st.caption("🚀 Corporate Data Intelligence Suite | Built by Denis | Powered by Python & Streamlit")
