from typing import Iterator

import openai
import pandas as pd
import numpy as np
from numpy import array, average

from utils.settings import assistant_settings
from utils.database import load_vectors


def get_col_average_from_list_of_lists(list_of_lists):
    """Return the average of each column in a list of lists."""

    if len(list_of_lists) == 1:
        return list_of_lists[0]
    else:
        list_of_lists_array = array(list_of_lists)
        average_embedding = average(list_of_lists_array, axis=0)
        return average_embedding.tolist()


def get_embeddings(text_array, engine):
    # See https://platform.openai.com/docs/api-reference/embeddings/create
    return openai.Embedding.create(input=text_array, model=engine)["data"]


def create_embeddings_for_text(text, tokenizer):
    """
    Create embeddings for a text using a tokenizer and an OpenAI engine.
    Return a list of tuples (text_chunk, embedding) and an average embedding for a text.
    """

    token_chunks = list(
        chunks(text, assistant_settings.text_embedding_chunk_size, tokenizer)
    )
    text_chunks = [tokenizer.decode(chunk) for chunk in token_chunks]

    embeddings_response = get_embeddings(
        text_chunks, assistant_settings.embeddings_model
    )
    embeddings = [embedding["embedding"] for embedding in embeddings_response]
    text_embeddings = list(zip(text_chunks, embeddings))

    average_embedding = get_col_average_from_list_of_lists(embeddings)

    return (text_embeddings, average_embedding)


def chunks(text, n, tokenizer):
    """Split a text into smaller chunks of size n, preferably ending at the end of a sentence."""

    tokens = tokenizer.encode(text)

    # Yield successive n-sized chunks from text
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j


def get_unique_id_for_file_chunk(filename, chunk_index):
    return str(filename + "-!" + str(chunk_index))


def handle_file_string(file, tokenizer, redis_conn, text_embedding_field, index_name):
    file_path = file[0]
    file_body_string = file[1]

    # Clean up the file string by replacing newlines and double spaces and semi-colons
    clean_file_body_string = (
        file_body_string.replace("  ", " ").replace("\n", "; ").replace(";", " ")
    )

    # Add the filename to the text to embed
    text_to_embed = "Filename is: {}; {}".format(str(file_path), clean_file_body_string)

    # Create embeddings for the text
    try:
        text_embeddings, average_embedding = create_embeddings_for_text(
            text_to_embed, tokenizer
        )
        print("[transformer] Created embedding for {}".format(str(file_path)))
    except Exception as e:
        print("[transformer] Error creating embedding: {}".format(e))

    # Get the vectors array of triples: file_chunk_id, embedding, metadata for each embedding
    # Metadata is a dict with keys: filename, file_chunk_index
    vectors = []
    for i, (text_chunk, embedding) in enumerate(text_embeddings):
        id = get_unique_id_for_file_chunk(str(file_path), i)
        vectors.append(
            (
                {
                    "id": id,
                    "vector": embedding,
                    "metadata": {
                        "filename": str(file_path),
                        "text_chunk": text_chunk,
                        "file_chunk_index": i,
                    },
                }
            )
        )

    try:
        load_vectors(redis_conn, vectors, text_embedding_field)

    except Exception as e:
        print(f"Ran into a problem uploading to Redis: {e}")


class BatchGenerator:
    """Generates batches of a given size from a DataFrame"""

    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size

    # Makes chunks out of an input DataFrame
    def to_batches(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        splits = self.splits_num(df.shape[0])
        if splits <= 1:
            yield df
        else:
            for chunk in np.array_split(df, splits):
                yield chunk

    # Determines how many chunks DataFrame contains
    def splits_num(self, elements: int) -> int:
        return round(elements / self.batch_size)

    __call__ = to_batches
