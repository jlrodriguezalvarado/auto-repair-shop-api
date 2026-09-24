# Django API repository guidance

This repository (`auto-repair-shop-api`) is the Django/DRF API half of the Mechanics product. Its first-party HTTP/WebSocket consumer is the Angular app in sibling `../auto-repair-shop-front`.

## Jose knowledge base

Cross-project engineering knowledge (global rules, anti-patterns, patterns) lives in `~/projects/jose-knowledge-base` (WSL). On Windows, use the cloned vault path.

Before implementing: read that vault's `AGENTS.md` and `00-System/AI-Instructions.md`, then this file.

- This repository remains the source of truth for code, HTTP contracts, and this product's workflow (`.plans/`, `.cursor/`, `.agents/`).
- The vault does not make this repo read-only.
- Do not copy vault notes into this repo. Link or follow them.
- Global examples: no `window.confirm`/`alert` for business UI; reuse existing helpers; OpenAPI/Swagger only on the local machine, never on deployed development/production.

Cloud / remote agents usually cannot read the vault. Put **task-relevant** vault constraints into the approved `.plans/` file (vault: `00-System/Integrations/Cloud-Agents.md`).

## Sources of truth (this repo)

- `.agents/WORKFLOW.md` — lifecycle
- `.agents/HANDOFF.md` — delegation block
- `.agents/policies/django-api.md` — engineering rules
- `.agents/policies/integration.md` — cross-layer contracts
- `.agents/policies/qa.md` — QA gate
- `.agents/policies/continuous-improvement.md` — turn repeatable agent failures into kit defenses
- `.cursor/agents/django-api.md` / `qa.md`
- Approved plans under `.plans/` (also stores **cross** plans as contract owner)

## Sibling

| Sibling | Role |
|---------|------|
| `../auto-repair-shop-front` | Sole first-party Angular consumer; regenerates types from `docs/openapi.yaml` |

When a change needs UI work: finish a compatible API contract + validated OpenAPI here first, then adapt `auto-repair-shop-front` (open that folder or the parent `mechanics/` workspace for full orchestration).

## Parent workspace

Opening parent `mechanics/` loads root `AGENTS.md` plus root `.cursor/agents/` for full-feature orchestration. Detail still lives in this kit and in `auto-repair-shop-front`’s kit.

## Safeguards

- Prefer explicit, stable HTTP contracts and validated OpenAPI.
- Scope user-owned querysets before lookup; additive migrations unless destruction is approved.
- Never duplicate domain helpers. Search existing Utils/services/shared modules first and reuse or extend them; do not reimplement the same helper in a new call site.
- Do not push, merge, deploy, or run production migrations without explicit authorization.
- Do not skip ownership or QA gates.
- After a repeatable agent failure, follow `.agents/policies/continuous-improvement.md` (or a parent harness directive) before declaring done.
