from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class QuestionHistory(Base):
    __tablename__ = "question_history"

    id = Column(Integer,primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source_file = Column(String(255), nullable=True)
    source_page = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)