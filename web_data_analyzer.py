import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Corporate Data Analyzer | Denis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Corporate Data Analyzer")
st.subheader("Professional Data Insights Platform | Built by Denis")

st.divider()

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["csv", "xlsx"])

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully ✅")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Numeric Columns", len(df.select_dtypes(include=["int64","float64"]).columns))

    st.divider()

    st.subheader("📄 Data Preview")
    st.dataframe(df, use_container_width=True)

    numeric_columns = df.select_dtypes(include=["int64","float64"]).columns

    if len(numeric_columns) > 0:
        st.subheader("📈 Interactive Chart")

        selected_column = st.selectbox("Select column", numeric_columns)

        fig = px.histogram(df, x=selected_column)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Processed File",
        csv,
        "processed_data.csv",
        "text/csv"
    )

st.divider()
st.caption("© 2026 Denis | Corporate Data Analytics Platform")
