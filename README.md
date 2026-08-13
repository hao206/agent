# Construction AI Copilot
---

## Chức năng chính 

- **Trích xuất Thông số từ Ngôn ngữ Tự nhiên**: Sử dụng Local LLM (Qwen2.5) hoặc các mô hình Cloud thông qua LangChain để chuyển đổi câu hỏi tiếng Việt của người dùng thành Pydantic Schema chuẩn hóa (`ProjectBrief`).
- **Bóc tách Khối lượng & Khái toán Chi phí Deterministic**: Tính toán diện tích sàn quy đổi (GFA), thể tích bê tông sơ bộ, khối lượng thép, số lượng gạch và phân rã chi phí bằng các hàm toán học Python độc lập, dễ kiểm thử.
- **Sơ bộ Cảnh báo Rủi ro Dựa trên Quy tắc**: Đánh giá sơ bộ dự toán so với ngân sách và áp dụng các quy tắc heuristics dựa trên QCVN 01:2021/BXD để phát hiện sớm các nguy cơ rủi ro.
- **Cổng Xác nhận Con người (HITL - Human-in-the-Loop)**: Tạm dừng luồng xử lý (`WAITING_HITL` / `DECISION_BLOCKED`), cho phép người dùng kiểm tra và điều chỉnh thông số trước khi chạy engine tính toán.

---

## Demo Workflow

```text
Yêu cầu Người dùng (Ngôn ngữ Tự nhiên)
        │
        ▼
   [ Planner Node ] ────────► Structured ProjectBrief Schema
        │
        ▼
[ Risk Auditor Node ] ──────► Sơ bộ Cảnh báo Rủi ro / Quy chuẩn
        │
        ▼
 [ Math Engine Node ] ──────► BOQ & Khái toán Chi phí Deterministic
        │
        ▼
  Kết quả Báo cáo & Streamlit UI
```

---

##  Kiến trúc Hệ thống (Architecture)

```mermaid
graph TD
    subgraph Client Layer
        UI[Streamlit Web UI - app.py]
    end

    subgraph API Layer
        API[FastAPI Router - main.py]
    end

    subgraph Multi-Agent Graph Layer - src/graph.py
        Planner[Planner Node - Qwen2.5 / LLM]
        Auditor[Risk Auditor Node - Rule Screening]
        Engine[Deterministic Estimation Engine]
    end

    UI --> API
    UI <--> Multi-Agent Graph Layer
    API <--> Multi-Agent Graph Layer
```

### Các Processing Nodes Đang Hoạt động
1. **Planner Node (`src/foundation/agents/planner.py`)**: Trích xuất các thông số công trình (`location`, `land_area_m2`, `num_floors`, `quality_tier`, `budget_vnd`) vào `ProjectBrief`.
2. **Risk Auditor Node (`src/foundation/agents/risk_auditor.py`)**: Chạy kiểm định sơ bộ theo quy tắc mật độ/số tầng (QCVN) và giới hạn ngân sách.
3. **Math Engine Node (`src/math_engine.py`)**: Chạy các công thức toán học Python deterministic để xuất ra `BillOfQuantitiesSummary`.

---

##  Ý tưởng Kỹ thuật Nòng cốt

- **Pydantic V2 Schemas**: Đảm bảo kiểm tra kiểu dữ liệu nghiêm ngặt và tự động serialize các trường `@computed_field`.
- **LangGraph Workflow**: Mô hình hóa luồng thực thi và các trạng thái tạm dừng xác nhận con người (HITL) bằng StateGraph.
- **Deterministic Math Engine**: Tách biệt hoàn toàn tính toán đại số (không xác suất) khỏi suy luận của LLM (có xác suất).
- **TCVN-Informed Heuristics**: Tham khảo các hệ số thi công thực tế tại Việt Nam phục vụ mục đích minh họa khái toán sơ bộ.

---

## Example

### Đầu vào (User Input)
> *"Tôi muốn xây nhà phố 3 tầng 100m² tại Hà Nội, gói trung cấp, ngân sách 2.8 tỷ."*

### Kết quả Khái toán Sơ bộ
- **Diện tích sàn quy đổi (GFA)**: `400.0 m²` (Móng 50m² + 3 Sàn 300m² + Mái 50m²)
- **Thể tích Bê tông dự kiến**: `140.0 m³` (Giả định demo: 0.35 m³/m² GFA)
- **Khối lượng Thép dự kiến**: `40.0 tấn` (Giả định demo: 100 kg/m² GFA)
- **Số lượng Gạch dự kiến**: `32,000 viên` (Giả định demo: 80 viên/m² GFA)
- **Tổng Dự Toán Ước Tính**: `2,834,250,000 VNĐ` (Đã bao gồm 5% dự phòng rủi ro thi công)

---

## Giới hạn 

> [!IMPORTANT]
> **Các giới hạn quan trọng cần lưu ý:**
> - **Giả định Đơn giản hóa**: Các tỷ lệ minh họa (100 kg thép/m², 0.35 m³ bê tông/m², 80 viên gạch/m²) là các số liệu demo sơ bộ, **không phải** số liệu tính toán thiết kế kết cấu chuyên ngành.
> - **Chỉ mang Tính chất Tham khảo Thông tin**: Các tham chiếu TCVN/QCVN đóng vai trò là ngữ cảnh domain học thuật, **không phải** báo cáo thẩm định quy hoạch pháp lý chính thức.
> - **Không Thay thế Chuyên gia**: Kết quả chỉ mang tính chất khái toán ước tính ban đầu, không thay thế cho Kỹ sư Kết cấu, Kỹ sư Dự toán (QS), hoặc bản vẽ thiết kế thi công chính thức.
> - **Đơn giá Cố định**: Đơn giá và các hệ số trong demo được cố định phục vụ mục đích minh họa.

---

## Cấu trúc Thư mục (Project Structure)

```text
construction-ai-foundation/
├── README.md                           # Tài liệu hướng dẫn 
├── pyproject.toml                      # Cấu hình project & dependencies
├── requirements.txt                    # Danh sách thư viện phụ thuộc
├── .env.example                        # Mẫu biến môi trường
├── app.py                              # Streamlit Web UI Frontend
├── main.py                             # FastAPI Backend API
│
├── src/
│   ├── math_engine.py                  # Engine tính toán khái toán deterministic
│   ├── graph.py                        # Định nghĩa luồng LangGraph StateGraph
│   └── foundation/
│       ├── llm_factory.py              # LLM Factory (Qwen2.5 Local / ChatOllama)
│       ├── agents/
│       │   ├── planner.py              # Agent trích xuất thông số & lập kế hoạch
│       │   └── risk_auditor.py          # Agent kiểm định rủi ro sơ bộ
│       ├── schemas/
│       │   └── project_brief.py        # Pydantic V2 Domain Schemas
│       └── prompts/
│           └── concept_extractor.py    # System prompts trích xuất thông tin
│
├── docs/
│   ├── architecture/                   # Tài liệu kiến trúc hệ thống
│   ├── domain/                         # Phương pháp tính toán & tham chiếu TCVN
│   └── legacy/                         # Ghi chú nghiên cứu lịch sử & code baseline
│
└── tests/                              # Bộ kiểm thử tự động
    ├── test_schemas.py                 # Unit test kiểm tra Pydantic schema
    ├── test_math_engine.py             # Unit test kiểm tra Math Engine
    ├── test_risk_auditor.py            # Unit test kiểm tra Risk Auditor
    └── patterns/
        └── golden_master_example.py    # Integration test Golden Master cost
```

---

## Setup & Installation

### Yêu cầu Tiền đề
- Python `>= 3.10`
- (Tùy chọn) [Ollama](https://ollama.com/) chạy mô hình local `qwen2.5:32b-instruct-q4_K_M`.

### Khởi tạo Môi trường
```powershell
# Clone repository
git clone https://github.com/hao206/agent.git
cd construction-ai-foundation

# Tạo và kích hoạt môi trường ảo Python
python -m venv .venv
.\.venv\Scripts\activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### Cấu hình Môi trường
Tạo file `.env` từ file `.env.example`:
```powershell
cp .env.example .env
```

---


## Testing

Chạy bộ unit test tự động bằng `unittest`:
```powershell
python -m unittest discover tests
```

Chạy trực tiếp Golden Master test:
```powershell
python -m unittest tests/patterns/golden_master_example.py
```
