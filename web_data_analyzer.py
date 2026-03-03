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
