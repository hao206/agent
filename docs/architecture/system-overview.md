# Architecture Overview — Construction AI Copilot

## Overview

**Construction AI Copilot** is designed around a **Multi-Agent Supervisor StateGraph Architecture** powered by LangGraph, FastAPI, and Pydantic schemas.

```mermaid
graph TD
    subgraph Frontend Layer
        UI[React + Vite Workspace]
    end

    subgraph API Layer
        API[FastAPI Routers]
        Auth[Authentication & Session Service]
        Cache[Redis / Memory Cache Layer]
    end

    subgraph Multi-Agent Graph Layer
        Classify[Classify Intent Node]
        Architect[Concept Architect Agent]
        Gate{HITL Confirmation Gate}
        Supervisor[Project Manager Supervisor / Dispatcher]
        
        Material[Material Price Agent]
        Labor[Labor Rate Agent]
        Curing[Seasonality & Curing Agent]
        Zoning[Zoning Legal Agent]

        Auditor[Risk & QA Auditor Agent]
        Engine[Deterministic TCVN Math Engine]
        Response[Response Agent]
    end

    subgraph Persistence Layer
        DB[(PostgreSQL / SQLite)]
        Checkpointer[(AsyncSqliteSaver LangGraph Memory)]
    end

    UI <--> API
    API <--> Auth
    API <--> Cache
    API <--> Multi-Agent Graph Layer
    Multi-Agent Graph Layer <--> Persistence Layer
```

## Key Architectural Principles

1. **Deterministic Engine First**: Calculations for GFA ($m^2$), concrete volume ($m^3$), steel tonnage, brick counts, and cost breakdowns are executed via standard, testable Python code (TCVN compliant) rather than LLM inference.
2. **Parallel Agent Execution (Map-Reduce)**: Specialist agents (`MaterialAgent`, `LaborAgent`, `SeasonalityAgent`, `ZoningLegalAgent`) are dispatched in parallel using LangGraph `Send` API to achieve low latency (~3s response).
3. **Human-In-The-Loop (HITL)**: Execution is paused before supervisor dispatch to allow the user to review, edit, and approve extracted project parameters (`ProjectBrief`).
4. **Append-Only LangGraph State**: `AgentState.messages` maintains standard append-only conversation history while thread persistence is bound to `thread_id=session_id`.
