from os import getenv, environ
from typing import Optional, List

import openai
import streamlit as st

from utils.message import Message


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
# -*- Sidebar component to show status
#
def show_status():
    st.sidebar.markdown("## Status")
    if (
        "OPENAI_API_KEY" in st.session_state
        and st.session_state["OPENAI_API_KEY"] != ""
    ):
        st.sidebar.markdown("🔑  OpenAI API key set")


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

    # Show status on sidebar
    show_status()

    # Show reload button
    show_reload()


#
# -*- Prompt Main UI
#
def prompt_main() -> None:
    prompt = st.text_input(
        "Enter your query here",
        placeholder="Generate a list of 20 names of SQL AI assistants from star wars",
        key="input",
    )

    if prompt:
        # -*- Create a System Prompt
        system_prompt = (
            "You are a helpful assistant that helps customers answer questions."
        )

        # -*- Add the System Prompt to the conversation
        messages: List = []
        system_message = Message("system", system_prompt)
        messages.append(system_message.message())

        # -*- Add the user query to the conversation
        user_message = Message("user", prompt)
        messages.append(user_message.message())

        # -*- Generate completion
        completion_result = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1024,
            temperature=0,
        )
        result = completion_result["choices"][0]["message"]["content"]

        # -*- Write result
        st.write(result)


#
# -*- Prompt UI
#
st.set_page_config(page_title="AI Prompt", page_icon="🔎", layout="wide")
st.markdown("## Build a Prompt using your own data")

prompt_sidebar()
prompt_main()
