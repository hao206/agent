# Testing Strategy — Construction AI Foundation

> **Golden Master Pattern & Deterministic Engine Validation Strategy**

---

## 🎯 Chiến lược Kiểm thử (Testing Strategy)

Hệ thống **Construction AI Foundation** áp dụng 3 lớp kiểm thử chính để bảo đảm độ chính xác 100% trong dự toán và bóc tách khối lượng:

1. **Schema Validation Tests**: Kiểm tra tính toàn vẹn của Pydantic Models (`ProjectBrief`, `BOQItem`, `ConstructionCostBreakdown`, `DecisionOutput`). Đảm bảo dữ liệu đầu vào không bao giờ chứa thông số âm hoặc sai định dạng.
2. **Golden Master Regression Tests (`tests/patterns/golden_master_example.py`)**: 
   - Kiểm thử hồi quy dựa trên các kịch bản thực tế (Golden Cases): ví dụ nhà phố $100m^2$ 3 tầng, biệt thự $200m^2$ 2 tầng.
   - So sánh trực tiếp kết quả bóc tách khối lượng (bê tông $m^3$, thép tấn, gạch viên) và tổng chi phí dự toán với kết quả chuẩn ("Golden Master baseline").
   - Đảm bảo khi refactor toán engine trong tương lai, kết quả dự toán không bị sai lệch vô lý.
3. **Deterministic Math Bounds Tests**: Kiểm tra các trường hợp biên của thuật toán tính diện tích sàn GFA, hệ số móng, và hệ số mái.

---

## 🚀 Chạy Tests (Running Tests)

Chạy tất cả kiểm thử với `pytest`:

```bash
pytest tests/
```

Chạy riêng kiểm thử Golden Master:

```bash
pytest tests/patterns/golden_master_example.py -v
```

Kiểm tra độ phủ code (Code Coverage):

```bash
pytest --cov=src tests/
```
