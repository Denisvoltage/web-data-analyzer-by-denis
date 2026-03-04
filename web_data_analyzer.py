import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Corporate Data Analyzer | Denis",
    page_icon="📊",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Corporate Data Analyzer")
st.sidebar.markdown("Built by Denis")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    ["Upload & Overview", "Visualizations", "Data Cleaning"]
)

# ---------------- HEADER ----------------
st.title("📊 Corporate Data Analyzer")
st.caption("Professional Data Insights Platform | 2026 Edition")

st.divider()

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["csv", "xlsx"])

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # ---------------- PAGE 1 ----------------
    if menu == "Upload & Overview":

        st.success("File uploaded successfully ✅")

        col1, col2, col3 = st.columns(3)

        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.divider()

        st.subheader("📄 Data Preview")
        st.dataframe(df, use_container_width=True)

        st.subheader("📊 Statistical Summary")
        st.write(df.describe())

    # ---------------- PAGE 2 ----------------
    if menu == "Visualizations":

        numeric_columns = df.select_dtypes(include=["int64","float64"]).columns

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

    # ---------------- PAGE 3 ----------------
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

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Cleaned Data",
            csv,
            "cleaned_data.csv",
            "text/csv"
        )

st.divider()
st.caption("© 2026 Denis | Corporate Data Analytics Platform | Powered by Python & Streamlit")
