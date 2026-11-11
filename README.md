# Document Approval Workflow

A submitter submits a document (pasted text **or** an uploaded file) and tracks its status; a reviewer sees submissions and approves or rejects them. Django REST Framework API + React (Vite) client, SQLite storage.

- **Loom walkthrough:** (sent through Google form/email)
- **Hosted URL:** not hosted (bonus item skipped); run locally as below.

## Setup

Requires Python 3.11+ and Node 20+.

**Backend** (http://127.0.0.1:8000)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_users     # alice, bob (submitters), rita (reviewer); password: demo-pass
python manage.py runserver
```

**Frontend** (http://localhost:5173, proxies `/api` to the backend)
```bash
cd frontend
npm install
npm run dev
```

Swagger UI: http://127.0.0.1:8000/api/docs/ (OpenAPI schema generated from the code with drf-spectacular, not hand-written).

Config is via env vars, none required for local use: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DEMO_PASSWORD`. The demo password is a throwaway for seeded local users; no real secrets are in the repo.

## Tests

One command from the repo root: runs the Django tests, then the Vitest tests (run `npm install` in `frontend/` once first).
```bash
npm test
```
The backend step uses `$PYTHON` if set, else `backend/.venv`, else the `python` on your PATH, so activate the environment you installed `backend/requirements.txt` into (or set `PYTHON`). If Django isn't found it says so instead of crashing. `npm run test:backend` / `npm run test:frontend` run each half. Currently 66 backend + 21 frontend tests.

## API design

All routes are under `/api`; authenticated routes take `Authorization: Token <key>`.

| Method & path | Who | Purpose |
|---|---|---|
| `POST /auth/login/` | anyone | `{username, password}` → `{token, user:{id, username, role}}` |
| `GET /auth/me/` | any user | current user |
| `POST /submissions/` | submitter | create: `title` + exactly one of `content` (text) or `file`. JSON or multipart. → `201` |
| `GET /submissions/?status=` | any user | list. Submitters get their own, reviewers get all. Optional filter `pending\|approved\|rejected` |
| `GET /submissions/{id}/` | owner or reviewer | one submission |
| `PATCH /submissions/{id}/status/` | reviewer | `{status: "approved"\|"rejected"}` → updated submission |
| `GET /submissions/{id}/file/` | owner or reviewer | download the uploaded file |

Submission shape: `{id, title, content, file_name, status, submitted_by, created_at, decided_by, decided_at}`.

**Errors** use one envelope everywhere, so the client has a single code path:
`{"error": {"code": "...", "message": "...", "details": {"field": ["msg"]}}}` (`details` only for validation errors).

| Status | When |
|---|---|
| 400 | invalid payload (missing/blank title, neither or both of content/file, bad file type/size, unknown status, bad `?status=`, malformed JSON) |
| 401 | missing or invalid token |
| 403 | wrong role (reviewer submitting, submitter deciding) |
| 404 | unknown id, **or another submitter's document** (404 rather than 403 so ids can't be probed) |
| 409 | deciding a submission that is already approved/rejected |

**Reasoning**
- Status is changed through its own sub-resource (`PATCH …/status/`) with a body that can only contain a decision. Clients can never edit title, owner, or arbitrary fields through it, and `pending` is not an accepted value.
- The list is scoped by role in one place (`Submission.objects.visible_to(user)`), and every view uses it, so there is no endpoint that forgets the check.
- Files are never served statically; downloads go through a permission-checked endpoint.
- No pagination yet: the list is a plain array to keep the first iteration simple (see production notes).

## Major decisions

**Data model.** `accounts.User` (custom user, `role` = submitter | reviewer) and `submissions.Submission` (`title`, `content`, `file`, `submitted_by`, `status`, `created_at`, `updated_at`, `decided_by`, `decided_at`). The `decided_*` fields are a cheap audit trail. Two DB `CheckConstraint`s back the rules the API also enforces: a document has either text or a file (never both/neither), and a pending submission has no decider while a decided one always does.

**State machine.** `pending → approved | rejected`; both are terminal. It is a plain transition table in `submissions/services.py`, so adding a state means adding one entry. The decision is a single conditional `UPDATE … WHERE status = <what we read>`: if two reviewers race, one wins and the other gets a 409, with no lock needed.

**Roles.** Exclusive (a user is a submitter or a reviewer), enforced on the server by permission classes, not just hidden in the UI. Because roles are exclusive, a reviewer cannot submit and so cannot review their own document; `decide()` also refuses `decided_by == submitted_by`, in case roles ever overlap.

**Auth.** DRF token auth with seeded demo users: enough to demonstrate server-side roles without building user management.

**Document = text or file.** The spec allows "a file, or an input", so both are supported (file types: pdf, txt, md, docx; max 5 MB; text max 20k chars).

**Layering.** Views are thin; business rules live in `services.py` and are unit-tested without HTTP; validation lives in serializers/validators; the frontend has a single `api/client.js` that all calls go through.

**Trade-offs for the time budget.** Local disk file storage, non-expiring tokens kept in `localStorage`, no pagination, no hosting, no reviewer comment on a decision, no user registration.

## Project layout

```
backend/
  config/        settings, urls, error envelope (exceptions.py)
  accounts/      User + role, login, role permissions, seed_demo_users
  submissions/   models, services (state machine), serializers, validators, views, tests/
frontend/src/
  api/           fetch wrapper + endpoint functions
  auth/          session context        features/  submitter/, reviewer/
  components/    StatusBadge, ErrorBanner, Spinner, SubmissionList, ...
  test/          Vitest tests
```

## AI tools used

- **Claude Code** (Claude desktop app, Claude Sonnet 5.5) for scaffolding, implementing the backend and tests, and debugging (e.g. the error handler and test-speed fixes found by running the suite).
- A Claude Code subagent built the first version of the React frontend from a written brief while I wrote the backend tests; I reviewed the code and verified it manually against the running API.
- **apcd** is a Claude Code skill I developed myself. It keeps a short `CLAUDE.md` (decisions, rules, progress log) and a verbatim copy of the spec in `docs/`, so a fresh AI session resumes with full context instead of re-deriving it, and the spec is checked line by line rather than from memory.

I made the design calls (stack, roles, state machine, scope) and can walk through every part of the code.

## What I'd add for production

- Postgres, object storage (S3) for files with virus scanning and content-type sniffing, and a real `SECRET_KEY`/env-based config.
- Token expiry/rotation or JWT/SSO, HTTPS-only cookies, rate limiting on login, CORS/CSRF review.
- Pagination, search and sorting on the list; optimistic concurrency/ETags in the UI.
- Reviewer comments on decisions, an immutable audit log of every status change, notifications (email/webhook) to the submitter.
- User management and a role/permission model beyond two fixed roles (e.g. reviewer groups).
- CI (tests, lint, type checks), structured logging, error monitoring, Docker, and a hosted deployment.
- Browser end-to-end tests (Playwright) on top of the unit/integration tests.
