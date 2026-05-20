from pathlib import Path
import re
import pandas as pd
from app.models.schemas import KPIRecord

# -------------------------
# NORMALIZATION MAPS
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
    if path.suffix.lower() in [".xlsx", ".xls", ".csv"]:
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

    for _, row in df.iterrows():
        # Combine entire row into one string
        raw_row = " ".join([str(v) for v in row.values]).lower()

        # Extract numbers
        numbers = re.findall(r"\d+\.?\d*", raw_row)

        # 🚨 FILTER OUT JUNK ROWS
        if len(numbers) < 2:
            continue

        actual = float(numbers[0])
        target = float(numbers[1])

        variance = compute_variance(actual, target)

        metric = normalize_metric(raw_row)
        department = normalize_department(raw_row)
        store = extract_store(raw_row)

        # 🚨 Skip useless rows
        if metric == "unknown_metric":
            continue

        records.append(KPIRecord(
            date=None,
            store=store,
            department=department,
            metric=metric,
            actual=actual,
            target=target,
            variance=variance,
            status=status(metric, actual, target),
            source=str(path.name),
            confidence_score=0.9
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

        numbers = re.findall(r"\d+\.?\d*", clean)

        if len(numbers) < 2:
            continue

        actual = float(numbers[0])
        target = float(numbers[1])

        variance = compute_variance(actual, target)

        metric = normalize_metric(clean)
        department = normalize_department(clean)
        store = extract_store(clean)

        if metric == "unknown_metric":
            continue

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
    match = re.search(r"\b\d{3,5}\b", text)
    return match.group(0) if match else None


def compute_variance(actual, target):
    return actual - target if actual is not None and target is not None else None


def status(metric, actual, target):
    if actual is None or target is None:
        return "unknown"

    # Higher is better
    if metric in ["sales"]:
        return "off_track" if actual < target else "on_track"

    # Lower is better
    return "off_track" if actual > target else "on_track"
