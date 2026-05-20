from pathlib import Path
import re
import pandas as pd
from app.models.schemas import KPIRecord

# -------------------------
# KNOWN MAPPINGS (NORMALIZATION)
# -------------------------

METRIC_MAP = {
    "sales": ["sales", "revenue", "rev"],
    "labor": ["labor", "hrs", "hours"],
    "shrink": ["shrink", "loss"],
    "service": ["service", "osat"],
    "oos": ["oos", "out of stock"],
    "forecast": ["forecast"],
}

DEPARTMENT_MAP = {
    "produce": ["produce"],
    "meat": ["meat"],
    "deli": ["deli"],
    "bakery": ["bakery"],
    "grocery": ["grocery"],
    "dairy": ["dairy"],
    "front end": ["front end", "frontend", "fe"],
}

# -------------------------
# MAIN ENTRY
# -------------------------

def parse_file(path: Path) -> list[KPIRecord]:
    suffix = path.suffix.lower()

    if suffix in [".xlsx", ".xls", ".csv"]:
        return parse_excel_or_csv(path)

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
        raw_metric = str(row.get(cols.get("metric", ""), "")).lower()
        metric = normalize_metric(raw_metric)

        actual = safe_float(row.get(cols.get("actual", ""), None))
        target = safe_float(row.get(cols.get("target", ""), None))

        variance = compute_variance(actual, target)

        records.append(KPIRecord(
            date=str(row.get(cols.get("date", ""), "")) or None,
            store=extract_store(str(row.get(cols.get("store", ""), ""))),
            department=normalize_department(str(row.get(cols.get("department", ""), ""))),
            metric=metric,
            actual=actual,
            target=target,
            variance=variance,
            status=status(metric, actual, target),
            source=str(path.name),
            confidence_score=0.95
        ))

    return records


# -------------------------
# TEXT PARSER (OCR / PASTE)
# -------------------------

def parse_text_blob(text: str) -> list[KPIRecord]:
    records = []
    lines = text.split("\n")

    for line in lines:
        clean = line.lower().strip()

        store = extract_store(clean)
        metric = normalize_metric(clean)
        department = normalize_department(clean)

        numbers = re.findall(r"\d+\.?\d*", clean)

        if len(numbers) >= 2:
            actual = float(numbers[0])
            target = float(numbers[1])
            variance = compute_variance(actual, target)

            records.append(KPIRecord(
                date=None,
                store=store,
                department=department,
                metric=metric,
                actual=actual,
                target=target,
                variance=variance,
                status=status(metric, actual, target),
                source="ocr_text",
                confidence_score=0.75
            ))

    return records


# -------------------------
# NORMALIZATION
# -------------------------

def normalize_metric(text: str) -> str:
    for key, values in METRIC_MAP.items():
        for v in values:
            if v in text:
                return key
    return "unknown_metric"


def normalize_department(text: str):
    for key, values in DEPARTMENT_MAP.items():
        for v in values:
            if v in text:
                return key
    return None


# -------------------------
# HELPERS
# -------------------------

def extract_store(text: str):
    match = re.search(r"store\s*\d+", text)
    return match.group(0) if match else None


def safe_float(value):
    try:
        return float(value)
    except:
        return None


def compute_variance(actual, target):
    if actual is None or target is None:
        return None
    return actual - target


def status(metric, actual, target):
    if actual is None or target is None:
        return "unknown"

    # Some metrics are better higher (sales), some lower (labor/shrink)
    if metric in ["sales"]:
        return "off_track" if actual < target else "on_track"
    else:
        return "off_track" if actual > target else "on_track"
