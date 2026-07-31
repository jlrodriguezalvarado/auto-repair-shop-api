# Continuous improvement (harness) — auto-repair-shop-api

Keep aligned with `../auto-repair-shop-front/.agents/policies/continuous-improvement.md` for the shared loop. Layer landing zones differ below.

Companion policies: `django-api.md`, `integration.md`, `qa.md`.

## Principle

When an agent (or human correcting an agent) hits a **repeatable** failure, fixing application code alone is not enough. Land a durable defense in **this** kit so the next run cannot make the same mistake silently.

## When to trigger

Trigger after any of:

- The same mistake class appears twice in a session or across recent plans.
- QA `FAIL` / `BLOCKED` with a clear preventable cause (missing check, wrong ownership, contract drift, skipped gate).
- The user corrects a pattern the agent should have known from policy/rules.
- Parent workspace (`mechanics/`) issues a harness directive naming this repo.

Do **not** invent process for one-off typos or unique product decisions.

## Loop (this repo owns its landing)

1. **Name the failure class** in one line (e.g. “OpenAPI left unvalidated after serializer change”).
2. **Choose the smallest durable defense** (prefer earlier gates):
   - **Rule** — `.cursor/rules/*.mdc` or a bullet in an existing always-apply rule.
   - **Policy** — `.agents/policies/*.md` (prefer editing an existing policy over a new file).
   - **Workflow / HANDOFF** — only if the lifecycle or delegation shape was wrong.
   - **Test** — regression in the Django suite when behavior can be asserted.
   - **Plan template / checklist** — only if the gap is planning/verification coverage.
3. **Apply the change in this repository** (and sibling only if the failure is cross-layer — see Root).
4. **Record** under the active plan’s `### Harness improvements` (date, failure class, artifact path, why it prevents recurrence).
5. Continue the feature; do not declare complete while a required harness item for this failure is still open.

## Landing zones (API)

| Failure class (examples) | Prefer |
|--------------------------|--------|
| Contract / OpenAPI / auth / Celery / migrations | `policies/django-api.md` or `integration.md` + targeted test |
| Ownership / wrong repo edits | `AGENTS.md`, `HANDOFF.md`, agent preload |
| QA skipped or weak evidence | `policies/qa.md` (keep aligned with auto-repair-shop-front) |
| Repeated command omission | `policies/django-api.md` verification section or HANDOFF “Commands expected” |
| Cursor-session habit | `.cursor/rules/workflow.mdc` or a focused `.mdc` |

## Sibling and parent

- **Sibling-only front failure**: do not change this repo; note follow-up for `auto-repair-shop-front` in the plan.
- **Cross-layer failure**: apply the API-side defense here; require the matching front-side defense in `auto-repair-shop-front` (or accept an explicit “none — API-only root cause” in the plan).
- **Opened from parent `mechanics/`**: follow the root harness directive in `mechanics/AGENTS.md`. Root decides *which* repos act; each repo decides *how* to land per this policy.

## Anti-patterns

- Fixing only the feature code and hoping memory holds.
- Duplicating the same rule in three places; one clear SoT plus a short pointer is enough.
- Weakening tests or deleting checks to “pass”.
- Writing long essays; defenses must be short and actionable.
