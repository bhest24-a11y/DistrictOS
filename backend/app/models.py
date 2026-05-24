from sqlalchemy import Column, Integer, Text, DateTime, JSON, Date, Numeric, String, Boolean, Index
from datetime import datetime
from .db import Base

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    store_id = Column(String(20), unique=True, index=True)  # '045'
    store_name = Column(String(100))
    district = Column(String(50))
    region = Column(String(50))

class DailyPOS(Base):
    __tablename__ = "daily_pos"
    id = Column(Integer, primary_key=True)
    business_date = Column(Date, index=True)
    store_id = Column(String(20), index=True)
    sku = Column(String(30), index=True)
    sku_description = Column(Text)
    category = Column(String(100))
    units_sold = Column(Integer)
    net_sales = Column(Numeric(10,2))
    avg_unit_price = Column(Numeric(10,2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_daily_pos_date_store_sku', 'business_date', 'store_id', 'sku', unique=True),
    )

class OSAAlert(Base):
    __tablename__ = "osa_alerts"
    id = Column(Integer, primary_key=True)
    business_date = Column(Date, index=True)
    store_id = Column(String(20), index=True)
    sku = Column(String(30))
    sku_description = Column(Text)
    category = Column(String(100))
    expected_units = Column(Numeric(10,2))
    actual_units = Column(Integer)
    days_since_last_sale = Column(Integer)
    confidence = Column(Numeric(3,2))  # 0.91 = 91%
    est_missed_sales = Column(Numeric(10,2))
    likely_oos_flag = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Analysis(Base):  # your existing table
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text)
    summary = Column(Text)
    store_severity = Column(JSON)
    alerts = Column(JSON)
    patterns = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

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