from pathlib import Path
import re
import pandas as pd
from app.models.schemas import KPIRecord


KNOWN_DEPARTMENTS = [
    "produce", "meat", "deli", "bakery",
    "grocery", "dairy", "front end", "store"
]

KNOWN_METRICS = [
    "sales", "shrink", "compliance",
    "labor", "forecast", "in-stock",
    "oos", "service"
]


# -------------------------
# MAIN ENTRY POINT
# -------------------------

def parse_file(path: Path) -> list[KPIRecord]:
    if path.suffix.lower() in [".xlsx", ".xls", ".csv"]:
        return parse_excel_or_csv(path)
    else:
        return []


# -------------------------
# EXCEL / CSV PARSER
# -------------------------

def parse_excel_or_csv(path: Path) -> list[KPIRecord]:
    if path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    records = []

    cols = {c.lower().strip(): c for c in df.columns}

    for _, row in df.iterrows():
        metric = str(row.get(cols.get("metric", ""), "")).lower() or "unknown_metric"

        actual = safe_float(row.get(cols.get("actual", ""), None))
        target = safe_float(row.get(cols.get("target", ""), None))

        variance = None
        if actual is not None and target is not None:
            variance = actual - target

        records.append(KPIRecord(
            date=str(row.get(cols.get("date", ""), "")) or None,
            store=extract_store(str(row.get(cols.get("store", ""), ""))),
            department=str(row.get(cols.get("department", ""), "")).lower() or None,
            metric=metric,
            actual=actual,
            target=target,
            variance=variance,
            status=status(actual, target),
            source=str(path.name),
            confidence_score=0.9
        ))

    return records


# -------------------------
# TEXT PARSER (FOR OCR / PASTE)
# -------------------------

def parse_text_blob(text: str) -> list[KPIRecord]:
    records = []
    lines = text.split("\n")

    for line in lines:
        line_clean = line.lower()

        store = extract_store(line_clean)
        metric = extract_metric(line_clean)

        numbers = re.findall(r"\d+\.?\d*", line_clean)

        if len(numbers) >= 2:
            actual = float(numbers[0])
            target = float(numbers[1])

            variance = actual - target

            records.append(KPIRecord(
                date=None,
                store=store,
                department=None,
                metric=metric,
                actual=actual,
                target=target,
                variance=variance,
                status=status(actual, target),
                source="text",
                confidence_score=0.7
            ))

    return records


# -------------------------
# HELPERS
# -------------------------

def extract_store(text: str):
    match = re.search(r"store\s*\d+", text)
    return match.group(0) if match else None


def extract_metric(text: str):
    for metric in KNOWN_METRICS:
        if metric in text:
            return metric
    return "unknown_metric"


def safe_float(value):
    try:
        return float(value)
    except:
        return None


def status(actual, target):
    if actual is None or target is None:
        return "unknown"
    return "off_track" if actual > target else "on_track"
