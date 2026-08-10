# Decision 0001: Package Src Layout

## Decision

Use `src/foundation` as the single Python package for domain schemas, architectural patterns, and prompt templates in the clean foundation layer.

## Consequences

- Foundation modules are imported cleanly via `foundation.schemas`, `foundation.prompts`, etc.
- Dependencies are kept strictly minimal (`pydantic`, `langgraph`, `langchain-core`).
