# Daily Tracker – Infrastructure Cost Estimate (No Labor)

Scope: Recurring monthly costs and minimal one-time fees to run the system described in DAILY_TRACKER_ARCHITECTURE_COMBINED.md. Includes API, GraphQL subscriptions, async workers, scheduling, managed Postgres with PITR, Redis, object storage for backups/exports, email, monitoring, and domain/TLS. Labor is explicitly excluded.

Assumptions
- Currency: USD (USD → INR reference rate: 1 USD ≈ ₹83 for internal conversions if needed)
- Scale targets:
  - Small (up to ~200 DAU, ~1k MAU)
  - Growing (1k–5k DAU, ~10k–50k MAU)
- Environments: Dev (shared), Staging (small), Production (sized per tier)
- Data: Postgres 50 GB (small) to 100–200 GB (growing) including WAL retention; backups stored on S3-compatible storage with 30-day retention; GDPR exports small volume
- Email: Daily reminders + notifications → Small: 10k emails/month; Growing: 40k–100k emails/month
- Frontend hosting can be free on Netlify/Vercel (hobby) or bundled with API on a host

Key hosting options
- Managed PaaS (Render/Railway/Heroku-like): simplest ops, predictable pricing
- Managed cloud (AWS/GCP/Azure): more granular control, potentially higher ops effort
- VPS/self-host: lowest raw cost, highest ops burden (you must run Postgres PITR, monitoring, TLS, etc.)

Recommended baseline (for simplicity and reliability): PaaS + managed DB/Redis + S3-compatible storage

Monthly cost scenarios (estimate ranges)
Note: Choose one scenario for production. Dev/Staging are additive.

1) Dev environment (shared by both engineers)
- API + Worker + Scheduler (single small service/container): $10–$20
- Postgres (starter managed DB with PITR if available, otherwise small shared DB): $7–$25
- Redis (starter managed): $0–$15 (some providers include free tier)
- Object storage (backups minimal + GDPR exports): $1–$3
- Email (dev SMTP/sandbox): $0
- Monitoring (basic): $0–$5 (free tiers)
- Domain/TLS: $0 (covered under prod)
Total (Dev): $18–$68/month

2) Staging environment (small, prod-parity features)
- API + Worker + Scheduler (small instances): $15–$30
- Postgres managed with PITR (small): $15–$40
- Redis (starter managed): $5–$15
- Object storage: $2–$5
- Email (low volume, real provider): $0–$10
- Monitoring/logging: $0–$10
Total (Staging): $37–$110/month

3) Production – Small (≤200 DAU)
- Postgres (managed with PITR): $35–$60 (1–2 vCPU, 2–4 GB RAM, 50 GB storage incl. WAL retention)
- Redis (managed, 100–250 MB): $15–$30
- API (1 small instance) with WebSockets: $10–$20
- Worker (1 small instance): $10–$20
- Scheduler (tiny instance or cron/scheduler runner): $5–$10
- Frontend hosting: $0–$20 (free tier or upgraded plan)
- Object storage backups + WAL + GDPR exports (S3/B2/MinIO): $3–$10
- Email provider (10k/month): $15–$25
- Monitoring/logging (Sentry/Grafana Cloud basic): $0–$15
- Reverse proxy/load balancer or PaaS router (sticky sessions for WS): included or $0–$10
- Domain (amortized): $1/month (≈$12/year)
Total (Prod Small): $104–$220/month

4) Production – Growing (1k–5k DAU)
- Postgres (managed with PITR): $80–$120 (2–4 vCPU, 4–8 GB RAM, 100–200 GB storage + WAL retention)
- Redis (managed, 512 MB–1 GB): $30–$60
- API (2 small instances or 1 medium) with WS: $30–$60
- Worker (1 medium): $20–$40
- Scheduler: $5–$10
- Frontend hosting (paid tier/CDN): $0–$25
- Object storage backups + WAL + GDPR exports: $8–$20
- Email provider (40k–100k/month): $40–$120
- Monitoring/logging (paid tiers): $25–$50
- Reverse proxy/LB (sticky sessions): $10–$20 (if needed separately)
- Domain (amortized): $1/month
Total (Prod Growing): $249–$526/month

Optional cost-saving alternatives (with tradeoffs)
- VPS self-host (all-in-one)
  - 1× VPS 4 GB RAM (api+worker+scheduler+redis+proxy) + self-hosted Postgres on same box is not recommended for prod due to data safety; better: 2× VPS (app + dedicated DB)
  - VPS 4–8 GB: $12–$40 each; 2 nodes → $24–$80 total
  - S3-compatible storage (Backblaze B2) for backups/WAL: $2–$10
  - Email (SendGrid/SMTP): $15–$25
  - Monitoring (self-hosted Prometheus/Grafana, Sentry): $0 (infra included) but ops heavy
  - Total (2 VPS + services): ~$41–$115/month, but you must run PITR yourself and accept higher ops risk

Itemized bill of materials (what you need)
- Compute
  - API service (with WebSocket support)
  - Worker service (Dramatiq/Arq)
  - Scheduler service (APScheduler) or platform cron
  - Frontend hosting (Vercel/Netlify or served by API)
- Data services
  - Managed Postgres with PITR (WAL archiving)
  - Managed Redis (cache, rate limiting, queue broker if using Redis)
  - Object storage (S3-compatible) for backups and data exports
  - Email provider (SendGrid/SMTP)
- Networking
  - Domain registration (~$12/year)
  - TLS certificates (Let’s Encrypt free) if self-hosting proxy
  - Reverse proxy/load balancer with sticky sessions for WebSockets (if not covered by PaaS)
- Observability
  - Monitoring/metrics: Prometheus + Grafana (or Grafana Cloud free/paid)
  - Error tracking: Sentry (free to paid)
  - Tracing: OpenTelemetry collector + backend (Tempo/Jaeger/Grafana Cloud)
- Optional
  - CDN for frontend/static files (often bundled with host)
  - pgbouncer (connection pooling) if not provided by DB vendor

One-time and variable costs
- Domain registration: $10–$15/year
- Data transfer/egress: Usually small; budget $5–$20/month for growing tier if users download exports frequently
- Email warm-up: Some providers require ramp-up; initial rate-limit tiers may be free

Concrete provider examples (typical 2025 pricing, approximate)
- Render
  - Web services (starter): ~$7–$15 each
  - Managed PostgreSQL: starter ~$7, standard with PITR ~$20–$40+
  - Redis: ~$7–$15+
  - Cron jobs: ~$5–$7
- Railway
  - Usage-based credits; small services often ~$5–$20 each/month depending on hours/CPU/RAM
  - PostgreSQL/Redis with usage-based tiers; plan for ~$15–$40 each for prod
- Backblaze B2 (object storage)
  - ~$0.006–$0.02/GB-month (tiered); 50 GB → ~$0.30–$1; add $2–$5 buffer for puts/gets and WAL churn
- SendGrid/Mailgun
  - Free/sandbox tiers; 10k/month paid tiers ~ $15–$25; higher tiers scale accordingly

Suggested baseline (pragmatic)
- Dev + Staging combined: ~$60–$150/month
- Production small: ~$120–$180/month
- Production growing: ~$300–$450/month
- Annual domain: ~$12/year

Notes and guidance
- Start on PaaS small tier. Upgrade Postgres/Redis first when you see CPU/memory pressure or slow queries.
- Use S3-compatible storage with lifecycle policies: keep 30 daily backups + 12 monthly; expire WAL older than retention.
- If you adopt WebSockets, confirm provider supports sticky sessions or use a dedicated proxy.
- Use providers’ free tiers for Sentry/Grafana Cloud until you exceed limits; budget upgrades in growing tier.
- If cost is critical, VPS self-hosting can reduce raw spend but increases operational risk; ensure you automate PITR (pgBackRest/WAL-G), monitoring, and security hardening.

Quick monthly totals snapshot
- Dev: $18–$68
- Staging: $37–$110
- Prod (Small): $104–$220
- Prod (Growing): $249–$526

These figures are planning estimates; actuals depend on region, provider, and observed usage. Revisit monthly after launch and right-size services.
