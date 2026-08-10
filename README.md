# Construction AI Foundation (Phase 1 Base)

> **Core Foundation & Architecture Standard for Construction AI Copilot**
> 
> *Dự án Nền tảng AI Dự toán & Quản lý Xây dựng — Bóc tách Kiến trúc & Domain Engine Chuẩn Việt Nam.*

---

## 🎯 Mục đích dự án (Project Objective)

Thư mục `construction-ai-foundation` đóng vai trò là **nền tảng sạch (Clean Foundation)** được bóc tách từ repository `Construction-AI-Copilot-2`. Thư mục này loại bỏ hoàn toàn các fake services (RAG fake, Geo fake, BIM fake, Price Ingestion fake), loại bỏ code không đạt chuẩn production và tổng hợp lại các thành phần có giá trị cốt lõi:

1. **LangGraph Multi-Agent Patterns**: Mẫu thiết kế phân luồng xử lý song song (Map-Reduce Send API) và cổng tương tác con người (HITL Confirmation Gate).
2. **Deterministic TCVN Math & BOQ Schemas**: Hệ thống Pydantic Schemas được định nghĩa chặt chẽ để phục vụ bóc tách khối lượng và dự toán chi phí theo chuẩn TCVN.
3. **Domain Knowledge & Engineering Guidance**: Bộ tài liệu kiến trúc, danh mục TCVN/QCVN áp dụng, và các quy trình kiểm thử Golden Master.
4. **Refactor Audit Log**: Lưu trữ code cũ bị lỗi logic toán học/kiến trúc để phục vụ tái cấu trúc ở Phase 1 & 2.

---

## 📁 Cấu trúc Thư mục (Directory Structure)

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
├── _reference_needs_rewrite/       # Thư mục lưu trữ code cũ cần Refactor (KHÔNG chạy)
│   ├── REFACTOR_NOTES.md           # Báo cáo chi tiết lỗi logic toán học & thiết kế cũ
│   ├── construction_math_old.py    # Code tính toán GFA & BOQ cũ (chứa lỗi nhân trùng)
│   ├── concept_architect_old.py    # Agent lập kế hoạch cũ
│   └── risk_auditor_old.py         # Agent kiểm định rủi ro cũ
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

---

## 📄 Giấy phép & Quy tắc Đóng góp (License & Guidelines)

Dự án này là mã nguồn nền tảng được quản lý theo quy trình Domain-Driven Design (DDD) và Test-Driven Development (TDD) cho ngành xây dựng Việt Nam.
