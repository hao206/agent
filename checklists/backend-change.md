# Backend Change Checklist

- Read `.agents/skills/backend/SKILL.md`.
- Confirm affected state fields are defined in `foundation/schemas/project_brief.py`.
- Preserve `thread_id=session_id`.
- Preserve SSE event types or update frontend client in the same change.
- Prefer deterministic services before new LLM calls.
- Run `python -m compileall src tests`.
