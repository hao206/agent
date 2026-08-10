# Audit & Refactor Notes (Lưu ý Tái cấu trúc)

> **CẢNH BÁO**: Các file trong thư mục `_reference_needs_rewrite/` CHỈ DÙNG ĐỂ THAM KHẢO VÀ PHÂN TÍCH LỖI LOGIC. KHÔNG NÊN CHẠY HOẶC SỬ DỤNG TRỰC TIẾP TRONG PRODUCTION.

---

## 1. `construction_math_old.py` (Lỗi logic toán học & tính trùng chi phí)

### Lỗi 1: Tính trùng chi phí Hoàn thiện (Finishing) & Nhân công (Labor) cho Móng & Mái
- **Hiện trạng trong code cũ**:
  - `total_gfa = foundation_area + floors_area + roof_area`
  - `finishing_cost = gfa * prices["finishing"]`
  - `labor_cost = gfa * prices["labor"]`
- **Nguyên nhân lỗi**:
  Hệ số móng (ví dụ: móng băng $K_{\text{foundation}} = 0.50$) và mái (ví dụ: mái tôn $K_{\text{roof}} = 0.30$) được tính cộng vào `GFA`. Khi nhân đơn giá hoàn thiện (sơn, gạch ốp, thiết bị) và nhân công hoàn thiện với toàn bộ `GFA`, hệ thống đã **tính chi phí hoàn thiện nội thất cho cả phần móng dưới đất và diện tích mái tôn**!
- **Phương án Refactor**:
  Chi phí hoàn thiện (`finishing_cost`) và nhân công (`labor_cost`) chỉ được tính trên **diện tích sàn sử dụng thực tế** ($\text{Land Area} \times N_{\text{floors}}$), không nhân trên hệ số quy đổi móng/mái của GFA.

### Lỗi 2: Tính 5% Dự phòng rủi ro (Contingency) trùm lên Phí Giấy phép Xây dựng
- **Hiện trạng trong code cũ**:
  `subtotal = foundation_cost + structure_rough_cost + finishing_cost + labor_cost + permits_cost_vnd`
  `contingency_cost = subtotal * 0.05`
- **Nguyên nhân lỗi**:
  Chi phí pháp lý / giấy phép hành chính ($15,000,000$ VND) là chi phí cố định (fixed baseline administrative fee), không có biến động vật tư hay biến thiên theo rủi ro thi công.
- **Phương án Refactor**:
  `contingency_cost` chỉ bằng $5\%$ tổng chi phí thi công xây dựng (`foundation + rough + finishing + labor`), không cộng phí pháp lý vào subtotal tính % dự phòng.

---

## 2. `concept_architect_old.py` (Lỗi thiết kế Agent & Xử lý fallback)

### Lỗi 1: Trích xuất thiếu fallback validation
- **Hiện trạng**: Sử dụng `get_llm().with_structured_output(ProjectBrief)` mà không có guardrails kiểm định giới hạn vật lý (như số tầng < 1 hoặc diện tích < 1m²).
- **Phương án Refactor**:
  Đưa Pydantic `field_validator` / `model_validator` vào `ProjectBrief` để tự động normalize dữ liệu hoặc raise error trước khi chốt plan.

### Lỗi 2: Hardcode các steps chạy song song
- **Hiện trạng**: Các steps luôn bị gán cứng `["material_agent", "labor_agent", "curing_agent", "zoning_agent"]` mà không điều chỉnh theo loại hình công trình (ví dụ: cải tạo nội thất không cần `curing_agent` đổ bê tông móng).
- **Phương án Refactor**: Dynamic step generation dựa trên `construction_type` và `functional_requirements`.

---

## 3. `risk_auditor_old.py` (Lỗi logic QA Audit & Giới hạn vòng lặp)

### Lỗi 1: Ép qua QA (Forcing pass) sau 2 lần sửa đổi
- **Hiện trạng**:
  ```python
  if revision_count > 2:
      return {"needs_revision": False, ...}
  ```
- **Nguyên nhân lỗi**:
  Khi rủi ro vi phạm pháp lý QCVN (như xây quá số tầng hoặc quá mật độ) nghiêm trọng, việc tự động "cho qua" sau 2 lần retry sẽ khiến hệ thống trả về báo cáo sai luật cho người dùng.
- **Phương án Refactor**:
  Nút thắt vi phạm quy hoạch / pháp lý nghiêm trọng PHẢI gắn cờ `decision_blocked` hoặc chuyển về cổng HITL yêu cầu người dùng cắt giảm tầng/diện tích thay vì tự động ép pass.
