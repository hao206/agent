# Construction AI Foundation (Phase 1 Base)

> **Core Foundation & Architecture Standard for Construction AI Copilot**
> 
> *Dự án Nền tảng AI Dự toán & Quản lý Xây dựng — Kiến trúc Nòng nốt & Domain Engine Chuẩn Việt Nam.*

---

##  Mục đích dự án (Project Objective)

Dự án `construction-ai-foundation` đóng vai trò là **nền tảng kiến trúc sạch (Clean Production Foundation)** được thiết kế và phát triển cho hệ thống AI Dự toán & Quản lý Xây dựng. Hệ thống tập trung hoàn toàn vào các thành phần có giá trị thực tế cao, chuẩn hóa dữ liệu và sẵn sàng cho môi trường Production:

1. **LangGraph Multi-Agent Patterns**: Mẫu thiết kế phân luồng xử lý song song (Map-Reduce Send API) và cổng tương tác con người (HITL Confirmation Gate).
2. **Deterministic TCVN Math & BOQ Schemas**: Hệ thống Pydantic Schemas được định nghĩa chặt chẽ để phục vụ bóc tách khối lượng và dự toán chi phí theo chuẩn TCVN.
3. **Domain Knowledge & Engineering Guidance**: Bộ tài liệu kiến trúc, danh mục TCVN/QCVN áp dụng, và các quy trình kiểm thử Golden Master.
4. **Audit & Reference Notes**: Phân tích chuyên sâu các mẫu thuật toán cũ và lưu vết giải pháp tối ưu hóa qua từng giai đoạn.

---

## Cấu trúc Thư mục (Directory Structure)

```text
construction-ai-foundation/
├── README.md                       # Tài liệu hướng dẫn chính
├── pyproject.toml                  # Khai báo dependencies tối giản
├── .gitignore                      # Git ignore rules cho Python/Environment
├── .env.example                    # Mẫu cấu hình môi trường (LLM API keys)
│
├── docs/                           # Tài liệu Kiến trúc & Domain
│   ├── architecture/
│   │   ├── system-overview.md      # Tổng quan kiến trúc hệ thống Multi-Agent
│   │   └── agent-responsibilities.md# Chi tiết trách nhiệm từng Agent
│   ├── domain/
│   │   ├── construction-logic.md   # Công thức bóc tách khối lượng & GFA theo TCVN
│   │   └── tcvn-references.md      # Danh mục Tiêu chuẩn Kỹ thuật Việt Nam áp dụng
│   └── decisions/                  # Các ADRs (Architecture Decision Records)
│       ├── 0001-package-src-layout.md
│       └── 0002-product-harness.md
│
├── src/foundation/                 # Mã nguồn nòng nốt & Schemas
│   ├── __init__.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── project_brief.py        # Pydantic models chuẩn cho ProjectBrief, BOQ, Risk
│   ├── patterns/                   # Hướng dẫn & Mã tham khảo LangGraph Patterns
│   │   ├── __init__.py
│   │   ├── langgraph_parallel.md   # Pattern chạy agent song song (Map-Reduce)
│   │   └── hitl_gate.md            # Pattern HITL interrupt/resume
│   └── prompts/
│       ├── __init__.py
│       └── concept_extractor.py    # System prompts chuẩn cho intent & extraction
│
├── checklists/                     # Quy trình kiểm thử & Đảm bảo chất lượng
│   ├── backend-change.md
│   ├── frontend-change.md
│   └── demo-validation.md
│
├── _reference_needs_rewrite/       # Module tham khảo & Lưu vết phân tích thuật toán
│   ├── REFACTOR_NOTES.md           # Ghi chú phân tích chuyên sâu & Hướng giải pháp tối ưu
│   ├── construction_math_old.py    # Baseline Engine tính toán GFA & BOQ thử nghiệm
│   ├── concept_architect_old.py    # Baseline Agent lập kế hoạch thử nghiệm
│   └── risk_auditor_old.py         # Baseline Agent kiểm định rủi ro thử nghiệm
│
└── tests/                          # Hệ thống kiểm thử
    ├── README.md                   # Chiến lược kiểm thử & Golden Master test
    └── patterns/
        └── golden_master_example.py# Mã nguồn ví dụ Golden Master Cost Test
```

---

## 🛠️ Yêu cầu & Cài đặt (Requirements & Setup)

- **Python**: `>= 3.10`
- **Dependencies chính**: `pydantic>=2.0.0`, `langgraph>=0.2.0`, `langchain-core>=0.3.0`, `pytest>=8.0.0`

Khởi tạo môi trường ảo và cài đặt:

```bash
python -m venv .venv
source .venv/bin/activate  # Hoặc .venv\Scripts\activate trên Windows
pip install -e .
```

Kiểm tra cú pháp code:

```bash
python -m compileall src tests
pytest tests/
```

