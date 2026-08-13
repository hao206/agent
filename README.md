# Construction AI Copilot

> **Student Prototype for AI-Assisted Construction Estimation**
>
> A student-built research prototype exploring how LLMs, structured data models, deterministic calculations, and workflow orchestration can support preliminary construction estimation.

---

## 📌 Project Status

**Student Prototype / Educational Demo**

This project is a personal computer science student prototype. It is **not** a production-grade construction management platform, certified engineering software, or legal compliance verification system.

---

## 💡 What This Project Does

- **Natural Language Parameter Extraction**: Uses local LLM (Qwen2.5) or cloud models via LangChain to convert Vietnamese user requests into structured Pydantic schemas (`ProjectBrief`).
- **Deterministic Cost & Volume Takeoff**: Computes Gross Floor Area (GFA), preliminary concrete volume, steel tonnage, brick counts, and cost breakdowns using standard testable Python math routines.
- **Rule-Based Preliminary Risk Screening**: Audits preliminary estimates against budget constraints and basic QCVN zoning heuristics to highlight potential risks early.
- **Human-in-the-Loop Confirmation**: Pauses workflow execution state (`WAITING_HITL` / `DECISION_BLOCKED`) allowing users to review and adjust parameters before calculation.

---

## 🔄 Demo Workflow

```text
User Input (Natural Language)
        │
        ▼
   [ Planner Node ] ────────► Structured ProjectBrief Schema
        │
        ▼
[ Risk Auditor Node ] ──────► Preliminary Warning / QCVN Check
        │
        ▼
 [ Math Engine Node ] ──────► Deterministic BOQ & Cost Estimate
        │
        ▼
  Result Output & Streamlit UI
```

---

## 🏗️ Architecture

```mermaid
graph TD
    subgraph Client Layer
        UI[Streamlit Web UI]
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

### Active Processing Nodes
1. **Planner Node (`src/foundation/agents/planner.py`)**: Extracts parameters (`location`, `land_area_m2`, `num_floors`, `quality_tier`, `budget_vnd`) into `ProjectBrief`.
2. **Risk Auditor Node (`src/foundation/agents/risk_auditor.py`)**: Runs preliminary rule-based screening for QCVN height/density rules and budget limits.
3. **Math Engine Node (`src/math_engine.py`)**: Runs deterministic Python formulas to produce the preliminary `BillOfQuantitiesSummary`.

---

## 🛠️ Key Technical Ideas

- **Pydantic V2 Schemas**: Strict data validation and `@computed_field` serialization for transparent data handling.
- **LangGraph Workflow**: StateGraph representation of agent transitions and HITL confirmation states.
- **Deterministic Math Engine**: Separates non-probabilistic arithmetic from probabilistic LLM reasoning.
- **TCVN-Informed Heuristics**: References Vietnamese construction practices for illustrative preliminary cost ratios.

---

## 📝 Example

### User Input
> *"Tôi muốn xây nhà phố 3 tầng 100m² tại Hà Nội, gói trung cấp, ngân sách 2.8 tỷ."*

### Structured Output Summary
- **GFA (Gross Floor Area)**: `400.0 m²` (Móng 50m² + 3 Sàn 300m² + Mái 50m²)
- **Bê tông dự kiến**: `140.0 m³` (0.35 m³/m² GFA assumption)
- **Thép dự kiến**: `40.0 tấn` (100 kg/m² GFA assumption)
- **Gạch dự kiến**: `32,000 viên` (80 viên/m² GFA assumption)
- **Tổng Dự Toán Ước Tính**: `2,755,500,000 VNĐ` (Đã bao gồm 5% dự phòng rủi ro thi công)

---

## 🚨 Limitations

> [!IMPORTANT]
> **Known Project Limitations:**
> - **Simplified Assumptions**: Ratios (100 kg steel/m², 0.35 m³ concrete/m², 80 bricks/m²) are illustrative demo figures and do **not** constitute structural engineering design values.
> - **Informational References Only**: TCVN/QCVN references in code/docs serve as educational domain context, not a certified compliance audit.
> - **No Replacement for Professionals**: Results are preliminary approximations and cannot replace licensed structural engineers, quantity surveyors, or official architectural blueprints.
> - **Static Cost Factors**: Unit prices and coefficients in the demo are static assumptions for demonstration purposes.

---

## 📁 Project Structure

```text
construction-ai-foundation/
├── README.md                           # Main documentation
├── pyproject.toml                      # Project metadata & dependencies
├── requirements.txt                    # Dependencies file
├── .env.example                        # Environment variables template
├── app.py                              # Streamlit Web UI Frontend
├── main.py                             # FastAPI Backend API
│
├── src/
│   ├── math_engine.py                  # Deterministic estimation math engine
│   ├── graph.py                        # LangGraph StateGraph workflow definition
│   └── foundation/
│       ├── llm_factory.py              # Qwen2.5 Local / ChatOllama factory
│       ├── agents/
│       │   ├── planner.py              # Planner & parameter extraction node
│       │   └── risk_auditor.py          # Preliminary risk auditor node
│       ├── schemas/
│       │   └── project_brief.py        # Pydantic V2 domain models
│       └── prompts/
│           └── concept_extractor.py    # Rule-based extraction system prompts
│
├── docs/
│   ├── architecture/                   # Architecture documentation
│   ├── domain/                         # Estimation logic & standard references
│   └── legacy/                         # Historical research notes & baseline code
│
└── tests/                              # Automated test suite
    ├── test_schemas.py                 # Pydantic schema tests
    ├── test_math_engine.py             # Math engine unit tests
    ├── test_risk_auditor.py            # Risk auditor screening tests
    └── patterns/
        └── golden_master_example.py    # Golden Master baseline cost test
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python `>= 3.10`
- (Optional) [Ollama](https://ollama.com/) running locally for Qwen2.5 model execution.

### Environment Setup
```powershell
# Clone repository
git clone https://github.com/hao206/agent.git
cd construction-ai-foundation

# Create & activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Copy `.env.example` to `.env` and set your local model/API parameters:
```powershell
cp .env.example .env
```

---

## 🚀 Running the Prototype

### Run Streamlit UI
```powershell
streamlit run app.py
```

### Run FastAPI Backend
```powershell
uvicorn main:app --reload
```

---

## 🧪 Testing

Run the automated test suite using Python `unittest`:
```powershell
python -m unittest discover tests
```

Run Golden Master test directly:
```powershell
python -m unittest tests/patterns/golden_master_example.py
```

---

## 🔮 Future Improvements

- **Specialist Domain Agents**: Integration of dynamic external market pricing APIs (Material Agent, Labor Agent).
- **Persistent Workflow State**: Database checkpointer for multi-session LangGraph state restoration.
- **BIM / IFC File Integration**: Direct takeoff extraction from 3D IFC/Revit building models.
- **Document Export**: Automated PDF/Excel BOQ export generation.

---

## 👤 Author

**Student / Personal Project** — Computer Science Research Prototype.

---

## ⚠️ Disclaimer

*This prototype is developed strictly for academic and educational demonstration purposes. All cost estimations, material takeoff quantities, and risk screening alerts are preliminary approximations generated from simplified demo rules. They must not be used for actual construction contracting, financial commitments, structural design, or legal regulatory compliance.*
