from typing import List

import openai
from fastapi import APIRouter
from pydantic import BaseModel
from phidata.utils.log import logger

from api.routes.endpoints import endpoints
from utils.message import Message

# -*- Create a FastAPI router
prompt_router = APIRouter(prefix=endpoints.PROMPT, tags=["prompt"])


class PromptRequest(BaseModel):
    query: str
    max_tokens: int = 1024
    temperature: float = 0


class PromptResponse(BaseModel):
    output: str


@prompt_router.post("/query", response_model=PromptResponse)
def prompt_query(prompt_request: PromptRequest):
    # -*- Create a System Prompt
    system_prompt = "You are a helpful assistant that helps customers answer questions."

    # -*- Add the System Prompt to the conversation
    messages: List = []
    system_message = Message("system", system_prompt)
    messages.append(system_message.message())

    # -*- Add the user query to the conversation
    user_message = Message("user", prompt_request.query)
    messages.append(user_message.message())

    # -*- Generate completion
    completion_result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=prompt_request.max_tokens,
        temperature=prompt_request.temperature,
    )
    result = completion_result["choices"][0]["message"]["content"]
    logger.info(result)

    # -*- Return result
    return PromptResponse(output=result)
