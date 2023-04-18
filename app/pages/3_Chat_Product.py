from typing import List

import streamlit as st
from streamlit_chat import message

from assistant.chatbot import Chatbot, Message
from assistant.database import get_redis_connection

# Initialize Redis connection
redis_client = get_redis_connection()

# Set instructions for the assistant using a
# System prompt that requires Question and Year to be extracted from the user
system_prompt = """
You are a helpful Formula 1 knowledge base assistant.
You need to capture a Question and Year from each customer.
The Question is their query on Formula 1, and the Year is the year of the applicable Formula 1 season.
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


def query(messages: List):
    response = st.session_state["chat"].ask_assistant(messages)
    return response


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
        # Initialization
        messages: List = []
        if "chat" not in st.session_state:
            st.session_state["chat"] = Chatbot()
            messages = []
            system_message = Message("system", system_prompt)
            messages.append(system_message.message())
        else:
            messages = []

        user_message = Message("user", prompt)
        messages.append(user_message.message())

        response = query(messages)
        # Debugging step to print the whole response
        # st.write(response)

        st.session_state.past.append(prompt)
        st.session_state.generated.append(response["content"])

    if st.session_state["generated"]:
        for i in range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["generated"][i], key=str(i))
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")


#
# -*- Chat Sidebar
#
def chat_sidebar():
    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Chatbot Page
#
st.set_page_config(page_title="Chat Product", page_icon="🔎", layout="wide")
st.title("Build a Chat based product using your own data")
st.subheader("Chat about Formula 1 rules")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

chat_sidebar()
chat_main()
