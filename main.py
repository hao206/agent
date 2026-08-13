from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.foundation.schemas.project_brief import ProjectBrief
from src.math_engine import calculate_construction_cost_breakdown

app = FastAPI(
    title="Construction AI Backend",
    description="Backend API for Construction AI Copilot - Local Qwen2.5 & TCVN Math Engine",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Construction AI Math Engine & Qwen2.5 Copilot"}


@app.post("/api/estimate")
def estimate_project(brief: ProjectBrief):
    """
    Endpoint nhận dữ liệu từ Frontend và chạy TCVN Math Engine
    """
    land_area = brief.land_area_m2 or 100.0
    floors = brief.num_floors or 3

    boq_summary = calculate_construction_cost_breakdown(
        land_area_m2=land_area,
        num_floors=floors,
        foundation_type=brief.foundation_type,
        roof_type=brief.roof_type,
        quality_tier=brief.quality_tier,
    )

    return {
        "status": "success",
        "project_brief": brief.model_dump(),
        "boq_summary": boq_summary.model_dump(),
        "cost_breakdown": boq_summary.cost_breakdown.model_dump(),
    }