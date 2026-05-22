# DistrictOS Capture Architecture

## Intake Modes

1. Picture/screenshot upload
2. File upload
3. Review-session recording upload
4. Pasted text/table intake

## Privacy Defaults

- Recording is user initiated only.
- Visible recording indicator is required.
- No silent capture.
- Sensitive text is redacted locally before analysis where possible.
- Raw recordings are deleted after frame extraction.
- Saved data is limited to cleaned KPI records and summaries.
- User review is required for low-confidence records.

## Standard KPI Schema

```text
date
store
department
metric
actual
target
variance
status
source
confidence_score
```

## Build Priority

The moat is not the dashboard.
The moat is the messy-data translation layer.
