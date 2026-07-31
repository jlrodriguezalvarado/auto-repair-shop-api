# Feature delivery workflow (auto-repair-shop-api)

## 1. Plan with the user

Identify outcome, non-goals, API impact, Angular consumer impact, contracts, auth/ownership, persistence/Celery, tests, and risks. Wait for explicit approval before implementation.

## 2. Record the approved plan

Create `.plans/YYYY-MM-DD-<slug>.md` (America/Caracas) from `.plans/TEMPLATE.md`.

- API-only: `Repositories: auto-repair-shop-api`
- Cross (API + front): `Repositories: both` / `Scope: cross` — still stored here (contract owner). Frontend work is delegated via sibling `../auto-repair-shop-front` or by opening the parent `mechanics/` workspace.

## 3. Implement by ownership

- Use the `django-api` subagent (`.cursor/agents/django-api.md`) for API writes.
- Read `.agents/policies/django-api.md` and `.agents/policies/integration.md`.
- If the plan is cross and this workspace is API-only: implement the API contract first, validate OpenAPI, then either hand off to `auto-repair-shop-front` (open that folder or the parent workspace) or stop with an explicit frontend follow-up in the plan.
- Do not invent contracts that contradict the approved plan.

## 4. QA gate

After API work (and after frontend is integrated when cross), run `qa`. Do not declare complete without PASS (or an explicit user waiver in the plan).

## 5. Record the final result

Append results, commands, migrations, commits, and QA verdict to the same plan file.

## 6. Harden the harness when failures repeat

If a preventable agent mistake class appeared (or parent `mechanics/` issued a harness directive), follow `.agents/policies/continuous-improvement.md`: land a rule, policy, test, or workflow constraint in this repo (and require the sibling when cross-layer). Record under `### Harness improvements` in the plan before calling the work done.
