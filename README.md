# SkillPulse

SkillPulse is a next-day construction labour marketplace connecting small contractors with skilled daily-wage workers using skill, availability, location, experience, wage compatibility and reliability.

## Architecture

- **Frontend:** React 19 + Vite
- **Backend:** Flask + Flask-SQLAlchemy + JWT
- **Database:** MySQL 8.x
- **Matching:** hard constraints + configurable weighted ranking + Haversine distance
- **ML:** reproducible logistic-regression reliability model trained on clearly labelled synthetic development data

## 1. Prerequisites

- Python 3.10+
- Node.js 20+
- MySQL 8.x

## 2. Database

Create the database and schema:

```sql
CREATE DATABASE skillpulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Then import `database/schema.sql` or allow `backend/run.py` to create missing tables.

## 3. Environment

Copy `backend/.env.example` to `backend/.env` and set your own values. Never commit `backend/.env`.

Frontend API URL is configured through `frontend_bup2/.env`:

```text
VITE_API_BASE=http://localhost:5000/api
```

## 4. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Backend health check: `GET http://localhost:5000/api/health`

## 5. ML model

The repository contains a reproducible synthetic training pipeline. It does **not** claim the synthetic records are real SkillPulse history.

```powershell
cd backend
python ml/training/train_model.py
```

This creates:

- `ml/data/reliability_training.csv`
- `ml/models/reliability_model.pkl`
- `ml/models/metrics.json`

The model is used by the matching service to estimate worker reliability. If the model file is missing, the application uses the transparent rule-based reliability fallback.

## 6. Seed development data

```powershell
cd backend
python seed_data.py
```

The seed script creates development-only users and records. The demo password is documented in the seed script and must not be reused in production.

## 7. Frontend

```powershell
cd frontend_bup2
npm install
npm run dev
```

Open the Vite URL shown in the terminal.

## 8. Main workflows

### Worker

Register → configure skills → set availability → receive ranked jobs → apply → receive notification → complete work → build rating/reliability history.

### Contractor

Register → post labour requirement → retrieve ranked workers → select worker → confirm/start/complete job → rate worker.

## 9. Matching logic

Workers are first removed when they fail a hard requirement:

1. Required skill
2. Availability on the job date
3. Existing conflicting assignment on the same date
4. Maximum travel radius

Remaining workers are ranked using configurable weights for location, experience, wage compatibility and reliability. The active weights are in `backend/config/matching_weights.json`.

## 10. API documentation

See `docs/API.md`.

## 11. Model documentation

See `backend/ml/MODEL_CARD.md`. The evaluation metrics in `backend/ml/models/metrics.json` are test-set results on synthetic data only.

## 12. Security notes

- Passwords are bcrypt-hashed.
- JWT-protected routes enforce roles.
- Admin accounts cannot be created through public registration.
- Environment-specific secrets belong in `.env` and are excluded from the deliverable.
- CORS is restricted by `FRONTEND_ORIGIN` instead of allowing every origin by default.
- Client-side validation is supplemented by server-side validation.

## Known limitations

The current project does not have real historical SkillPulse outcomes, so the ML model is a synthetic-data development model. For a production deployment, retrain and validate it on consented, representative historical outcomes and monitor drift/fairness.
