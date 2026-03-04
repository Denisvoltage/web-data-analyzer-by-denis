import streamlit as st

st.set_page_config(page_title="Corporate Data Analyzer", layout="wide")

st.title("📊 Corporate Data Analyzer by Denis")
st.write("App is running successfully 🚀")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Corporate Data Analyzer by Denis",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
# 📊 Corporate Data Analyzer
### Built & Designed by Denis

Upload your corporate Excel or CSV file and get instant insights.
""")

st.divider()

uploaded_file = st.file_uploader(
    "📂 Upload Excel or CSV File",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully ✅")

    st.subheader("📄 Data Preview")
    st.dataframe(df)

    st.subheader("📊 Data Summary")
    st.write(df.describe())

    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns

    if len(numeric_columns) > 0:
        column = st.selectbox("Select column to visualize", numeric_columns)

        fig, ax = plt.subplots()
        df[column].hist(ax=ax)
        st.pyplot(fig)
st.divider()
st.markdown("""
---
🔗 Developed by **Denis**  
💼 Corporate Data Analytics Tool  
🚀 Powered by Python & Streamlit
""")
