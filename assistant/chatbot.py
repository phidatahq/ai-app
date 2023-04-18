import openai

from assistant.message import Message
from assistant.database import get_redis_connection, get_redis_results
from assistant.settings import assistant_settings


class Chatbot:
    """A class to create a chatbot assistant that can retrieve search results from a Redis database"""

    def __init__(self):
        self.conversation_history = []
        self.redis_client = get_redis_connection()

    def _get_assistant_response(self, prompt):
        """Get a response from the OpenAI API"""

        try:
            completion = openai.ChatCompletion.create(
                model=assistant_settings.chat_model, messages=prompt, temperature=0.1
            )

            response_message = Message(
                completion["choices"][0]["message"]["role"],
                completion["choices"][0]["message"]["content"],
            )
            return response_message.message()

        except Exception as e:
            return f"Request failed with exception {e}"

    def _get_search_results(self, prompt):
        """Retrieve search results from Redis database"""

        latest_question = prompt
        search_content = get_redis_results(
            self.redis_client, latest_question, assistant_settings.index_name
        )["result"][0]
        return search_content

    def ask_assistant(self, next_user_prompt):
        """Ask the assistant a question and return the response"""

        [self.conversation_history.append(x) for x in next_user_prompt]
        assistant_response = self._get_assistant_response(self.conversation_history)

        # Answer normally unless the trigger sequence is used "searching_for_answers"
        if "searching for answers" in assistant_response["content"].lower():
            question_extract = openai.Completion.create(
                model=assistant_settings.completions_model,
                prompt=f"Extract the user's latest question and the year for that question from this conversation: {self.conversation_history}. Extract it as a sentence stating the Question and Year",
            )
            search_result = self._get_search_results(
                question_extract["choices"][0]["text"]
            )

            # We insert an extra system prompt here to give fresh context to the Chatbot on how to use the Redis results
            # In this instance we add it to the conversation history, but in production it may be better to hide
            self.conversation_history.insert(
                -1,
                {
                    "role": "system",
                    "content": f"Answer the user's question using this content: {search_result}. If you cannot answer the question, say 'Sorry, I don't know the answer to this one'",
                },
            )

            assistant_response = self._get_assistant_response(self.conversation_history)

            self.conversation_history.append(assistant_response)
            return assistant_response
        else:
            self.conversation_history.append(assistant_response)
            return assistant_response

    def pretty_print_conversation_history(self, colorize_assistant_replies=True):
        """Print the conversation history in a pretty format"""
        from termcolor import colored

        for entry in self.conversation_history:
            if entry["role"] == "system":
                pass
            else:
                prefix = entry["role"]
                content = entry["content"]
                output = (
                    colored(prefix + ":\n" + content, "green")
                    if colorize_assistant_replies and entry["role"] == "assistant"
                    else prefix + ":\n" + content
                )
                # prefix = entry['role']
                print(output)
