st.subheader("🧠 AI Auto Insights")

try:
    category_col = report.columns[0]
    value_col = report.columns[1]

    total_value = report[value_col].sum()
    avg_value = report[value_col].mean()

    top_row = report.iloc[0]
    bottom_row = report.iloc[-1]

    st.info(f"""
**Automated Data Insights**

• The dataset shows **{len(report)} categories** grouped by **{category_col}**.

• The **highest performing category** is **{top_row[category_col]}**
  with a value of **{round(top_row[value_col],2)}**.

• The **lowest performing category** is **{bottom_row[category_col]}**
  with a value of **{round(bottom_row[value_col],2)}**.

• The **total value across all categories** is **{round(total_value,2)}**.

• The **average value per category** is **{round(avg_value,2)}**.

• The top category contributes significantly compared to the lowest category,
  which may indicate concentration or uneven distribution.

• Further analysis may identify drivers behind the top-performing segment.
""")

except:
    st.warning("AI insights could not be generated for this dataset.")
