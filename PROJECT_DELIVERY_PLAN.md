# Daily Tracker – Project Delivery Plan

Source: DAILY_TRACKER_ARCHITECTURE_COMBINED.md (Original + Modifications)

This plan translates the architecture into an actionable schedule, estimates, tools list, and completion criteria tailored for a two-person team working 2–3 hours/day each weekday.

## 0) Assumptions and Capacity

- Team size: 2 engineers
- Availability: 2–3 hours/day each, 5 days/week → 20–30 hours/week total
- Planning basis: 25 hours/week midpoint
- Working model: Parallel work per week with clear ownership and handoffs
- Environments: Local dev (Docker), staging, production

## 1) Duration and Effort Estimates

- Estimated effort: ≈ 516 hours (baseline)
- Contingency: +10–15% for integration, ops, and polishing
  - 10%: 568 hours (rounded)
  - 15%: 593 hours (rounded)

- Duration by available weekly hours:
  - 20 h/week: 26–30 weeks (with contingency)
  - 25 h/week: 21–24 weeks (with contingency)
  - 30 h/week: 17–20 weeks (with contingency)

## 2) Weekly Task Breakdown (two-person team)

Each week lists primary owners; if tasks finish early, pull next ready item for that week.

Week 1: Project bootstrap and CI/CD
- Dev A: Repo structure, pre-commit, Python (ruff/black/isort), TypeScript (eslint/prettier), GitHub Actions CI
- Dev B: Docker Compose baseline (api, frontend, postgres, redis), .env templates, Makefile/dev scripts
Deliverables: Empty FastAPI + React shells start locally; CI green

Week 2: Database schema, Alembic, soft deletes
- Dev A: SQLAlchemy models + Alembic migrations for Users, Roles, Groups, GroupMembers, SectionEntries, Notifications, AuditLogs, BackupLogs
- Dev B: Partial unique indexes (WHERE deleted_at IS NULL), with_loader_criteria for soft deletes, seed data script
Deliverables: Schema migrated, indexes valid, seeds available

Week 3: Postgres Row-Level Security (RLS)
- Dev A: Enable RLS, define own/group/all policies across core tables
- Dev B: Integration tests validating RLS blocks unauthorized access; DB roles for app/staff
Deliverables: RLS in migrations with tests

Week 4: Authentication foundation
- Dev A: Argon2id hashing, register/login, short-lived access tokens, refresh token rotation + reuse detection
- Dev B: httpOnly cookies, SameSite/secure flags, CSRF (double-submit or header), logout + token revocation
Deliverables: Secure auth flow end-to-end

Week 5: 2FA + roles wiring
- Dev A: TOTP (PyOTP), QR issuance, verify; backup codes handling
- Dev B: Role endpoints, middleware stubs; promote/demote skeleton APIs
Deliverables: 2FA for super admins, backup codes, role APIs baseline

Week 6: GraphQL base and resolvers
- Dev A: Strawberry schema for User/Group/GroupMember + DataLoader batching
- Dev B: Auth context on resolvers, permission decorators aligned with RLS, uniform error format
Deliverables: /graphql endpoint with basic queries, N+1 avoided

Week 7: Entries domain & business rules
- Dev A: SectionEntries CRUD/mutations; server-controlled entryDate; edit limit enforcement
- Dev B: Streak logic; milestone notifications; audit logs for mutations
Deliverables: Entries feature with non-resetting streaks

Week 8: Scheduling and notifications (timezone aware)
- Dev A: APScheduler (SQLAlchemyJobStore) with per-group 20:00 local jobs; reschedule on tz changes
- Dev B: Email sending (SendGrid/SMTP), Notifications API (mark-read/all), rate limiting guards
Deliverables: Daily reminder jobs per group; notifications pipeline working

Week 9: Async tasks (Dramatiq or Arq) and worker infra
- Dev A: Port scheduled jobs and email dispatch to Dramatiq/Arq tasks with retries/backoff; idempotency keys
- Dev B: Containerize worker and scheduler; liveness/readiness health checks
Deliverables: Stable queue processing and ops runbooks

Week 10: Backups and PITR
- Dev A: pgBackRest or WAL-G (full + WAL to S3-compatible); retention and encryption
- Dev B: Staging restore-to-point-in-time validation; backup logs + admin endpoint
Deliverables: Proven PITR with documented restore steps

Week 11: Frontend shell and auth flows
- Dev A: Base layout (Tailwind + shadcn/ui); login/register/2FA screens; refresh handling; CSRF wiring
- Dev B: Apollo Client, GraphQL Code Generator, error boundaries, toast/loader patterns
Deliverables: Authenticated FE with typed GraphQL hooks

Week 12: Entries UI and daily progress
- Dev A: Section cards (Health/Happiness/Hela), edit count warnings, success toasts
- Dev B: Calendar view; timezone banner; “today” semantics mirrored with server
Deliverables: Day-to-day entry UX complete

Week 13: Groups and role management UI
- Dev A: Group CRUD and timezone settings
- Dev B: Membership management; promote/demote UI; confirmations; audit log views
Deliverables: Admin tools for groups and roles

Week 14: Moderation and notification center
- Dev A: Flag/unflag interface, moderation queue
- Dev B: Notification center with unread badge; filters; mark-all-read
Deliverables: Admin moderation and polished notifications

Week 15: Real-time updates (subscriptions) and proxy
- Dev A: Strawberry WebSocket subscriptions + Redis pub/sub (notifications, live lists)
- Dev B: Reverse proxy (nginx/traefik) sticky sessions; FE subscription adoption
Deliverables: Live updates across instances

Week 16: Analytics backend
- Dev A: Group analytics queries (completion rates, active users, section popularity) with caching
- Dev B: Global analytics for super admin; pagination and RBAC checks
Deliverables: Efficient analytics resolvers

Week 17: Analytics frontend
- Dev A: Charts (line/bar/pie) for group dashboards
- Dev B: Super admin dashboards (multi-group comparison, system stats)
Deliverables: Responsive analytics UI

Week 18: GDPR + backup visibility
- Dev A: Export pipeline (ZIP+temp URL), delete-my-account (soft delete + purge policy)
- Dev B: Backup logs view; guarded trigger backup action
Deliverables: GDPR workflows and backup transparency

Week 19: Observability
- Dev A: OpenTelemetry traces (FastAPI + Strawberry + DB), Sentry server+client, request IDs
- Dev B: Prometheus exporters (app/DB), Grafana dashboards, alerts (latency, error, pool usage, backups, disk)
Deliverables: Monitoring and alerting online

Week 20: Testing and hardening
- Dev A: Backend unit/integration/permission/RLS tests; Locust load test
- Dev B: FE component tests (Jest/RTL), E2E (Playwright/Cypress), accessibility checks (axe-core)
Deliverables: Coverage targets met; load/performance acceptable

Week 21: Deployment and polish
- Dev A: pgbouncer, IaC snippets, domain/TLS (Let’s Encrypt), prod configs + migrations
- Dev B: Runbooks (backup/restore, job ops, scaling), security review, final release checklist
Deliverables: Production-ready release with docs

## 3) Cost Estimate

Assumptions:
- Hours baseline: 516 h; with contingency: 568–593 h
- Currency: USD; INR conversion at 1 USD = ₹83. Figures rounded to nearest whole.

Scenario A ($25/h):
- Baseline: $12,900 ≈ ₹1,070,700
- +10%: $14,190 ≈ ₹1,177,770
- +15%: $14,835 ≈ ₹1,231,305

Scenario B ($40/h):
- Baseline: $20,640 ≈ ₹1,713,120
- +10%: $22,704 ≈ ₹1,884,432
- +15%: $23,736 ≈ ₹1,970,088

Scenario C ($60/h):
- Baseline: $30,960 ≈ ₹2,569,680
- +10%: $34,056 ≈ ₹2,826,648
- +15%: $35,604 ≈ ₹2,955,132

Category breakdown (baseline 516 h; example at $40/h):
- Backend/API/Auth/GraphQL/RLS: 237 h → $9,480 ≈ ₹786,840
- Frontend (React/Apollo/Codegen/UI): 134 h → $5,360 ≈ ₹444,880
- DevOps/Infra/Backups/PITR/Monitoring: 93 h → $3,720 ≈ ₹308,760
- Testing/QA/Docs: 52 h → $2,080 ≈ ₹172,640

## 4) Tools and Machines Required

Development machines
- 2 developer laptops; 8+ cores recommended, 16–32 GB RAM (Docker), 512 GB SSD; macOS/Windows/Linux

Local software
- Docker Desktop, Python 3.11, Node 18 LTS, pnpm or npm, PostgreSQL client (psql), Redis CLI
- VSCode + extensions (Python, Pylance, ESLint, Prettier)
- Git + pre-commit

Backend libraries
- FastAPI, Strawberry GraphQL, SQLAlchemy 2.0, Alembic
- passlib[argon2], PyOTP, APScheduler, Dramatiq or Arq, Redis
- slowapi/starlette-limiter, python-jose or PyJWT
- OpenTelemetry SDK + exporters, Sentry SDK

Frontend libraries
- React 18 + Vite, Tailwind CSS + shadcn/ui
- Apollo Client, GraphQL Code Generator
- React Hook Form + Zod, date-fns/luxon for tz display

Quality and testing
- pytest, coverage
- Jest + React Testing Library
- Playwright or Cypress (E2E)
- Locust (load testing)
- axe-core (accessibility)
- ruff/black/isort (Python), eslint/prettier (TS)

Infrastructure/services
- Managed PostgreSQL with PITR (Neon/Supabase/Crunchy/RDS)
- Managed Redis
- S3-compatible object storage for backups/exports (AES-256; lifecycle policies)
- Email (SendGrid/SMTP)
- Prometheus + Grafana (or Grafana Cloud), Postgres exporter
- Sentry, OpenTelemetry Collector
- Reverse proxy/load balancer (nginx/traefik) with sticky sessions for WebSockets
- pgbouncer for Postgres connection pooling
- CI/CD: GitHub Actions (or equivalent)

## 5) Detailed Completion Notes (Definition of Done)

Functional completeness
- RBAC enforced in app and DB via RLS; policy tests green
- Entries: server-controlled entryDate; same-day edits only; max 2 edits; timezone-correct calendars
- Streaks: non-decreasing; milestone notifications issued
- Per-group 20:00 local reminders scheduled with APScheduler; email delivery verified
- Moderation: flag/unflag flows; admin review queue
- Analytics: group and global dashboards; performant queries with caching
- GDPR: export ZIP (temp URL); delete-my-account soft-deletes with purge retention job

Security
- Argon2id password hashing
- Short-lived access + rotated refresh tokens; CSRF for cookie flows
- 2FA (TOTP) for super admins; backup codes; option for group admins
- Rate limits on endpoints and operations; failed login lockout; audit logs for sensitive actions
- Secrets via env vars/secret manager; no secrets in repo

Reliability and data safety
- PITR via pgBackRest or WAL-G; retention and encryption configured
- Weekly restore-to-point-in-time test to staging documented
- Soft-delete purge after 90 days
- pgbouncer pooling; slow-query logging and index health checks

Observability
- OpenTelemetry traces across HTTP/WS/DB; Sentry for errors
- Prometheus metrics and Grafana dashboards
- Alerts: latency >500ms, error rate >1%, DB pool >80%, backup failure, disk >85%

Testing quality gates
- Backend unit/integration/permission/RLS coverage ≥80%
- Frontend component coverage ≥70%
- Critical paths (auth, entries, role management) ≥100% tested
- E2E flows validated; load testing meets SLOs; accessibility checks (WCAG 2.1 AA) passed on key screens

Operations and documentation
- Runbooks: backup/restore, scaling workers, rescheduling jobs, rotating secrets
- Deployment checklist: migrations, env config, TLS, domain, health checks
- Admin and developer onboarding docs

## 6) Risks and Mitigations

- RLS complexity: Code reviews + policy tests in CI, migration gating
- Timezone scheduling drift: Compute next-run in UTC per group; persistent job store; reschedule on tz change
- WebSocket scaling: Sticky sessions + Redis pub/sub; separate subscriptions service if needed
- Backup/PITR misconfig: Weekly automated restore tests; alerts on backup/WAL failures
- Scope creep (new sections): If likely, shift ENUM to SectionTypes FK early

## 7) Immediate Next Actions

- Choose Dramatiq (richer middleware) or Arq (async simplicity). Recommendation: Arq for pure-async with FastAPI unless advanced middleware needed.
- Select providers: managed Postgres/Redis + S3-compatible storage
- Reserve domain; scaffold CI/CD pipeline
- Kick off Week 1 tasks

## 8) Estimation Footnotes

- Currency rate used: 1 USD = ₹83; adjust if your finance team uses a different spot rate
- Contingency covers integration, infra tuning, and polish; not feature creep
- Adding weekend time or a third contributor reduces duration proportionally
