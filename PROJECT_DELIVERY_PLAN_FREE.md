# Daily Tracker – Free-Tier MVP Delivery Plan (Zero Cloud Spend)

Goal
- Deliver a functional MVP using only free-tier services or self-hosted on a personal machine, incurring $0/month infra cost during development and closed beta.
- Defer cost-incurring features (PITR, email-at-scale, sticky WebSockets, paid monitoring, custom domain) to a later paid phase.

Scope Guardrails (What’s In vs Deferred)

Included (no infra spend)
- Core domain: Users, Roles, Groups, GroupMembers, SectionEntries with same-day+2-edits rule, non-decreasing streaks
- Auth: argon2id password hashing, JWT access + refresh (short-lived), httpOnly cookies, CSRF protection
- RBAC: App-level + optional Postgres RLS (works fine on free Postgres; keep policies simple)
- UI: React + Vite + Tailwind + shadcn/ui, Apollo Client with GraphQL Code Generator
- GraphQL API: FastAPI + Strawberry, DataLoader, error handling
- Notifications: In-app notifications only (no emails)
- Scheduling: Avoid always-on schedulers; compute “reminders” and progress on-demand (e.g., on dashboard load) to bypass sleeping containers
- Backups: Manual or nightly pg_dump via GitHub Actions (free) to free object storage (Cloudflare R2/B2 free tier)
- Observability: Sentry free, basic logs; minimal Prometheus/Grafana optional on local only
- CI/CD: GitHub Actions free (public repo recommended for unlimited minutes)

Deferred to Paid Phase (because free tiers limit or break UX/SLAs)
- True Point-In-Time Recovery (PITR) (requires paid managed Postgres or self-operated WAL archiving with operational overhead)
- Email notifications at scale (free tiers too limited; deliver in-app first)
- WebSocket subscriptions in production (free PaaS sleeping breaks long-lived connections; start with polling/“Refresh” UX or short SSE on interaction)
- Sticky sessions/load balancer and multi-instance scaling
- Custom domain + DNS (costs ~ $12/year); use provider subdomain during free phase
- Advanced monitoring/log retention (paid Sentry/Grafana Cloud)
- Redis-backed rate limiting/queues (start without Redis; single-instance MVP can use in-memory rate limit and in-process background tasks)

Zero-Cost Architecture Choices

Frontend (Free)
- Vercel or Netlify free plan (static React build with TLS and a *.vercel.app / *.netlify.app subdomain)

Backend/API (Free)
- Render free web service OR Fly.io free app; use a single API process that also runs:
  - APScheduler in-process (but do not rely on it for time-based runs due to sleeping). Use “on-demand reminders” computed per request/page-load.
  - Lightweight background tasks in-process (asyncio), avoiding a separate worker

Database (Free)
- Neon or Supabase free Postgres (accept quotas, no SLA/PITR). Keep data volume modest.

Object Storage for Backups/Exports (Free)
- Cloudflare R2 or Backblaze B2 free tier; nightly pg_dump via GitHub Actions (free minutes for public repos). Keep dumps small; apply lifecycle rules.

Email (Deferred)
- No outbound email in MVP. Show reminders in-app. Add email later with SendGrid/Mailgun paid tiers.

Redis/Queues (Deferred)
- No Redis initially. If needed for dev only, use Upstash free (but not required for MVP).

Observability (Free)
- Sentry free plan (client + server). Basic logs in platform dashboard.
- Optional: Grafana Cloud free for metrics if desired.

Security and Compliance (Within Free Constraints)
- Implement Data Export/Delete features; store exports in temporary free object storage with short expiry.
- DPA/contractual GDPR posture with third parties typically requires paid tiers; for closed beta keep data minimal and documented.

Feature Adjustments to Fit Free Tier
- Notifications: Replace scheduled emails with an in-app notification center and dashboard-level “you have incomplete sections today” messages computed on load.
- Subscriptions: Replace GraphQL subscriptions with:
  - Polling at modest intervals (e.g., 30–60s) while the page is active, or
  - Manual “Refresh” buttons and optimistic UI after mutations
- Backups: Nightly pg_dump via CI; store to R2/B2 free bucket; verify small restore manually monthly.
- Rate limiting: Per-process in-memory counters (Starlette middleware) suitable for single-instance MVP.

Week-by-Week Plan (Free MVP, ~10 Weeks)

Capacity assumption: 2 engineers × 2–3 h/day × 5 days = 20–30 h/week (25 h/week typical)

Week 1: Bootstrap (FE/BE/CI)
- FE: Vite + React + Tailwind + shadcn/ui; routing and layout shell
- BE: FastAPI + Strawberry skeleton; health check; Docker dev
- CI: GitHub Actions free pipelines; pre-commit linters

Week 2: DB & Models
- SQLAlchemy models + Alembic migrations (Users, Roles, Groups, GroupMembers, SectionEntries, Notifications)
- Soft deletes, partial unique indexes; seed script

Week 3: Auth & RBAC
- Argon2id hashing, JWT access/refresh with cookies + CSRF
- Role-based middleware; optional RLS policies (basic)

Week 4: GraphQL Core
- Schema for User/Group/GroupMember; DataLoader; error envelope
- Apollo Client + GraphQL Codegen in FE; auth context wired

Week 5: Entries & Business Rules
- SectionEntries mutations: server-controlled entryDate; 2-edits/day rule
- Streak logic (non-decreasing); audit logging

Week 6: In-App Notifications & “On-Demand Reminders”
- In-app notification list and “unread” badges
- Dashboard computes daily incomplete sections and shows callouts (no email or cron)

Week 7: Groups & Roles UI
- Group CRUD, timezone selector; membership management
- Promote/demote UI (no email confirmations)

Week 8: Calendar & Progress Views
- Calendar heatmap; group timezone banner; progress bar
- Client polling or manual refresh for updates (no subscriptions)

Week 9: Backups & GDPR (Free)
- Nightly pg_dump via GitHub Actions to R2/B2 free
- Export My Data (ZIP to R2/B2 with short-lived URL); Delete My Account (soft delete, purge job is manual/monthly in free phase)

Week 10: Testing & Beta Release
- Backend unit/integration; FE component/E2E smoke; basic accessibility checks
- Sentry free telemetry; release to Vercel/Netlify + Render/Fly free

Free-Tier Infra Estimate
- Frontend: $0 (Vercel/Netlify free)
- Backend/API: $0 (Render/Fly free; accepts sleeping/cold starts)
- Postgres: $0 (Neon/Supabase free)
- Object storage: $0 (R2/B2 free tier; apply lifecycle)
- Email: $0 (not used)
- Observability: $0 (Sentry free)
- CI/CD: $0 (GitHub Actions free, public repo)
- Domain: $0 (use provider subdomain)
Total Monthly Infra: $0

Upgrade Path (Add Paid Features Later)
- Email notifications: Add SendGrid/Mailgun starter; enable APScheduler jobs (or provider cron) for nightly reminders; rewire dashboard to reflect outbound status
- WebSocket subscriptions: Move to a paid PaaS tier that doesn’t sleep and supports sticky sessions; adopt Redis Pub/Sub
- PITR backups: Switch to paid managed Postgres with WAL archiving (pgBackRest/WAL-G)
- Redis & rate limiting: Add managed Redis; replace in-memory limits with Redis-based
- Custom domain and TLS: Purchase domain (~$12/year); configure DNS/HTTPS
- Monitoring/logging: Upgrade Sentry/Grafana Cloud for retention and alerting

Deliverables and Definition of Done (Free MVP)
- Functional: Auth, RBAC, entries with rules, streaks, groups, in-app notifications, dashboard reminders-on-load, calendar
- Reliability: Nightly pg_dump to free object storage; manual monthly restore test
- Security: Argon2id, CSRF-protected cookies, JWT rotation; minimal PII; secrets via env vars
- Observability: Sentry free; platform logs
- Docs: Setup guide for free stack; backup/restore runbook; upgrade path doc

Bill of Materials (All Free)
- FE: Vercel/Netlify
- API: Render/Fly free
- DB: Neon/Supabase free
- Storage: Cloudflare R2 or Backblaze B2 free tier
- CI/CD: GitHub Actions free
- Telemetry: Sentry free
- Optional local-only: Mailpit (dev email), Prometheus/Grafana via Docker compose (not public)

Notes and Risks
- Sleeping services cause cold starts; avoid background schedules—compute on demand
- No SLA; free tiers may throttle or change limits
- No true PITR—accept risk; keep data volume small; run manual restore drills monthly
- GDPR with third parties may require paid DPAs for full compliance; for small closed beta, reduce PII and communicate limitations

Appendix: Minimal Env Matrix (Free)
- Dev: local Docker (api, db), FE served by Vite dev server
- Staging: FE (Vercel/Netlify), API (Render/Fly), DB (Neon/Supabase), R2/B2
- Pilot: same as staging; avoid WebSockets and outbound email; rely on in-app notifications and polling
