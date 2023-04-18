from typing import Optional

import openai
import pandas as pd
import numpy as np

from redis import Redis
from redis.commands.search.field import VectorField
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.query import Query

from assistant.settings import assistant_settings

# from workspace.dev.docker_resources import dev_redis


def get_redis_connection(
    host: str = "redis-stack-container", port: int = 6379, db: int = 0
):
    """Get a Redis connection"""

    redis_host = host  # or dev_redis.get_db_host_docker()
    redis_port = port  # or dev_redis.get_db_port_docker()
    redis_db = db  # or dev_redis.get_db_schema()

    return Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=False)


def create_hnsw_index(
    redis_conn, vector_field_name, vector_dimensions=1536, distance_metric="COSINE"
):
    """Create a Redis index to hold our data"""

    redis_conn.ft().create_index(
        [
            VectorField(
                vector_field_name,
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimensions,
                    "DISTANCE_METRIC": distance_metric,
                },
            ),
            TextField("filename"),
            TextField("text_chunk"),
            NumericField("file_chunk_index"),
        ]
    )


def load_vectors(client: Redis, input_list, vector_field_name):
    """Load vectors into Redis"""

    p = client.pipeline(transaction=False)
    for text in input_list:
        # hash key
        key = f"{assistant_settings.prefix}:{text['id']}"

        # hash values
        item_metadata = text["metadata"]
        item_keywords_vector = np.array(text["vector"], dtype="float32").tobytes()
        item_metadata[vector_field_name] = item_keywords_vector

        # HSET
        p.hset(key, mapping=item_metadata)

    p.execute()


def query_redis(redis_conn, query, index_name, top_k=2):
    """Query Redis for most relevant documents"""

    # Creates embedding vector from user query
    embedded_query = np.array(
        openai.Embedding.create(
            input=query,
            model=assistant_settings.embeddings_model,
        )["data"][0]["embedding"],
        dtype=np.float32,
    ).tobytes()

    # Prepare the query
    q = (
        Query(
            f"*=>[KNN {top_k} @{assistant_settings.vector_field_name} $vec_param AS vector_score]"
        )
        .sort_by("vector_score")
        .paging(0, top_k)
        .return_fields("vector_score", "filename", "text_chunk", "text_chunk_index")
        .dialect(2)
    )
    params_dict = {"vec_param": embedded_query}

    # Execute the query
    results = redis_conn.ft(index_name).search(q, query_params=params_dict)

    return results


def get_redis_results(redis_conn, query, index_name):
    """Get mapped documents from Weaviate results"""

    # Get most relevant documents from Redis
    query_result = query_redis(redis_conn, query, index_name)

    # Extract info into a list
    query_result_list = []
    for i, result in enumerate(query_result.docs):
        result_order = i
        text = result.text_chunk
        score = result.vector_score
        query_result_list.append((result_order, text, score))

    # Display result as a DataFrame for ease of us
    result_df = pd.DataFrame(query_result_list)
    result_df.columns = ["id", "result", "certainty"]
    return result_df
