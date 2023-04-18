from os import getenv, environ
from typing import Optional, Any

import openai
import streamlit as st

from assistant.database import get_redis_connection, get_redis_results
from assistant.settings import assistant_settings


#
# -*- Sidebar component to get OpenAI API key
#
def get_openai_key() -> Optional[str]:
    # Get OpenAI API key from environment variable
    openai_key: Optional[str] = getenv("OPENAI_API_KEY")
    # If not found, get it from user input
    if openai_key is None or openai_key == "" or openai_key == "sk-***":
        api_key = st.sidebar.text_input(
            "OpenAI API key", placeholder="sk-***", key="api_key"
        )
        if api_key != "sk-***" or api_key != "" or api_key is not None:
            openai_key = api_key

    # Store it in session state and environment variable
    if openai_key is not None and openai_key != "":
        st.session_state["OPENAI_API_KEY"] = openai_key
        environ["OPENAI_API_KEY"] = openai_key

    return openai_key


#
# -*- Sidebar component to select data source
#
def select_data_source() -> None:
    # Get the data source
    data_source = st.sidebar.radio("Select Data Source", options=["None", "F1 rules"])
    if data_source:
        st.session_state["data_source"] = data_source
    st.sidebar.markdown(f"📊  Data source : {st.session_state['data_source']}")


#
# -*- Sidebar component to show status
#
def show_status():
    st.sidebar.markdown("## Status")
    if (
        "OPENAI_API_KEY" in st.session_state
        and st.session_state["OPENAI_API_KEY"] != ""
    ):
        st.sidebar.markdown("🔑  OpenAI API key set")
    if "redis_client" in st.session_state:
        st.sidebar.markdown("📡  Redis client available")


#
# -*- Sidebar component to show reload button
#
def show_reload():
    st.sidebar.markdown("---")
    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Prompt Sidebar
#
def prompt_sidebar():
    st.sidebar.markdown("# Settings")

    # Get OpenAI API key
    openai_key = get_openai_key()
    if openai_key is None or openai_key == "" or openai_key == "sk-***":
        st.write("🔑  OpenAI API key not set")

    # Choose data source
    select_data_source()

    # Show status on sidebar
    show_status()

    # Show reload button
    show_reload()


#
# -*- Create redis client
#
def create_redis_client() -> Any:
    # Get duckdb connection
    redis_client = st.session_state.get("redis_client", None)
    if redis_client is None:
        redis_client = get_redis_connection()
        st.session_state["redis_client"] = redis_client
    return redis_client


#
# -*- Prompt Main UI
#
def prompt_main():
    prompt = st.text_input(
        "Enter your question here",
        placeholder="what is the cost cap for a power unit in 2023",
        key="input",
    )

    if prompt:
        completion_prompt = prompt

        if st.session_state["data_source"] != "None":
            # -*- Get redis client
            redis_client = create_redis_client()
            if redis_client is None:
                st.write("📡  Redis client not available")
                return

            # -*- Get results from redis
            result_df = get_redis_results(
                redis_client, prompt, assistant_settings.index_name
            )

            # -*- Create a Summary Prompt
            completion_prompt = """Summarise the search results in a bulleted list to
            answer the search query a customer has sent.
            Search query: {}
            Search result: {}
            Summary:
            """.format(
                prompt, result_df["result"][0]
            )

        # -*- Generate completion
        completion_result = openai.Completion.create(
            engine=assistant_settings.completions_model,
            prompt=completion_prompt,
            max_tokens=500,
        )

        # -*- Write result
        st.write(completion_result["choices"][0]["text"])


#
# -*- Prompt UI
#
st.set_page_config(page_title="AI Prompt", page_icon="🔎", layout="wide")
st.markdown("## Build a Prompt using your own data")
st.write("Select a data source and ask a question")

prompt_sidebar()
prompt_main()
