from foundation.schemas.project_brief import ConstructionCostBreakdown, DecisionOutput

def calculate_construction_cost_breakdown(
    land_area_m2: float, 
    num_floors: int, 
    foundation_type: str, 
    roof_type: str, 
    quality_tier: str
) -> ConstructionCostBreakdown:
    """
    Deterministic Math Engine - Tuân thủ nghiêm ngặt REFACTOR_NOTES.md
    """
    # 1. Đơn giá cơ sở (Hardcoded cho Demo, thực tế sẽ gọi MaterialAgent/LaborAgent)
    prices = {
        "budget": {"rough": 3_000_000, "finishing": 1_800_000, "labor": 1_200_000, "foundation_coeff": 0.3},
        "medium": {"rough": 3_600_000, "finishing": 2_400_000, "labor": 1_500_000, "foundation_coeff": 0.5},
        "premium": {"rough": 4_500_000, "finishing": 3_500_000, "labor": 2_000_000, "foundation_coeff": 0.7},
    }
    p = prices[quality_tier]

    # 2. Tính diện tích (GFA vs Usable Area)
    usable_area = land_area_m2 * num_floors # Diện tích sàn sử dụng thực tế
    
    # FIX LỖI 1: Hệ số móng/mái chỉ áp dụng cho PHẦN THÔ, KHÔNG áp dụng cho Hoàn thiện/Nhân công
    foundation_area = land_area_m2 * p["foundation_coeff"]
    roof_area = land_area_m2 * 0.3 # Giả sử hệ số mái trung bình 30%
    
    # 3. Bóc tách chi phí (VND)
    # Móng & Thô tính trên GFA quy đổi (Móng + Sàn + Mái)
    total_structural_area = foundation_area + usable_area + roof_area
    foundation_vnd = foundation_area * p["rough"] # Đơn giản hóa
    structure_rough_vnd = usable_area * p["rough"]
    
    # Hoàn thiện & Nhân công CHỈ TÍNH TRÊN DIỆN TÍCH SÀN SỬ DỤNG (Không tính cho móng/mái)
    finishing_vnd = usable_area * p["finishing"]
    labor_vnd = (usable_area + foundation_area) * p["labor"] # Nhân công có làm móng
    
    permits_legal_vnd = 15_000_000 # Chi phí cố định
    
    # FIX LỖI 2: Dự phòng 5% chỉ tính trên chi phí thi công, KHÔNG tính trên phí pháp lý
    construction_subtotal = foundation_vnd + structure_rough_vnd + finishing_vnd + labor_vnd
    contingency_vnd = construction_subtotal * 0.05 

    return ConstructionCostBreakdown(
        foundation_vnd=round(foundation_vnd, 0),
        structure_rough_vnd=round(structure_rough_vnd, 0),
        finishing_vnd=round(finishing_vnd, 0),
        labor_vnd=round(labor_vnd, 0),
        permits_legal_vnd=permits_legal_vnd,
        contingency_vnd=round(contingency_vnd, 0)
    )