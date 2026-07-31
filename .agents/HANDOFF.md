# Standard subagent handoff (auto-repair-shop-api)

Include this block (filled in) when delegating to `django-api` or `qa`.

```text
Plan: .plans/YYYY-MM-DD-<slug>.md
Role: django-api | qa
Sibling: this repo (Django API) <-> ../auto-repair-shop-front (Angular)
Scope:
- <allowed work>
Non-goals:
- <exclusions>
Contracts:
- <request/response/error/auth/pagination/decimal, or "unchanged">
- OpenAPI / generated types: <unchanged | validate schema | frontend must regenerate>
Patterns to mirror:
- <paths>
Acceptance criteria to satisfy:
- <subset>
Commands expected before return:
- <from policies/django-api.md or qa.md>
Return format:
- files changed | contract decisions | commands + outcomes | failures | follow-ups for auto-repair-shop-front | harness improvement needed? (failure class + suggested landing or none)
```

## Parallelism

- Finish compatible API + validated OpenAPI before Angular consumes changes.
- For cross features opened from parent `mechanics/`, follow the root `AGENTS.md` orchestration (API then front, then QA).
- When parent issues a harness directive, land API-side defenses per `.agents/policies/continuous-improvement.md`.
