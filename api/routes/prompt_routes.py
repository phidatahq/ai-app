import openai
from fastapi import APIRouter
from pydantic import BaseModel
from phidata.utils.log import logger

from api.routes.endpoints import endpoints
from assistant.database import get_redis_connection, get_redis_results
from assistant.settings import assistant_settings

# -*- Create a FastAPI router
prompt_router = APIRouter(prefix=endpoints.PROMPT, tags=["prompt"])

try:
    # -*- Create a Redis connection
    redis_client = get_redis_connection()
except Exception as e:
    logger.error("Failed to connect to redis: {}".format(e))


class PromptRequest(BaseModel):
    query: str = "what is the cost cap for a power unit in 2023"


class PromptResponse(BaseModel):
    output: str


@prompt_router.post("/query", response_model=PromptResponse)
def prompt_query(prompt_request: PromptRequest):
    # Get results from redis
    try:
        query = prompt_request.query
        result_df = get_redis_results(
            redis_client, query, assistant_settings.index_name
        )
    except Exception as e:
        error_msg = "Failed to get results from redis: {}".format(e)
        logger.error(error_msg)
        return PromptResponse(output=error_msg)

    # Build a prompt that provides the original query, the results and asks GPT to summarize them.
    summary_prompt = """Summarise the search results in a bulleted list to
    answer the search query a customer has sent.
    Search query: {}
    Search result: {}
    Summary:
    """.format(
        query, result_df["result"][0]
    )

    summary = openai.Completion.create(
        engine=assistant_settings.completions_model,
        prompt=summary_prompt,
        max_tokens=500,
    )

    # Response provided by GPT-3
    return PromptResponse(output=summary["choices"][0]["text"])
