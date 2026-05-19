import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from backend.app.core.config import PROCESSED_DIR
from backend.app.models.schemas import KPIRecord, IntelligenceOutput

def save_records(records: list[KPIRecord]) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PROCESSED_DIR / f"cleaned_kpi_records_{ts}.csv"
    pd.DataFrame([r.model_dump() for r in records]).to_csv(path, index=False)
    return path

def save_summary(output: IntelligenceOutput) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PROCESSED_DIR / f"districtos_summary_{ts}.json"
    with open(path, "w") as f:
        json.dump(output.model_dump(), f, indent=2)
    return path
