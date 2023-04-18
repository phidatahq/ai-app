import openai
from fastapi import APIRouter
from pydantic import BaseModel
from phidata.utils.log import logger

from api.routes.endpoints import endpoints
from assistant.database import get_redis_connection, get_redis_results
from assistant.settings import assistant_settings

# -*- Create a FastAPI router
prompt_router = APIRouter(prefix=endpoints.PROMPT, tags=["prompt"])


class PromptRequest(BaseModel):
    message: str


class PromptResponse(BaseModel):
    output: str


@prompt_router.post("/query", response_model=PromptResponse)
def prompt_query(prompt_request: PromptRequest):
    # -*- Generate Completion
    completion_result = openai.Completion.create(
        engine=assistant_settings.completions_model,
        prompt=prompt_request.message,
        max_tokens=1024,
    )
    logger.info(completion_result)

    # -*- Return response
    return PromptResponse(output=completion_result["choices"][0]["text"])


try:
    # -*- Create a Redis connection
    redis_client = get_redis_connection()
except Exception as e:
    logger.warning("Failed to connect to redis: {}".format(e))


@prompt_router.post("/f1_query", response_model=PromptResponse)
def f1_query(prompt_request: PromptRequest):
    # -*- Get query results from redis
    try:
        query = prompt_request.message
        result_df = get_redis_results(
            redis_client, query, assistant_settings.index_name
        )
    except Exception as e:
        error_msg = "Failed to get results from redis: {}".format(e)
        logger.error(error_msg)
        return PromptResponse(output=error_msg)

    # -*- Create a Summary Prompt
    # Build a prompt that provides the original query, the results and asks GPT to summarize them.
    summary_prompt = """Summarise the search results in a bulleted list to
    answer the search query a customer has sent.
    Search query: {}
    Search result: {}
    Summary:
    """.format(
        query, result_df["result"][0]
    )

    # -*- Generate a summary
    summary = openai.Completion.create(
        engine=assistant_settings.completions_model,
        prompt=summary_prompt,
        max_tokens=500,
    )

    # -*- Return response
    return PromptResponse(output=summary["choices"][0]["text"])
