import streamlit as st

st.set_page_config(
    page_title="AI Apps",
    page_icon="🚝",
)

st.markdown("### Select an App from the sidebar:")
st.markdown("1. DuckGpt: Use GPT to query your data using DuckDB (AI Agent demo)")
st.markdown("2. Prompt Product: Build a Prompt based product using your own data")
st.markdown("3. Chat Product: Build a Chat based product using your own data")
st.markdown("4. ChatGpt: Chat with GPT-3.5 turbo")

st.sidebar.success("Select an App from above")
