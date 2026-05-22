from sqlalchemy import Column, Integer, Text, DateTime, JSON
from datetime import datetime
from .db import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    raw_text = Column(Text)
    summary = Column(Text)

    # 🔥 NEW STRUCTURED STORAGE
    store_severity = Column(JSON)
    alerts = Column(JSON)
    patterns = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)