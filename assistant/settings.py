from pydantic import BaseSettings


class AssistantSettings(BaseSettings):
    """Assistant settings that can be derived using environment variables.

    Reference: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    completions_model: str = "text-davinci-003"
    embeddings_model: str = "text-embedding-ada-002"
    chat_model: str = "gpt-3.5-turbo"
    text_embedding_chunk_size: int = 300
    vector_field_name: str = "content_vector"
    prefix: str = "sportsdoc"
    index_name: str = "f1-index"


# Create AssistantSettings object
assistant_settings = AssistantSettings()
