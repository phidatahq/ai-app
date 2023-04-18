import streamlit as st

st.set_page_config(
    page_title="AI Apps",
    page_icon="🚝",
)

st.markdown("### Select an App from the sidebar:")
st.markdown("1. Agent Demo: Use GPT to query your data using a DuckDB AI Agent")
st.markdown("2. Prompt Demo: Build a Prompt product using your own data")
st.markdown("3. Chat Demo: Build a Chat product using your own data")
st.markdown("4. ChatGpt: Chat with GPT-3.5 using the api")

st.sidebar.success("Select an App from above")
