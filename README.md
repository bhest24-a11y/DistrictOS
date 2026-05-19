# DistrictOS 3-Year MVP — Integrated Capture Build

This build adds the missing intake layer:

- Upload pictures/screenshots
- Upload Excel/CSV files
- Record/upload review sessions
- Extract frames from video
- Redact sensitive fields
- Convert inputs into standardized KPI records
- Generate district insights, risks, action plans, VP recap, and huddle script
- Delete raw recordings after extraction
- Store only cleaned KPI data and summaries

## Run

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
streamlit run frontend/streamlit_app.py
```

## Important

This MVP is designed for user-initiated capture only. It does not silently record screens.
