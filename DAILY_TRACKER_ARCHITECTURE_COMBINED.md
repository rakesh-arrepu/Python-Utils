# Daily Tracker – Architecture (Original + Modifications)

Generated on: 2025-10-08

This document consolidates:
- Part A: The original architecture document (verbatim)
- Part B: The architecture modifications (verbatim)

---

## Part A: Original Architecture Document (verbatim)

# Daily Tracker - Software Architecture (Updated)

## 1. Checklist

- [ ] Design normalized database schema with role-based access control and soft deletes
- [ ] Define three-tier role hierarchy with promotion/demotion APIs
- [ ] Create GraphQL API with granular permission enforcement
- [ ] Implement non-resetting streak counter (increments only on completion)
- [ ] Add group-level timezone configuration (default GMT+5:30)
- [ ] Design responsive SPA UI with progress indicators and info tooltips
- [ ] Implement 2FA for Super Admins and notification system
- [ ] Set up automated daily backups at 00:00 HRS with point-in-time recovery
- [ ] Add analytics dashboard and content moderation features
- [ ] Ensure GDPR compliance with data export/deletion

---

## 2. DB Schema

| Table | Column | Type | Key/Constraint | Description |
|-------|--------|------|----------------|-------------|
| **Users** | id | UUID | PK | Unique user identifier |
| Users | email | VARCHAR(255) | UNIQUE, NOT NULL | User email for login |
| Users | password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| Users | name | VARCHAR(100) | NOT NULL | User display name |
| Users | role_id | INT | FK → Roles(id) | User's system role |
| Users | totp_secret | VARCHAR(255) | NULL | 2FA secret (Super Admin only) |
| Users | is_2fa_enabled | BOOLEAN | DEFAULT FALSE | 2FA activation status |
| Users | created_at | TIMESTAMP | DEFAULT NOW() | Account creation time |
| Users | last_login | TIMESTAMP | NULL | Last login timestamp |
| Users | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| **Roles** | id | INT | PK | Role identifier |
| Roles | name | VARCHAR(50) | UNIQUE, NOT NULL | Role name (User, Group Admin, Super Admin) |
| Roles | description | TEXT | NULL | Role description |
| **Groups** | id | UUID | PK | Unique group identifier |
| Groups | name | VARCHAR(100) | NOT NULL | Group name |
| Groups | description | TEXT | NULL | Group description |
| Groups | timezone | VARCHAR(50) | DEFAULT 'Asia/Kolkata' | Group timezone (GMT+5:30 default) |
| Groups | admin_id | UUID | FK → Users(id) | Group admin user |
| Groups | created_at | TIMESTAMP | DEFAULT NOW() | Group creation time |
| Groups | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| **GroupMembers** | id | UUID | PK | Membership record ID |
| GroupMembers | group_id | UUID | FK → Groups(id) | Associated group |
| GroupMembers | user_id | UUID | FK → Users(id) | Member user |
| GroupMembers | joined_at | TIMESTAMP | DEFAULT NOW() | Join timestamp |
| GroupMembers | day_streak | INT | DEFAULT 0 | Non-resetting streak counter (increments only) |
| GroupMembers | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| GroupMembers | UNIQUE(group_id, user_id) WHERE deleted_at IS NULL | | CONSTRAINT | Prevent duplicate active memberships |
| **SectionEntries** | id | UUID | PK | Entry identifier |
| SectionEntries | user_id | UUID | FK → Users(id) | Entry author |
| SectionEntries | group_id | UUID | FK → Groups(id) | Associated group |
| SectionEntries | section_type | ENUM | 'Health', 'Happiness', 'Hela' | Section category (Hela = Money) |
| SectionEntries | content | TEXT | NOT NULL | Entry content |
| SectionEntries | entry_date | DATE | NOT NULL | Date of entry (in group timezone) |
| SectionEntries | edit_count | INT | DEFAULT 0 | Number of edits (max 2 per day) |
| SectionEntries | is_flagged | BOOLEAN | DEFAULT FALSE | Content moderation flag |
| SectionEntries | flagged_reason | TEXT | NULL | Reason for flagging |
| SectionEntries | created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| SectionEntries | updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |
| SectionEntries | deleted_at | TIMESTAMP | NULL | Soft delete timestamp |
| SectionEntries | UNIQUE(user_id, group_id, section_type, entry_date) WHERE deleted_at IS NULL | | CONSTRAINT | One active entry per section per day |
| **Permissions** | id | INT | PK | Permission identifier |
| Permissions | role_id | INT | FK → Roles(id) | Associated role |
| Permissions | resource | VARCHAR(50) | NOT NULL | Resource type (e.g., 'group', 'entry') |
| Permissions | action | VARCHAR(50) | NOT NULL | Action type (e.g., 'create', 'edit', 'delete', 'view') |
| Permissions | scope | ENUM | 'own', 'group', 'all' | Permission scope |
| **Notifications** | id | UUID | PK | Notification identifier |
| Notifications | user_id | UUID | FK → Users(id) | Recipient user |
| Notifications | type | ENUM | 'incomplete_day', 'streak_milestone', 'admin_action', 'moderation' | Notification category |
| Notifications | title | VARCHAR(200) | NOT NULL | Notification title |
| Notifications | message | TEXT | NOT NULL | Notification content |
| Notifications | is_read | BOOLEAN | DEFAULT FALSE | Read status |
| Notifications | created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| **AuditLogs** | id | UUID | PK | Audit record ID |
| AuditLogs | user_id | UUID | FK → Users(id) | Actor user |
| AuditLogs | action | VARCHAR(100) | NOT NULL | Action performed |
| AuditLogs | resource_type | VARCHAR(50) | NOT NULL | Resource affected |
| AuditLogs | resource_id | UUID | NOT NULL | Resource identifier |
| AuditLogs | metadata | JSONB | NULL | Additional context |
| AuditLogs | ip_address | VARCHAR(45) | NULL | User IP address |
| AuditLogs | created_at | TIMESTAMP | DEFAULT NOW() | Action timestamp |
| **BackupLogs** | id | UUID | PK | Backup record ID |
| BackupLogs | backup_file | VARCHAR(255) | NOT NULL | Backup filename |
| BackupLogs | backup_size | BIGINT | NOT NULL | Backup size in bytes |
| BackupLogs | status | ENUM | 'success', 'failed' | Backup status |
| BackupLogs | created_at | TIMESTAMP | DEFAULT NOW() | Backup timestamp |

**Schema Validation Notes:**
- Soft delete implemented via `deleted_at` column across major tables
- `day_streak` increments only when all 3 sections completed; never decreases
- `edit_count` enforces max 2 edits per entry per day (same-day only)
- Group timezone stored as IANA timezone string (e.g., 'Asia/Kolkata' for GMT+5:30)
- Partial unique indexes (`WHERE deleted_at IS NULL`) prevent duplicate active records

---

## 3. Roles and Permissions

| Role | Resource | Actions Allowed | Scope | Notes |
|------|----------|-----------------|-------|-------|
| **User** | SectionEntries | Create, Edit (same day, max 2x), View | Own entries + Group members' view-only | Can only modify own entries created today |
| User | Groups | View | Own groups only | Can see groups they belong to |
| User | Users | View | Group members only | Can view profiles of users in same group |
| User | Notifications | View, Mark as Read | Own notifications | Receives alerts for incomplete sections, streak milestones |
| **Group Admin** | SectionEntries | Create, Edit, Soft Delete, View, Flag | All entries within managed groups | Can moderate content and soft delete inappropriate entries |
| Group Admin | Groups | Create, Edit, Soft Delete, View | Own managed groups | Can manage group metadata, timezone, and memberships |
| Group Admin | GroupMembers | Add, Remove (soft delete), View | Own managed groups | Control group membership |
| Group Admin | Analytics | View | Own managed groups | Access group-level analytics dashboard |
| Group Admin | Notifications | Create | Group members | Can send notifications to group members |
| **Super Admin** | SectionEntries | Create, Edit, Soft Delete, Restore, View | All groups and users | Unrestricted access across all data |
| Super Admin | Groups | Create, Edit, Soft Delete, Restore, View | All groups | Full group management globally |
| Super Admin | Users | Create, Edit, Soft Delete, Restore, View | All users | User account management |
| Super Admin | Roles | Assign, Promote, Demote | All users | Can change user roles (promote User → Group Admin, demote Group Admin → User) |
| Super Admin | Analytics | View | All groups | Global analytics dashboard |
| Super Admin | AuditLogs | View | All actions | Access to complete audit trail |
| Super Admin | BackupLogs | View, Trigger | All backups | Can view backup history and manually trigger backups |

**Permission Validation:**
- Middleware checks role + resource + action before processing requests
- Same-day edit restriction enforced at application layer (check entry_date vs current date in group timezone)
- Role promotion/demotion requires Super Admin + confirmation
- When new Group Admin is promoted, existing admin auto-demoted to User role

---

## 4. GraphQL Schema & Operations

### Type Definitions

```graphql
scalar DateTime
scalar Date
scalar UUID

enum RoleType {
  USER
  GROUP_ADMIN
  SUPER_ADMIN
}

enum SectionType {
  Health
  Happiness
  Hela
}

enum NotificationType {
  INCOMPLETE_DAY
  STREAK_MILESTONE
  ADMIN_ACTION
  MODERATION
}

type User {
  id: UUID!
  email: String!
  name: String!
  role: Role!
  is2FAEnabled: Boolean!
  createdAt: DateTime!
  lastLogin: DateTime
  groups: [GroupMember!]!
}

type Role {
  id: Int!
  name: RoleType!
  description: String
}

type Group {
  id: UUID!
  name: String!
  description: String
  timezone: String!
  admin: User!
  members: [GroupMember!]!
  createdAt: DateTime!
}

type GroupMember {
  id: UUID!
  user: User!
  group: Group!
  dayStreak: Int!
  joinedAt: DateTime!
}

type SectionEntry {
  id: UUID!
  user: User!
  group: Group!
  sectionType: SectionType!
  content: String!
  entryDate: Date!
  editCount: Int!
  isFlagged: Boolean!
  flaggedReason: String
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Notification {
  id: UUID!
  user: User!
  type: NotificationType!
  title: String!
  message: String!
  isRead: Boolean!
  createdAt: DateTime!
}

type DailyProgress {
  date: Date!
  completedSections: [SectionType!]!
  totalSections: Int!
  isComplete: Boolean!
}

type GroupAnalytics {
  groupId: UUID!
  totalMembers: Int!
  avgCompletionRate: Float!
  topContributors: [User!]!
  recentActivity: [SectionEntry!]!
}

type AuthPayload {
  token: String!
  user: User!
  requires2FA: Boolean!
}

type MutationResponse {
  success: Boolean!
  message: String!
}
```

### Queries

```graphql
type Query {
  # Authentication & User Management
  me: User!
  user(id: UUID!): User
  users(limit: Int, offset: Int): [User!]!
  
  # Groups
  myGroups: [Group!]!
  group(id: UUID!): Group
  groups(limit: Int, offset: Int): [Group!]!
  
  # Entries
  myEntries(groupId: UUID!, startDate: Date, endDate: Date): [SectionEntry!]!
  groupEntries(groupId: UUID!, userId: UUID, startDate: Date, endDate: Date): [SectionEntry!]!
  entry(id: UUID!): SectionEntry
  
  # Progress & Streaks
  dailyProgress(groupId: UUID!, userId: UUID!, date: Date!): DailyProgress!
  streak(groupId: UUID!, userId: UUID!): Int!
  
  # Notifications
  myNotifications(unreadOnly: Boolean): [Notification!]!
  
  # Analytics (Group Admin / Super Admin)
  groupAnalytics(groupId: UUID!, startDate: Date, endDate: Date): GroupAnalytics!
  globalAnalytics(startDate: Date, endDate: Date): [GroupAnalytics!]! # Super Admin only
  
  # Audit Logs (Super Admin only)
  auditLogs(limit: Int, offset: Int): [AuditLog!]!
}
```

### Mutations

```graphql
type Mutation {
  # Authentication
  register(email: String!, password: String!, name: String!): AuthPayload!
  login(email: String!, password: String!, totpCode: String): AuthPayload!
  logout: MutationResponse!
  enable2FA: String! # Returns TOTP secret
  verify2FA(totpCode: String!): MutationResponse!
  
  # User Management (Super Admin)
  promoteToGroupAdmin(userId: UUID!, groupId: UUID!): MutationResponse!
  demoteToUser(userId: UUID!, groupId: UUID!): MutationResponse!
  softDeleteUser(userId: UUID!, confirm: Boolean!): MutationResponse!
  restoreUser(userId: UUID!): MutationResponse!
  
  # Groups
  createGroup(name: String!, description: String, timezone: String): Group!
  updateGroup(id: UUID!, name: String, description: String, timezone: String): Group!
  softDeleteGroup(id: UUID!, confirm: Boolean!): MutationResponse!
  restoreGroup(id: UUID!): MutationResponse!
  
  # Group Members
  addGroupMember(groupId: UUID!, userId: UUID!): GroupMember!
  removeGroupMember(groupId: UUID!, userId: UUID!, confirm: Boolean!): MutationResponse!
  
  # Entries
  createEntry(groupId: UUID!, sectionType: SectionType!, content: String!, entryDate: Date!): SectionEntry!
  updateEntry(id: UUID!, content: String!): SectionEntry!
  softDeleteEntry(id: UUID!, confirm: Boolean!): MutationResponse!
  restoreEntry(id: UUID!): MutationResponse!
  
  # Content Moderation (Group Admin)
  flagEntry(id: UUID!, reason: String!): MutationResponse!
  unflagEntry(id: UUID!): MutationResponse!
  
  # Notifications
  markNotificationRead(id: UUID!): MutationResponse!
  markAllNotificationsRead: MutationResponse!
  
  # GDPR Compliance
  exportMyData: String! # Returns download URL
  deleteMyAccount(confirm: Boolean!): MutationResponse!
  
  # Backups (Super Admin)
  triggerBackup: MutationResponse!
}
```

### Error Handling

```graphql
type Error {
  code: String!
  message: String!
  field: String
}

# All mutations can return errors
extend type MutationResponse {
  errors: [Error!]
}
```

**GraphQL Validation Notes:**
- All queries/mutations check JWT authentication and role permissions
- Edit restrictions enforced: max 2 edits per entry, same-day only (checked via `editCount` and `entry_date`)
- Soft delete mutations require `confirm: true` parameter
- Rate limiting: 100 requests/min per user, cached at resolver level
- DataLoader pattern for N+1 query optimization on User/Group relationships

---

## 5. REST API Endpoints (Legacy Support)

| Method | URL | Description | Required Roles | Sample Payload | Error Handling |
|--------|-----|-------------|----------------|----------------|----------------|
| POST | `/api/v1/auth/register` | Register new user | Public | `{"email": "user@ex.com", "password": "pass123", "name": "John"}` | 409: Email exists, 400: Validation error |
| POST | `/api/v1/auth/login` | User login | Public | `{"email": "user@ex.com", "password": "pass123", "totpCode": "123456"}` | 401: Invalid credentials, 403: 2FA required |
| POST | `/api/v1/auth/logout` | User logout | All authenticated | `{}` | 401: Not authenticated |
| POST | `/api/v1/auth/2fa/enable` | Enable 2FA | Super Admin | `{}` | Returns TOTP QR code URL |
| POST | `/api/v1/auth/2fa/verify` | Verify 2FA code | Super Admin | `{"totpCode": "123456"}` | 400: Invalid code |
| POST | `/api/v1/roles/promote` | Promote user to Group Admin | Super Admin | `{"userId": "uuid", "groupId": "uuid", "confirm": true}` | 403: Unauthorized, 400: Missing confirmation |
| POST | `/api/v1/roles/demote` | Demote Group Admin to User | Super Admin | `{"userId": "uuid", "groupId": "uuid", "confirm": true}` | 403: Unauthorized, 400: Missing confirmation |
| GET | `/api/v1/analytics/group/:groupId` | Group analytics | Group Admin (own), Super Admin | N/A | 403: Not authorized |
| GET | `/api/v1/analytics/global` | Global analytics | Super Admin | N/A | 403: Not authorized |
| POST | `/api/v1/backups/trigger` | Manual backup | Super Admin | `{}` | 403: Not authorized |
| GET | `/api/v1/backups/logs` | Backup history | Super Admin | N/A | 403: Not authorized |
| GET | `/api/v1/gdpr/export` | Export user data | All authenticated | N/A | Returns ZIP download URL |
| DELETE | `/api/v1/gdpr/delete` | Delete account | All authenticated | `{"confirm": true}` | 400: Missing confirmation |

**API Versioning:** `/api/v1/` prefix for future compatibility. GraphQL endpoint at `/graphql`.

---

## 6. UI Elements

| Component | Purpose | Description/Example |
|-----------|---------|---------------------|
| **Header** | Navigation & user actions | Contains app logo, navigation links (Dashboard, Groups, Profile), logout button, notification bell icon |
| **Login/Register Forms** | Authentication | Email/password inputs with validation, 2FA code input (Super Admin), "Remember me" checkbox |
| **2FA Setup Modal** | Super Admin security | QR code display for TOTP app (Google Authenticator), verification input |
| **Daily Progress Bar** | Overall completion status | Top-level bar showing "2/3 sections completed today" with color coding (green/yellow/red) |
| **Section Cards** | Entry submission | Three cards (Health, Happiness, Hela/Money) with textarea input, character counter, submit button, and completion checkmark |
| **Info Icons** | Contextual help | Hoverable/clickable icons (ⓘ) displaying tooltip: "Health: Log physical activity. Example: 'Walked 30 minutes'" / "Hela (Money): Track expenses/income. Example: "Saved ₹500 today"" |
| **Section Progress Indicators** | Per-section status | Checkmark or progress ring showing completion; displays "2/2 edits used today" warning |
| **Calendar View** | Historical entries | Monthly calendar with date highlighting (green = all 3 complete, yellow = partial, gray = none); displays in group timezone |
| **Group Member List** | Team overview | Table/grid with columns: Avatar, Name, Streak (🔥 icon), Today's Status (3/3 ✓), Last Active |
| **Data Table** | View entries | Sortable, filterable table: Date, Section, Content (truncated), User, Flag Status (if admin), Edit Count |
| **Edit Modal** | Entry modification | Popup form with content textarea, "Edits remaining: X/2" indicator, Save/Cancel buttons (disabled if same-day restriction violated) |
| **Confirmation Dialog** | Destructive action verification | Modal for delete/demote operations: "Are you sure? This will soft-delete the record" with Yes/No buttons |
| **Group Management Panel** | Admin controls | Interface for creating/editing groups, timezone selector dropdown (defaults to Asia/Kolkata GMT+5:30), add/remove members |
| **Role Management Panel** | Super Admin controls | User list with "Promote to Group Admin" / "Demote to User" buttons, requires confirmation |
| **Streak Counter** | Gamification | Badge displaying: "🔥 12 day streak!" (non-resetting, increments only) |
| **Notification Center** | Alert management | Dropdown with unread count badge, list of notifications (incomplete sections, streak milestones, admin actions) |
| **Analytics Dashboard** | Data insights | Charts showing: completion rates over time, most active members, section popularity, group comparison (Super Admin only) |
| **Content Moderation Panel** | Group Admin tools | Flagged entries list with reason, unflag/delete buttons, moderation history |
| **GDPR Compliance Menu** | Data privacy | "Export My Data" (downloads ZIP) and "Delete My Account" buttons in profile settings |
| **Responsive Menu** | Mobile navigation | Hamburger menu for small screens, expanding to full nav on desktop |

**UI Validation:**
- All forms include client-side validation (required fields, format checks)
- Edit button disabled if edit_count ≥ 2 or entry_date ≠ today
- Timezone displayed prominently on calendar view (e.g., "Times shown in IST (GMT+5:30)")
- Loading states for async operations (spinners, skeleton screens)
- Toast notifications for success/error messages
- WCAG 2.1 AA accessibility compliance

---

## 7. Framework/Technical Stack

| Category | Recommendation | Reasoning |
|----------|---------------|-----------|
| **Frontend** | React 18 + Vite | Fast development with HMR; React ecosystem for UI components |
| **UI Framework** | Tailwind CSS + shadcn/ui | Utility-first styling with pre-built accessible components |
| **State Management** | Apollo Client | Industry-standard GraphQL client with caching and optimistic UI |
| **Backend** | Python 3.11 + FastAPI | High-performance async framework; auto-generated OpenAPI docs; native GraphQL support via Strawberry |
| **GraphQL Layer** | Strawberry GraphQL | Type-safe GraphQL for Python; integrates seamlessly with FastAPI; supports DataLoader |
| **Database** | PostgreSQL 15+ | Open-source, robust support for JSONB, timezone handling, partial indexes for soft deletes |
| **ORM** | SQLAlchemy 2.0 + Alembic | Powerful ORM with async support; Alembic handles database migrations |
| **Authentication** | JWT + PyOTP (2FA) | Stateless auth with JSON Web Tokens; PyOTP for TOTP 2FA implementation |
| **Password Hashing** | bcrypt (via passlib) | Industry-standard secure password hashing |
| **Task Queue** | Celery + Redis | For background tasks: notifications, daily backups at 00:00 HRS, analytics calculation |
| **Notification Service** | Celery Beat (scheduler) + Email (SendGrid/SMTP) | Scheduled tasks for incomplete day reminders; email delivery |
| **Backup Service** | pg_dump + S3-compatible storage | Automated daily PostgreSQL backups at 00:00 HRS (group timezone agnostic, uses UTC); stored off-site |
| **Rate Limiting** | slowapi (FastAPI) | Request rate limiting: 100 req/min per user, 2 edits/day per entry |
| **API Documentation** | FastAPI auto-docs + GraphQL Playground | Interactive API docs at `/docs`; GraphQL explorer at `/graphql` |
| **Deployment** | Docker + Docker Compose | Containerization for consistent environments; separate containers for API, DB, Redis, Celery worker |
| **Hosting** | Self-hosted VPS or Railway/Render | Cost-effective for open-source; Railway supports PostgreSQL + Redis out-of-box |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization for performance monitoring |
| **Logging** | Python logging + Sentry | Structured logs for debugging; Sentry for error tracking |

**Technical Stack Validation:**
- FastAPI provides both REST (`/api/v1/`) and GraphQL (`/graphql`) endpoints
- Celery Beat schedules daily backup at 00:00 UTC (midnight)
- Redis used for: rate limiting, Celery broker, caching GraphQL queries
- All components are open-source and production-ready

---

## 8. Sample Data Entries

### Users Table
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "alice@example.com",
  "password_hash": "$2b$12$KIXvhEQFvaldgZJGBJ4oH.sBfLCzEPA0HdEUBTmONXQvFHZ6hslKy",
  "name": "Alice Johnson",
  "role_id": 3,
  "totp_secret": "JBSWY3DPEHPK3PXP",
  "is_2fa_enabled": true,
  "created_at": "2025-01-15T10:00:00Z",
  "last_login": "2025-10-08T08:30:00Z",
  "deleted_at": null
}
```

### Groups Table
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Morning Wellness Warriors",
  "description": "Daily health, happiness, and money tracking",
  "timezone": "Asia/Kolkata",
  "admin_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-02-01T12:00:00Z",
  "deleted_at": null
}
```

### SectionEntries Table (Hela/Money)
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "group_id": "660e8400-e29b-41d4-a716-446655440001",
  "section_type": "Hela",
  "content": "Saved ₹500 by cooking at home. Avoided dining out.",
  "entry_date": "2025-10-08",
  "edit_count": 1,
  "is_flagged": false,
  "flagged_reason": null,
  "created_at": "2025-10-08T09:15:00Z",
  "updated_at": "2025-10-08T10:30:00Z",
  "deleted_at": null
}
```

### GroupMembers Table
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "group_id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "joined_at": "2025-02-01T12:05:00Z",
  "day_streak": 45,
  "deleted_at": null
}
```

### Notifications Table
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "STREAK_MILESTONE",
  "title": "🎉 Streak Milestone!",
  "message": "Congratulations! You've reached a 30-day streak in Morning Wellness Warriors!",
  "is_read": false,
  "created_at": "2025-10-08T18:00:00Z"
}
```

---

## 9. Implementation Specifications

### Streak Logic (Non-Resetting)
```python
# Pseudocode for streak calculation
def update_streak(user_id: UUID, group_id: UUID, date: Date):
    # Check if all 3 sections completed for the date
    entries = get_entries(user_id, group_id, date)
    sections_completed = set([e.section_type for e in entries])
    
    if sections_completed == {'Health', 'Happiness', 'Hela'}:
        # Increment streak (never decrements)
        group_member = get_group_member(user_id, group_id)
        group_member.day_streak += 1
        
        # Check for milestone notifications
        if group_member.day_streak in [7, 30, 100, 365]:
            send_notification(user_id, 'STREAK_MILESTONE', 
                f"You've reached {group_member.day_streak} days!")
```

### Edit Restrictions
```python
# Enforce same-day edits only, max 2 edits
def can_edit_entry(entry: SectionEntry, user_timezone: str) -> bool:
    group_tz = get_group_timezone(entry.group_id)
    today_in_group_tz = datetime.now(pytz.timezone(group_tz)).date()
    
    # Check if entry is from today
    if entry.entry_date != today_in_group_tz:
        raise PermissionError("Can only edit today's entries")
    
    # Check edit count
    if entry.edit_count >= 2:
        raise PermissionError("Maximum 2 edits per day reached")
    
    return True
```

### Role Promotion/Demotion
```python
# When promoting new Group Admin, demote existing admin
def promote_to_group_admin(user_id: UUID, group_id: UUID):
    group = get_group(group_id)
    
    # Demote current admin to User
    if group.admin_id:
        update_user_role(group.admin_id, role='USER')
        log_audit(action='DEMOTE_GROUP_ADMIN', user_id=group.admin_id)
    
    # Promote new admin
    update_user_role(user_id, role='GROUP_ADMIN')
    group.admin_id = user_id
    log_audit(action='PROMOTE_GROUP_ADMIN', user_id=user_id)
    
    # Send notifications
    send_notification(user_id, 'ADMIN_ACTION', 
        f"You are now admin of {group.name}")
```

### Automated Backup (Celery Beat)
```python
# Celery task scheduled at 00:00 UTC daily
@celery_app.task
def daily_backup():
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    backup_file = f"backup_{timestamp}.sql"
    
    # Run pg_dump
    os.system(f"pg_dump -U {DB_USER} {DB_NAME} > /backups/{backup_file}")
    
    # Upload to S3 or local storage
    upload_to_storage(backup_file)
    
    # Log backup
    BackupLog.create(
        backup_file=backup_file,
        backup_size=os.path.getsize(f"/backups/{backup_file}"),
        status='success'
    )
    
    # Retain last 30 days only
    cleanup_old_backups(days=30)
```

### GDPR Data Export
```python
# Export all user data as JSON
def export_user_data(user_id: UUID) -> str:
    user = get_user(user_id)
    groups = get_user_groups(user_id)
    entries = get_user_entries(user_id)
    notifications = get_user_notifications(user_id)
    
    data = {
        "user": user.to_dict(),
        "groups": [g.to_dict() for g in groups],
        "entries": [e.to_dict() for e in entries],
        "notifications": [n.to_dict() for n in notifications],
        "exported_at": datetime.utcnow().isoformat()
    }
    
    # Create ZIP file
    filename = f"user_data_{user_id}_{int(time.time())}.zip"
    with zipfile.ZipFile(f"/exports/{filename}", 'w') as zf:
        zf.writestr('data.json', json.dumps(data, indent=2))
    
    # Upload to temporary storage (expires in 7 days)
    download_url = upload_to_temp_storage(filename, expires_in_days=7)
    
    return download_url
```

### Content Moderation
```python
# Flag entry for review
def flag_entry(entry_id: UUID, reason: str, admin_id: UUID):
    entry = get_entry(entry_id)
    
    # Verify admin has permission
    if not is_group_admin(admin_id, entry.group_id):
        raise PermissionError("Only Group Admins can flag content")
    
    entry.is_flagged = True
    entry.flagged_reason = reason
    
    # Notify entry author
    send_notification(
        entry.user_id, 
        'MODERATION',
        f"Your entry has been flagged for review: {reason}"
    )
    
    log_audit(action='FLAG_ENTRY', user_id=admin_id, resource_id=entry_id)
```

### Notification System
```python
# Celery Beat task running at 20:00 in each group's timezone
@celery_app.task
def send_incomplete_reminders():
    groups = get_all_active_groups()
    
    for group in groups:
        # Get current time in group timezone
        group_tz = pytz.timezone(group.timezone)
        current_time = datetime.now(group_tz)
        
        # Only run at 20:00 (8 PM) in group timezone
        if current_time.hour == 20:
            today = current_time.date()
            
            for member in group.members:
                entries = get_entries(member.user_id, group.id, today)
                completed = set([e.section_type for e in entries])
                missing = {'Health', 'Happiness', 'Hela'} - completed
                
                if missing:
                    send_notification(
                        member.user_id,
                        'INCOMPLETE_DAY',
                        f"Reminder: Complete {', '.join(missing)} section(s) today!"
                    )
```

---

## 10. Security & Compliance

### Authentication Flow
1. User submits email/password via `/api/v1/auth/login`
2. Backend validates credentials with bcrypt
3. If user is Super Admin and 2FA enabled, require TOTP code
4. Generate JWT token (expires in 24 hours) with user_id and role
5. Return token + user object to frontend
6. Frontend stores token in httpOnly cookie (not localStorage for security)

### 2FA Implementation (Super Admin Only)
- Uses PyOTP library for TOTP (Time-based One-Time Password)
- Secret generated during setup, displayed as QR code
- 6-digit codes valid for 30 seconds
- Required for all Super Admin logins

### Permission Middleware
```python
# GraphQL resolver decorator
def requires_permission(resource: str, action: str, scope: str):
    def decorator(func):
        async def wrapper(self, info, **kwargs):
            user = get_current_user(info.context)
            
            # Check permission
            if not has_permission(user.role_id, resource, action, scope):
                raise PermissionError(f"Insufficient permissions for {action} on {resource}")
            
            # Check resource ownership for 'own' scope
            if scope == 'own':
                resource_id = kwargs.get('id')
                if not owns_resource(user.id, resource, resource_id):
                    raise PermissionError("Can only access own resources")
            
            # Check group membership for 'group' scope
            if scope == 'group':
                group_id = kwargs.get('groupId')
                if not is_group_member(user.id, group_id):
                    raise PermissionError("Not a member of this group")
            
            return await func(self, info, **kwargs)
        return wrapper
    return decorator
```

### Rate Limiting Strategy
- Global: 100 requests/minute per user (across all endpoints)
- Entry edits: Max 2 per entry per day (enforced via `edit_count` column)
- Failed login attempts: 5 attempts per hour per IP, then temporary lockout
- Backup triggers: Super Admin can manually trigger max 1 backup per hour

### GDPR Compliance Checklist
- ✅ Right to Access: User can export all their data as JSON
- ✅ Right to Erasure: User can request account deletion (soft delete)
- ✅ Right to Rectification: Users can edit their entries (within restrictions)
- ✅ Data Portability: Export provided in machine-readable JSON format
- ✅ Consent: Clear privacy policy during registration
- ✅ Data Retention: Soft-deleted records purged after 90 days (configurable)
- ✅ Audit Trail: All data modifications logged in AuditLogs table

---

## 11. Deployment Architecture

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: daily_tracker
      POSTGRES_USER: tracker_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000
    environment:
      DATABASE_URL: postgresql://tracker_user:${DB_PASSWORD}@postgres:5432/daily_tracker
      REDIS_URL: redis://redis:6379/0
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  celery_worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://tracker_user:${DB_PASSWORD}@postgres:5432/daily_tracker
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
  
  celery_beat:
    build: ./backend
    command: celery -A tasks beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://tracker_user:${DB_PASSWORD}@postgres:5432/daily_tracker
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_GRAPHQL_URL: http://localhost:8000/graphql

volumes:
  postgres_data:
```

### Backup Strategy
- **Frequency**: Daily at 00:00 UTC
- **Method**: `pg_dump` full database dump
- **Storage**: 
  - Local: `/backups` directory (mounted volume)
  - Remote: S3-compatible storage (AWS S3, MinIO, Backblaze B2)
- **Retention**: Last 30 daily backups, last 12 monthly backups
- **Encryption**: Backups encrypted at rest using AES-256
- **Restoration**: Automated script: `./scripts/restore_backup.sh <backup_file>`
- **Verification**: Weekly automated restore test to staging environment

---

## 12. Analytics Dashboard Specifications

### Group Admin Dashboard
**Metrics Available:**
- Group completion rate (overall %)
- Individual member completion rates
- Section popularity (which section completed most often)
- Active members (completed at least once in last 7 days)
- Streak leaderboard (top 10 members)
- Daily completion trend (line chart, last 30 days)

**Visualizations:**
- Line chart: Completion rate over time
- Bar chart: Member comparison (completion %)
- Pie chart: Section distribution
- Table: Member details with sortable columns

### Super Admin Dashboard
**Additional Metrics:**
- Total users, groups, entries across platform
- Most active groups
- User growth rate (new registrations per week)
- System health (API response times, error rates)
- Backup status and storage usage
- Flagged content review queue

**Visualizations:**
- Multi-group comparison dashboard
- Heatmap: Activity by day of week and hour
- Funnel chart: User onboarding completion
- Real-time activity feed

---

## 13. Mobile App Considerations

### GraphQL Benefits for Mobile
- **Efficient Data Fetching**: Request only needed fields, reduce bandwidth
- **Single Request**: Fetch related data (user + groups + entries) in one query
- **Offline Support**: Apollo Client cache works seamlessly offline
- **Real-time Updates**: GraphQL subscriptions for live notifications

### Recommended Mobile Stack
- **React Native**: Code sharing with web app (shared GraphQL queries)
- **Apollo Client**: Same client library for iOS/Android/Web
- **React Native Paper**: Material Design components
- **Expo**: Simplified build and deployment

### Mobile-Specific Features
- Push notifications (via Firebase Cloud Messaging)
- Biometric authentication (Face ID, fingerprint)
- Offline entry drafts (synced when online)
- Daily reminder notifications (customizable time per user)

---

## 14. Testing Strategy

### Backend Tests
- **Unit Tests**: FastAPI route handlers, business logic (pytest)
- **Integration Tests**: Database operations, GraphQL resolvers
- **Permission Tests**: Verify role-based access control
- **Load Tests**: Simulate 1000 concurrent users (Locust)

### Frontend Tests
- **Component Tests**: React components (Jest + React Testing Library)
- **E2E Tests**: User flows (Playwright or Cypress)
- **Accessibility Tests**: WCAG compliance (axe-core)

### Coverage Target
- Backend: 80% code coverage
- Frontend: 70% code coverage
- Critical paths (auth, entry creation, role management): 100%

---

## 15. Questions & Clarifications Addressed

✅ **Hela Definition**: Confirmed as Money/Finance tracking  
✅ **Streak Logic**: Non-resetting, increments only on completion  
✅ **Timezone Handling**: Group-level with GMT+5:30 default  
✅ **Role Promotion**: Super Admin API with auto-demotion of existing admin  
✅ **Edit Window**: Same-day only, max 2 edits  
✅ **Multi-Group Membership**: Supported, per-group streak tracking  
✅ **Soft Deletes**: Implemented across all major tables  
✅ **Notifications**: Celery-based system for reminders and milestones  
✅ **Analytics**: Dashboards for Group Admin and Super Admin  
✅ **Rate Limiting**: 2 edits/day per entry enforced  
✅ **2FA**: Implemented for Super Admin with TOTP  
✅ **API Versioning**: `/api/v1/` prefix added  
✅ **Backup Strategy**: Automated daily at 00:00 UTC  
✅ **Content Moderation**: Flagging system for Group Admins  
✅ **Mobile App**: GraphQL implementation ready for React Native  
✅ **GDPR Compliance**: Export and delete functionality included  
✅ **Backend Framework**: Changed to Python + FastAPI

---

## 16. Next Steps & Implementation Timeline

### Phase 1: Foundation (Weeks 1-2)
- Set up PostgreSQL database with schema
- Implement FastAPI backend with basic CRUD
- Configure JWT authentication
- Set up Docker development environment

### Phase 2: Core Features (Weeks 3-4)
- Implement GraphQL layer with Strawberry
- Build React frontend with Apollo Client
- Entry creation with edit restrictions
- Streak calculation logic

### Phase 3: Advanced Features (Weeks 5-6)
- Role management (promote/demote APIs)
- Group timezone handling
- Notification system with Celery
- 2FA for Super Admin

### Phase 4: Analytics & Moderation (Week 7)
- Analytics dashboards
- Content moderation panel
- Audit logging

### Phase 5: Compliance & Polish (Week 8)
- GDPR export/delete
- Automated backup system
- Rate limiting
- UI/UX refinements

### Phase 6: Testing & Deployment (Weeks 9-10)
- Comprehensive testing (unit, integration, E2E)
- Load testing and optimization
- Production deployment
- Documentation and training

---

## 17. Maintenance & Monitoring

### Daily Tasks (Automated)
- Database backup at 00:00 UTC
- Cleanup of expired temp files (data exports)
- Notification reminders at 20:00 per group timezone

### Weekly Tasks
- Review flagged content in moderation queue
- Check backup restoration integrity
- Monitor error logs via Sentry
- Review analytics for unusual patterns

### Monthly Tasks
- Update dependencies (security patches)
- Review and optimize database queries
- Audit user roles and permissions
- Archive/purge soft-deleted records (90+ days old)

### Monitoring Alerts
- API response time > 500ms
- Error rate > 1%
- Database connections > 80% pool size
- Backup failure
- Disk usage > 85%

---

**Architecture Review Complete**: This comprehensive design addresses all requirements with scalable, secure, and maintainable architecture. The Python + FastAPI backend with GraphQL support provides optimal performance for both web and mobile clients, while the robust permission system ensures data security across all user roles.

---

## Part B: Architecture Modifications (verbatim)

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
