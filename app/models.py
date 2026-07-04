import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON

from app.database import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True)
    natural_language = Column(Text, nullable=False)
    sql_query = Column(Text, nullable=False)
    explanation = Column(Text, default="")
    result_preview = Column(JSON, default=list)
    columns = Column(JSON, default=list)
    row_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    success = Column(Integer, default=1)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
