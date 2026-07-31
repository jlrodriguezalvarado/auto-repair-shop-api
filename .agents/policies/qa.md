# QA gate policy

Keep aligned with `../auto-repair-shop-front/.agents/policies/qa.md`.

Companion policies: `django-api.md`, sibling `angular-frontend.md` (in auto-repair-shop-front), and `integration.md`.

## Review order

1. Read the approved `.plans` file and list every acceptance criterion.
2. Inspect both worktrees and complete diffs. Identify unrelated edits, missing generated artifacts, unplanned contract changes, and undocumented deviations.
3. Review high-risk behavior before running tests: authorization, ownership, validation, error envelopes, Django↔Angular contract fit, transactions, Celery idempotence, query growth, JWT refresh races, RxJS cancellation, user-state cleanup, PWA caches, and migration safety.
4. Run focused reproduction for every suspected defect.
5. Execute the full applicable matrix and compare the evidence with the plan.

## Required API evidence

- `git diff --check` and expected-only status.
- Django system check.
- No unintended migrations; reviewed migration plan when migrations exist.
- OpenAPI validation with zero errors and warnings when HTTP contracts are touched.
- Targeted tests plus the full PostgreSQL suite.
- Production deploy check using safe verification variables when deployment settings change.
- Health, Celery, and WebSocket tests when those paths are affected.

## Required frontend evidence

- `git diff --check` and expected-only status.
- Application and spec TypeScript compilation.
- Generated OpenAPI types current when contracts are touched.
- Targeted specs plus all specs in Chrome Headless.
- Production build within budget, with every warning recorded.
- PWA configuration and authenticated caching reviewed when service-worker or storage behavior changes.
- Dependency audit reported when dependencies change; do not force fixes.
- When UI copy or i18n changes: confirm keys live in `src/app/core/i18n/en.json` and `es.json` with matching key sets; reject embedded EN/ES catalogs in TypeScript.

## Verdict

- `PASS`: all acceptance criteria are evidenced, checks pass, and there are no unresolved blocking findings.
- `FAIL`: a defect, regression, missing requirement, stale artifact, or failed required check exists. Include severity, owner, file reference, and reproduction. If the cause is a preventable agent pattern, recommend a harness improvement (repo continuous-improvement policy or parent directive); do not apply it as QA.
- `BLOCKED`: a required dependency or authorization is unavailable. State exactly what is needed; do not substitute a weaker check silently.

QA is review-only. It must not edit production code, tests, schemas, plans, or configuration to manufacture a passing result.
