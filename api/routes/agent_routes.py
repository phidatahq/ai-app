from textwrap import dedent

from fastapi import APIRouter
from pydantic import BaseModel
from phidata.utils.log import logger
from phidata.llm.duckdb.agent import create_duckdb_agent
from phidata.llm.duckdb.connection import create_duckdb_connection
from phidata.llm.duckdb.loader import load_s3_path_to_table
from phidata.llm.duckdb.query import run_duckdb_query

from api.routes.endpoints import endpoints

# -*- Create a FastAPI router
agent_router = APIRouter(prefix=endpoints.AGENT, tags=["agent"])

# -*- List of test datasets
Tables = {
    "titanic": "s3://phidata-public/demo_data/titanic.csv",
    "census": "s3://phidata-public/demo_data/census_2017.csv",
    "covid": "s3://phidata-public/demo_data/covid_19_data.csv",
    "air_quality": "s3://phidata-public/demo_data/air_quality.csv",
}

try:
    # -*- Create a DuckDB connection
    duckdb_connection = create_duckdb_connection()
    # -*- Create a DuckDB agent
    duckdb_agent = create_duckdb_agent(duckdb_connection=duckdb_connection)
except Exception as e:
    logger.warning("Failed to create DuckDB agent: {}".format(e))


class DuckGptRequest(BaseModel):
    table: str = "titanic"
    query: str = "How many people survived by gender?"


class DuckGptResponse(BaseModel):
    output: str
    messages: list = []


@agent_router.post("/duckgpt", response_model=DuckGptResponse)
def duckgpt_query(duckgpt_request: DuckGptRequest):
    tables_loaded = []
    executed_queries = []

    table_to_query: str = duckgpt_request.table
    query = duckgpt_request.query

    # Load the data into DuckDB
    if table_to_query not in tables_loaded:
        s3_data_path: str
        if table_to_query in Tables:
            s3_data_path = Tables[table_to_query]
        else:
            return DuckGptResponse(output="Table not found")

        _table_name, executed_query = load_s3_path_to_table(
            duckdb_connection, s3_data_path
        )
        tables_loaded.append(table_to_query)
        executed_queries.append(executed_query)

    # Add an initial system message
    agent_messages = [
        {
            "role": "system",
            "content": """You are a helpful assistant that answers natural language questions by querying data using duckdb""",  # noqa: E501
        },
    ]

    # Add executed queries
    if len(executed_queries) > 0:
        agent_messages.append(
            {
                "role": "system",
                "content": dedent(
                    """\
                Startup SQL Queries:
                ```
                {}
                ```
            """.format(
                        "\n".join(executed_queries)
                    )
                ),
            },
        )

    # Add user query
    agent_messages.append({"role": "user", "content": query})

    # Create input for agent
    inputs = {
        "input": agent_messages,
        "table_names": run_duckdb_query(duckdb_connection, "show tables"),
    }

    # Generate response
    try:
        result = duckdb_agent(inputs)
    except Exception as e:
        logger.error("Failed to generate response from agent: {}".format(e))
        return DuckGptResponse(output=f"Failed to generate response from agent: {e}")

    # Get the output
    if "output" in result:
        return DuckGptResponse(messages=agent_messages, output=result["output"])
    else:
        return DuckGptResponse(messages=agent_messages, output="No output")
