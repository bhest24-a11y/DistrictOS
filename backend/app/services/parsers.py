from pathlib import Path
import re
import pandas as pd
from PIL import Image
import pytesseract
from app.models.schemas import KPIRecord

KNOWN_DEPARTMENTS = ["Produce", "Meat", "Deli", "Bakery", "Grocery", "Dairy", "Front End", "Store"]
KNOWN_METRICS = ["sales", "shrink", "compliance", "labor", "forecast", "in-stock", "oos", "service", "margin"]

def parse_excel_or_csv(path: Path) -> list[KPIRecord]:
    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    records = []
    cols = {c.lower().strip(): c for c in df.columns}

    for _, row in df.iterrows():
        metric = str(row.get(cols.get("metric", ""), "") or "unknown_metric")
        actual = _safe_float(row.get(cols.get("actual", ""), None))
        target = _safe_float(row.get(cols.get("target", ""), None))
        variance = actual - target if actual is not None and target is not None else None

        records.append(KPIRecord(
            date=str(row.get(cols.get("date", ""), "")) or None,
            store=str(row.get(cols.get("store", ""), "")) or None,
            department=str(row.get(cols.get("department", ""), "")) or None,
            metric=metric,
            actual=actual,
            target=target,
            variance=variance,
            status=_status(actual, target),
            source=path.name,
            confidence_score=0.85
        ))
    return records

def parse_image(path: Path) -> list[KPIRecord]:
    try:
        text = pytesseract.image_to_string(Image.open(path))
    except Exception:
        text = ""

    return parse_text_blob(text, source=path.name)

def parse_text_blob(text: str, source: str = "pasted_text") -> list[KPIRecord]:
    records = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        metric_hit = next((m for m in KNOWN_METRICS if m.lower() in line.lower()), None)
        dept_hit = next((d for d in KNOWN_DEPARTMENTS if d.lower() in line.lower()), None)
        store_hit = _extract_store(line)
        nums = [_safe_float(x) for x in re.findall(r"-?\\d+(?:\\.\\d+)?%?", line.replace(",", ""))]
        nums = [n for n in nums if n is not None]

        if metric_hit and nums:
            actual = nums[-1]
            target = nums[-2] if len(nums) >= 2 else None
            variance = actual - target if target is not None else None
            records.append(KPIRecord(
                store=store_hit,
                department=dept_hit,
                metric=metric_hit,
                actual=actual,
                target=target,
                variance=variance,
                status=_status(actual, target),
                source=source,
                confidence_score=0.55 if store_hit else 0.40
            ))

    if not records and text:
        records.append(KPIRecord(
            metric="unstructured_report_text",
            source=source,
            confidence_score=0.25
        ))

    return records

def _extract_store(line: str):
    m = re.search(r"\\b(?:store|st)\\s*#?\\s*(\\d{2,5})\\b", line, re.I)
    if m:
        return m.group(1)
    m = re.search(r"\\b(\\d{3,5})\\b", line)
    return m.group(1) if m else None

def _safe_float(value):
    try:
        if value is None:
            return None
        s = str(value).replace("%", "").replace(",", "").strip()
        if s == "" or s.lower() == "nan":
            return None
        return float(s)
    except Exception:
        return None

def _status(actual, target):
    if actual is None or target is None:
        return "needs_review"
    return "off_track" if actual < target else "on_track"
