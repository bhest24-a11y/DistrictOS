from fastapi import FastAPI
from app.api.routes import router
from app.db import engine
from app.models import Base

app = FastAPI(
    title="DistrictOS Capture + Intelligence",
    version="0.2.0",
    description="Messy data intake, redaction, KPI normalization, and operational intelligence."
)

Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "DistrictOS online", "module": "Capture + Intelligence"}
