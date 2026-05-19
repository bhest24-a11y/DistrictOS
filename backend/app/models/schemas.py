from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class KPIRecord(BaseModel):
    date: Optional[str] = None
    store: Optional[str] = None
    department: Optional[str] = None
    metric: str
    actual: Optional[float] = None
    target: Optional[float] = None
    variance: Optional[float] = None
    status: Optional[str] = None
    source: Optional[str] = None
    confidence_score: float = 0.0

class IntelligenceOutput(BaseModel):
    district_health_summary: List[str]
    highest_priority_stores: List[str]
    risks: List[str]
    likely_root_causes: List[str]
    suggested_actions: List[str]
    vp_email_draft: str
    huddle_script: str
    cleaned_records: List[KPIRecord]
