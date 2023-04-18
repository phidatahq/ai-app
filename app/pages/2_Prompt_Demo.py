import streamlit as st
import openai

from assistant.database import get_redis_connection, get_redis_results
from assistant.settings import assistant_settings

# Initialise Redis connection
redis_client = get_redis_connection()


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
        result_df = get_redis_results(
            redis_client, prompt, assistant_settings.index_name
        )

        # Build a prompt that provides the original query, the results and asks GPT to summarize them.
        summary_prompt = """Summarise the search results in a bulleted list to
        answer the search query a customer has sent.
        Search query: {}
        Search result: {}
        Summary:
        """.format(
            prompt, result_df["result"][0]
        )

        summary = openai.Completion.create(
            engine=assistant_settings.completions_model,
            prompt=summary_prompt,
            max_tokens=500,
        )

        # Response provided by GPT-3
        st.write(summary["choices"][0]["text"])

        # Option to display raw table instead of summary from GPT-3
        # st.table(result_df)


#
# -*- Prompt Sidebar
#
def prompt_sidebar():
    if st.sidebar.button("Reload Session"):
        st.session_state.clear()
        st.experimental_rerun()


#
# -*- Prompt Page
#
st.set_page_config(page_title="Prompt Product", page_icon="🔎", layout="wide")
st.title("Build a Prompt based product using your own data")
st.subheader("Ask a question about Formula 1 rules")

prompt_sidebar()
prompt_main()
