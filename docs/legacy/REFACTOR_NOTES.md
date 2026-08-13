# Technical Audit & Optimization Strategy (Báo cáo Phân tích & Hướng Tối ưu)

> **LƯU Ý THIẾT KẾ**: Các module trong thư mục `_reference_needs_rewrite/` đóng vai trò là mẫu tham khảo cho phiên bản thuật toán ban đầu (Baseline Experiments). Thư mục này phục vụ mục đích phân tích kỹ thuật và theo dõi quá trình tối ưu hóa logic qua các giai đoạn.

---

## 1. `construction_math_old.py` (Phân tích thuật toán toán học & công thức tính chi phí)

### Vấn đề 1: Công thức tính chi phí Hoàn thiện (Finishing) & Nhân công (Labor) cho Móng & Mái
- **Phân tích phiên bản ban đầu**:
  - `total_gfa = foundation_area + floors_area + roof_area`
  - `finishing_cost = gfa * prices["finishing"]`
  - `labor_cost = gfa * prices["labor"]`
- **Nguyên nhân hạn chế**:
  Hệ số móng (ví dụ: móng băng $K_{\text{foundation}} = 0.50$) và mái (ví dụ: mái tôn $K_{\text{roof}} = 0.30$) được tính cộng vào diện tích quy đổi `GFA`. Khi nhân đơn giá hoàn thiện (sơn, gạch ốp, thiết bị) và nhân công hoàn thiện với toàn bộ `GFA`, thuật toán ban đầu bị **tính trùng chi phí hoàn thiện nội thất cho cả phần móng dưới đất và mái tôn**.
- **Giải pháp tối ưu hóa**:
  Chi phí hoàn thiện (`finishing_cost`) và nhân công (`labor_cost`) chỉ tính trên **diện tích sàn sử dụng thực tế** ($\text{Land Area} \times N_{\text{floors}}$), không nhân trên hệ số quy đổi móng/mái của GFA.

### Vấn đề 2: Tỷ lệ Dự phòng rủi ro (Contingency) tính trên Phí Giấy phép Xây dựng
- **Phân tích phiên bản ban đầu**:
  `subtotal = foundation_cost + structure_rough_cost + finishing_cost + labor_cost + permits_cost_vnd`
  `contingency_cost = subtotal * 0.05`
- **Nguyên nhân hạn chế**:
  Chi phí pháp lý / giấy phép hành chính ($15,000,000$ VND) là chi phí cố định (fixed baseline administrative fee), không biến động theo vật tư hay rủi ro thi công.
- **Giải pháp tối ưu hóa**:
  `contingency_cost` được tính bằng $5\%$ tổng chi phí thi công trực tiếp (`foundation + rough + finishing + labor`), loại trừ chi phí pháp lý cố định khỏi subtotal tính % dự phòng.

---

## 2. `concept_architect_old.py` (Phân tích thiết kế Agent & Ràng buộc Validation)

### Vấn đề 1: Validation dữ liệu đầu vào & Guardrails
- **Phân tích phiên bản ban đầu**: Sử dụng `get_llm().with_structured_output(ProjectBrief)` mà không tích hợp guardrails kiểm định giới hạn vật lý (như số tầng < 1 hoặc diện tích < 1m²).
- **Giải pháp tối ưu hóa**:
  Tích hợp Pydantic `field_validator` và `model_validator` trực tiếp vào `ProjectBrief` để tự động chuẩn hóa dữ liệu và phát hiện bất hợp lý trước khi khởi tạo tiến trình.

### Vấn đề 2: Động hóa luồng thực thi song song (Dynamic Execution Dispatch)
- **Phân tích phiên bản ban đầu**: Luồng thực thi bị gán cố định `["material_agent", "labor_agent", "curing_agent", "zoning_agent"]` bất kể loại hình công trình.
- **Giải pháp tối ưu hóa**:
  Phát triển cơ chế tự động tạo danh sách bước (`steps`) dựa trên `construction_type` và `functional_requirements` thực tế của dự án.

---

## 3. `risk_auditor_old.py` (Phân tích kiểm định QA & Giới hạn vòng lặp)

### Vấn đề 1: Xử lý ngoại lệ vi phạm pháp lý & Quy hoạch
- **Phân tích phiên bản ban đầu**:
  ```python
  if revision_count > 2:
      return {"needs_revision": False, ...}
  ```
- **Nguyên nhân hạn chế**:
  Nếu công trình gặp vi phạm quy hoạch nghiêm trọng theo QCVN 01:2021/BXD (như vượt mật độ xây dựng hoặc số tầng tối đa), việc cho qua sau 2 lần thử sẽ tạo ra báo cáo không chính xác.
- **Giải pháp tối ưu hóa**:
  Cơ chế kiểm định phân loại rủi ro pháp lý thành lỗi chặn (`decision_blocked`) và tự động kích hoạt cổng HITL để người dùng chủ động điều chỉnh quy mô thay vì tự động ép thông qua.
