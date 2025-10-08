# Daily Tracker – Architecture Modifications (2025-10-08)

This document records the agreed changes to the original architecture to improve security, reliability, and operability, and to align with multi-timezone scheduling and real-time UX needs.

## 0) Summary of Decisions

- Replace Celery + Celery Beat with:
  - Task runner: Dramatiq or Arq (final selection below)
  - Scheduler: APScheduler (DB-backed)
- Add Postgres Row-Level Security (RLS) policies for defense-in-depth RBAC
- Replace pg_dump-only backups with true PITR via WAL archiving (pgBackRest or WAL-G)
- Strengthen auth: argon2id password hashing, short-lived access tokens + rotated refresh tokens, CSRF protection (cookies), 2FA backup codes, optional WebAuthn for admins
- Add GraphQL WebSocket subscriptions (Strawberry) with Redis pub/sub
- Frontend DX: GraphQL Code Generator + React Hook Form + Zod
- Data model refinements: server-controlled entryDate, optional SectionTypes table, partial unique indexes via Alembic
- Observability: OpenTelemetry tracing, structured logging, Postgres exporter, Sentry
- Deployment: sticky sessions for websockets, pgbouncer, managed Postgres recommended
- Optional acceleration: Hasura/PostGraphile for RLS-native GraphQL

---

## 1) Asynchronous Jobs and Scheduling

### 1.1 Switch from Celery to Dramatiq/Arq
- Options:
  - Dramatiq + Redis
    - Pros: Mature, simple decorators, retries/middleware, good ecosystem.
    - Best when you want classic task queues with straightforward ergonomics.
  - Arq (asyncio-native) + Redis
    - Pros: Excellent fit with FastAPI’s async stack, minimal overhead.
    - Best when you prefer pure-async flows and a lightweight solution.

- Reason to switch:
  - Modern tooling with simpler integration into an async FastAPI codebase.
  - Lower operational burden compared to Celery (fewer moving parts).
  - Cleaner developer ergonomics.

- Migration checklist:
  - Replace Celery tasks with Dramatiq/Arq tasks.
  - Replace Celery Beat schedules with APScheduler jobs.
  - Keep Redis as the broker; configure connection pools and timeouts.
  - Containerize a separate worker process (and scheduler) in Docker Compose.

### 1.2 Scheduling: APScheduler (DB-backed)
- Replace “scan-all-groups-then-check-local-time” pattern with per-group scheduling.
- Use RedisJobStore or SQLAlchemyJobStore to persist schedules.
- For daily reminders at 20:00 group-local:
  - Compute “next run” in UTC per group’s timezone and schedule that specific run.
  - On timezone or reminder time change, reschedule the job.
- Reason:
  - Scales with number of groups (O(1) per job).
  - Eliminates time-drift and repeated scans.

---

## 2) Database Security and Modeling

### 2.1 Postgres Row-Level Security (RLS)
- Enable RLS on tables holding user/group/entries.
- Define policies for scopes: own, group, all, based on the user’s role and group membership.
- Application still enforces permissions, but RLS provides defense-in-depth and prevents privilege escalation via logic bugs.

### 2.2 Soft Deletes and Partial Unique Indexes
- Implement unique constraints via partial indexes:
```sql
CREATE UNIQUE INDEX uniq_active_members
  ON group_members (group_id, user_id)
  WHERE deleted_at IS NULL;
```
- Ensure ORM queries exclude soft-deleted rows using SQLAlchemy with_loader_criteria.

### 2.3 Section Type and Extensibility
- If sections will evolve, replace ENUM with a SectionTypes table (FK).
- If stable, keep ENUM and enforce mapping consistency across DB/GraphQL/frontend.

### 2.4 Entry Date Semantics (Timezone correctness)
- Server sets “entryDate” as “today” in the group’s timezone for standard users.
- Backfill (manual entryDate) restricted to admins.
- Store timestamps in UTC; derive local-day on read using group timezone to avoid DST edge-cases.
- Keep created_at/updated_at for auditing; add last_edit_at.

---

## 3) Backups and Recovery (PITR)

### 3.1 Switch to WAL Archiving (pgBackRest or WAL-G)
- Replace daily pg_dump-only with:
  - Periodic full backups + continuous WAL archiving to S3-compatible storage.
- Reason:
  - True Point-In-Time Recovery (PITR) to any moment before an incident.
- Policies:
  - Retention: last 30 daily, last 12 monthly (configurable).
  - Encryption at rest (AES-256) and in transit.
  - Weekly automated restore test to staging.

---

## 4) Authentication, Authorization, and Security

### 4.1 Password Hashing
- Switch bcrypt → argon2id (passlib argon2).
- Reason: Memory-hard KDF; stronger against GPU attacks.

### 4.2 Token Model
- Short-lived access token + rotated refresh token (reuse detection).
- Store tokens in httpOnly cookies; apply SameSite/secure flags.
- Add CSRF protection (double-submit cookie or header with SameSite=strict).

### 4.3 2FA Enhancements
- Keep TOTP for Super Admin; add backup codes.
- Optional: Extend 2FA to Group Admins.
- Consider WebAuthn as a step-up factor for admin actions.

### 4.4 Rate Limiting and Abuse Prevention
- Keep slowapi/starlette-limiter with Redis.
- Add per-operation GraphQL limits and consider simple cost analysis.
- Lockouts for failed logins; audit logs for security-sensitive actions.

---

## 5) GraphQL Layer and Real-time

### 5.1 Subscriptions
- Add WebSocket subscriptions via Strawberry ASGI.
- Use Redis pub/sub for cross-instance fan-out.
- Use sticky sessions at the edge or a dedicated subscriptions service.

### 5.2 N+1 and Performance
- Keep DataLoader batching for relations (User/Group).
- Cache inexpensive reads with Redis; set TTLs.

### 5.3 Optional Acceleration
- Consider Hasura or PostGraphile for RLS-native GraphQL (instant CRUD/subscriptions).
- Keep FastAPI for custom actions, auth, and REST endpoints that don’t fit pure CRUD.

---

## 6) Frontend Developer Experience

### 6.1 Typed GraphQL
- Add GraphQL Code Generator to produce TypeScript types and hooks for Apollo Client.
- Eliminate runtime field mismatch errors; improve refactors.

### 6.2 Forms and Validation
- Use React Hook Form + Zod:
  - Consistent client-side validation mirroring server constraints.
  - Better performance than ad-hoc controlled components.

### 6.3 UI/UX
- Keep React + Vite + Tailwind + shadcn/ui.
- Ensure accessibility (WCAG 2.1 AA) and consistent toast/loading/error patterns.

---

## 7) Observability and Operations

### 7.1 Tracing and Metrics
- OpenTelemetry for FastAPI + Strawberry (ASGI), export to Grafana Tempo/Jaeger.
- Prometheus + Grafana remain; add Postgres Exporter and app-level custom metrics.

### 7.2 Logging and Errors
- Structured JSON logs with correlation/request IDs.
- Sentry for server and client error reporting.

### 7.3 Database and Pooling
- Add pgbouncer for connection pooling.
- Monitor slow queries and index health; periodic vacuum/analyze checks.

---

## 8) Deployment and Infrastructure

### 8.1 WebSockets
- Ensure ws support and sticky sessions if behind a load balancer (Render/Railway/nginx/traefik).
- Alternatively, run a dedicated subscriptions service with Redis.

### 8.2 Data Services
- Prefer managed Postgres with built-in PITR (Neon/Supabase/Crunchy/RDS) if possible.
- S3-compatible storage with encryption and lifecycle policies (backups, exports).

### 8.3 Containers
- Separate containers: api, worker (Dramatiq/Arq), scheduler (APScheduler), redis, postgres, frontend.
- Set resource requests/limits and health checks.

---

## 9) Testing and Quality

- Backend: pytest unit + integration + permission tests.
- GraphQL resolvers: integration tests validating RLS + app-layer checks.
- Frontend: Jest + React Testing Library; E2E (Playwright/Cypress).
- Load tests: Locust targeting 95th/99th percentiles and concurrency goals.
- Targets: Backend 80%+, Frontend 70%+, Critical paths 100%.

---

## 10) Risk/Trade-offs

- RLS increases DB-side complexity; mitigated by strict migrations and policy tests.
- Introducing subscriptions adds infra complexity (ws, sticky, Redis).
- Switching KDF/token flows impacts auth; require careful migration and user comms.
- APScheduler requires persistent job store and migration plan for existing reminders.

---

## 11) Decision: Dramatiq vs Arq

- Choose one:
  - Dramatiq if you prefer a mature, batteries-included task queue with built-in retries and rich middleware.
  - Arq if you prioritize minimalism and pure-async ergonomics tightly aligned with FastAPI.

- Both will:
  - Use Redis as broker.
  - Run as a separate worker container.
  - Integrate with APScheduler for time-based triggers.
  - Support idempotency keys and retry/backoff strategies.

(If undecided now, keep both paths documented; implement one during Phase 1.)

---

## 12) Migration Plan (High-level)

1. PITR:
   - Stand up S3 bucket, configure pgBackRest or WAL-G, enable WAL archiving.
   - Run initial full backup and test restore in staging.

2. Auth hardening:
   - Switch to argon2id for new passwords; rehash on next login for existing users.
   - Introduce refresh tokens with rotation + reuse detection.
   - Add CSRF protection for cookie-based auth; add backup codes for 2FA.

3. RLS:
   - Write Alembic migrations: enable RLS and add policies.
   - Update resolvers/queries to pass role/user context; validate with tests.

4. Async:
   - Implement Dramatiq/Arq workers; port tasks from Celery.
   - Introduce APScheduler with persistent job store; create per-group schedules.
   - Retire Celery Beat and Celery workers.

5. GraphQL real-time:
   - Add ws endpoint; wire Redis pub/sub; migrate client to subscriptions for notifications and live lists.

6. Frontend DX:
   - Add GraphQL Code Generator; adopt RHF + Zod; align enums and error handling.

7. Observability:
   - Add OTel instrumentation; configure exporters.
   - Add Postgres exporter; standardize JSON logging; propagate request IDs.

---

## 13) Acceptance Criteria

- PITR validated via restore-to-point-in-time in staging.
- RLS policy tests pass; unauthorized access blocked at DB layer.
- Daily reminders fire at correct local times without scanning every group.
- Passwords hashed with argon2id; token rotation and CSRF confirmed.
- Subscriptions deliver live notifications reliably across multiple instances.
- E2E flows (auth, entries, moderation) pass under load and across timezones.
