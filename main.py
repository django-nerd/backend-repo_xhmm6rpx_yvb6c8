import os
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Model as ModelSchema, Pipeline as PipelineSchema, Dataset as DatasetSchema, Job as JobSchema

app = FastAPI(title="AI Hijabi Model Studio API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "AI Hijabi Model Studio API is running"}


@app.get("/test")
def test_database():
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:  # pragma: no cover
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:  # pragma: no cover
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ---------------------------
# Schema exposure for tooling
# ---------------------------
class SchemaResponse(BaseModel):
    collections: List[Dict[str, Any]]


@app.get("/schema", response_model=SchemaResponse)
def get_schema():
    # Note: This is a lightweight reflection for the DB viewer tools
    return {
        "collections": [
            {"name": "model", "fields": list(ModelSchema.model_json_schema()["properties"].keys())},
            {"name": "pipeline", "fields": list(PipelineSchema.model_json_schema()["properties"].keys())},
            {"name": "dataset", "fields": list(DatasetSchema.model_json_schema()["properties"].keys())},
            {"name": "job", "fields": list(JobSchema.model_json_schema()["properties"].keys())},
        ]
    }


# ---------------------------
# Minimal CRUD endpoints
# ---------------------------
@app.post("/models")
def create_model(payload: ModelSchema):
    inserted_id = create_document("model", payload)
    return {"id": inserted_id}


@app.get("/models")
def list_models():
    docs = get_documents("model")
    # Convert ObjectId to string for JSON
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}


@app.post("/pipelines")
def create_pipeline(payload: PipelineSchema):
    inserted_id = create_document("pipeline", payload)
    return {"id": inserted_id}


@app.get("/pipelines")
def list_pipelines():
    docs = get_documents("pipeline")
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}


@app.post("/jobs")
def create_job(payload: JobSchema):
    inserted_id = create_document("job", payload)
    return {"id": inserted_id, "status": payload.status}


@app.get("/jobs")
def list_jobs():
    docs = get_documents("job")
    for d in docs:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
    return {"items": docs}


# ---------------------------
# Stubs for generation engine
# ---------------------------
class GenerateRequest(BaseModel):
    model_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    task: str  # face | fullbody | angles360 | expression | background | dress
    promptless: bool = True
    params: Dict[str, Any] = {}


@app.post("/generate")
def generate_assets(req: GenerateRequest):
    # This is a placeholder that simulates a job enqueue.
    job = JobSchema(
        type=req.task if req.task in [
            "face", "fullbody", "angles360", "expression", "background", "dress"
        ] else "dataset",
        model_id=req.model_id,
        pipeline_id=req.pipeline_id,
        params=req.params or {},
        status="queued",
        progress=0,
    )
    job_id = create_document("job", job)
    return {"job_id": job_id, "status": "queued"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
