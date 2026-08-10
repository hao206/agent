from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.foundation.schemas.project_brief import ProjectBrief
from src.math_engine import calculate_construction_cost_breakdown # Import từ Bước 2 hôm trước

app = FastAPI(title="Construction AI Backend")

# Cấu hình CORS để Frontend (Next.js trên Vercel) gọi được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Khi làm thật, hãy thay bằng domain Frontend của bạn
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "healthy", "service": "Construction AI Math Engine"}

@app.post("/api/estimate")
def estimate_project(brief: ProjectBrief):
    """
    Endpoint nhận dữ liệu từ Frontend và chạy Math Engine
    """
    # Gọi hàm tính toán Deterministic
    cost_breakdown = calculate_construction_cost_breakdown(
        land_area_m2=brief.land_area_m2,
        num_floors=brief.num_floors,
        foundation_type=brief.foundation_type,
        roof_type=brief.roof_type,
        quality_tier=brief.quality_tier
    )
    
    return {
        "status": "success",
        "project_brief": brief.model_dump(),
        "cost_breakdown": cost_breakdown.model_dump()
    }