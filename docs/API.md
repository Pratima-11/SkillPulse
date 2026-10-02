# SkillPulse API

Base URL: `http://localhost:5000/api`

## Public

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | No | Backend health |
| GET | `/public/stats` | No | Live platform counters |
| GET | `/jobs` | No | Open jobs with optional skill, area, wage, date and distance filters |
| GET | `/jobs/:id` | No | Job detail |

## Authentication

| Method | Endpoint | Auth | Body |
|---|---|---|---|
| POST | `/auth/register` | No | email, password, role + role fields |
| POST | `/auth/login` | No | email, password |
| GET | `/auth/me` | JWT | — |

## Worker

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/worker/profile` | Worker |
| PUT | `/worker/profile` | Worker |
| POST | `/worker/skills` | Worker |
| POST | `/worker/availability` | Worker |
| GET | `/worker/jobs/recommended` | Worker |
| GET | `/worker/applications` | Worker |
| GET | `/worker/dashboard-stats` | Worker |
| POST | `/jobs/:id/apply` | Worker |

## Contractor

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/contractor/profile` | Contractor |
| PUT | `/contractor/profile` | Contractor |
| POST | `/contractor/jobs` | Contractor |
| GET | `/contractor/jobs` | Contractor |
| GET | `/contractor/jobs/:id/recommended-workers` | Contractor |
| POST | `/contractor/applications/:id/select` | Contractor |
| POST | `/contractor/applications/:id/reject` | Contractor |
| POST | `/contractor/jobs/:id/status` | Contractor |
| POST | `/contractor/applications/:id/rate` | Contractor |
| GET | `/contractor/dashboard-stats` | Contractor |

## Notifications

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/notifications` | JWT |
| POST | `/notifications/:id/read` | JWT |
| POST | `/notifications/read-all` | JWT |

## Admin

| Method | Endpoint | Auth |
|---|---|---|
| GET | `/admin/stats` | Admin |
| GET | `/admin/workers` | Admin |
| POST | `/admin/workers/:id/verify` | Admin |
| GET | `/admin/contractors` | Admin |
| GET | `/admin/jobs` | Admin |
| POST | `/admin/users/:id/deactivate` | Admin |
| POST | `/admin/users/:id/activate` | Admin |
