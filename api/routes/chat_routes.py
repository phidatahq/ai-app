from typing import List

from fastapi import APIRouter
from pydantic import BaseModel
from phidata.utils.log import logger

from api.routes.endpoints import endpoints
from assistant.chatbot import Chatbot, Message
from assistant.database import get_redis_connection

# -*- Create a FastAPI router
chat_router = APIRouter(prefix=endpoints.CHAT, tags=["chat"])

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

try:
    # -*- Create a Redis connection
    redis_client = get_redis_connection()
except Exception as e:
    logger.error("Failed to connect to redis: {}".format(e))


class ChatRequest(BaseModel):
    message: str = "what is the cost cap for a power unit in 2023"


class ChatResponse(BaseModel):
    output: str


@chat_router.post("/message", response_model=ChatResponse)
def chat_message(chat_request: ChatRequest):
    # -*- Initialize the chatbot
    conversation = Chatbot()

    # -*- Add the system prompt to the conversation
    messages: List = []
    system_message = Message("system", system_prompt)
    messages.append(system_message.message())

    # -*- Add the user message to the conversation
    user_message = Message("user", chat_request.message)
    messages.append(user_message.message())

    # -*- Ask the assistant to respond
    response = conversation.ask_assistant(messages)

    # -*- Return response from the assistant
    return ChatResponse(output=response["content"])
