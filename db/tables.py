from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import Column
from sqlalchemy.types import String, BigInteger, DateTime


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy model definitions.

    https://fastapi.tiangolo.com/tutorial/sql-databases/#create-a-base-class
    https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.DeclarativeBase
    """

    pass


class AssistantPrompts(Base):
    """
    Table for storing assistant prompts.
    """

    __tablename__ = "assistant_prompts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    prompt_data = Column(JSONB)
    model_data = Column(JSONB)
    usage_data = Column(JSONB)
    response_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.utcnow())
    updated_at = Column(DateTime(timezone=True), onupdate=func.utcnow())
