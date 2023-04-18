from os import getenv, environ
from typing import Optional, Any, List

import streamlit as st
from streamlit_chat import message

from assistant.chatbot import Chatbot, Message
from assistant.database import get_redis_connection


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
# -*- Chat Sidebar
#
def chat_sidebar():
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
# -*- Chat Main UI
#
def chat_main():
    prompt = st.text_input(
        "Send a message",
        placeholder="what is the cost cap for a power unit in 2023",
        key="input",
    )

    if prompt:
        # -*- Create a System Prompt
        system_prompt = (
            "You are a helpful assistant that helps customers answer questions."
        )

        # -*- Create a System Prompt for F1 rules
        if st.session_state["data_source"] == "F1 rules":
            # -*- Get redis client
            redis_client = create_redis_client()
            if redis_client is None:
                st.write("📡  Redis client not available")
                return

            system_prompt = """
            You are a helpful Formula 1 knowledge base assistant.
            You need to capture a Question and Year from each customer.
            The Question is their query on Formula 1,
            and the Year is the year of the applicable Formula 1 season.
            Think about this step by step:
            - The user will ask a Question
            - You will ask them for the Year if their question didn't include a Year
            - Once you have the Year, say "searching for answers".

            Example:

            User: I'd like to know the cost cap for a power unit

            Assistant: Certainly, what year would you like this for?

            User: 2023 please.

            Assistant: Searching for answers.
            """

        # -*- Initialize Chatbot and add the System Prompt to the conversation
        messages: List = []
        if "conversation" not in st.session_state:
            st.session_state["conversation"] = Chatbot()
            system_message = Message("system", system_prompt)
            messages.append(system_message.message())

        # -*- Add the user message to the conversation
        user_message = Message("user", prompt)
        messages.append(user_message.message())

        response = st.session_state["conversation"].ask_assistant(messages)
        # Debugging step to print the whole response
        # st.write(response)

        st.session_state.past.append(prompt)
        st.session_state.generated.append(response["content"])

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")


#
# -*- Chatbot UI
#
st.set_page_config(page_title="AI Chat", page_icon="🔎", layout="wide")
st.markdown("## Build a Chatbot using your own data")
st.write("Select a data source and send a message")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

chat_sidebar()
chat_main()
