# Springboard Take-home: Document Approval Workflow
Product Engineer (Full stack) take-home: submitters submit documents and track status, reviewers approve/reject. Django+DRF API, React (Vite) client, SQLite. Spec: `docs/spec.md`. Run/API/decisions live in README.md (submission-facing only).

## Decisions (inputs, revisable)
- Stack: Django + DRF, React (Vite), SQLite, DRF token auth with seeded demo users (2026-11-11)
- Roles exclusive (submitter | reviewer), enforced server-side; submitters see only own docs (2026-11-11)
- State machine pending -> approved|rejected, terminal; 2nd decision = 409 (2026-11-11)
- Decision = status only (no comment); Swagger via drf-spectacular; Vitest for a few FE tests (2026-11-11)

## Rules & conventions
- Python: always use the `env1` conda env (see Layout), never the system python or a new venv.
- Ask whenever something is ambiguous or the decision is the user's to make.
- Keep all text super concise; waste no tokens.
- **Read the spec properly (`docs/spec.md`, only one provided) and satisfy every line as worded.** Re-read it before planning, before each phase, and before the README; check each requirement against it. Don't skim, don't paraphrase away detail (e.g. the spec says "submit a document (a file, or an input)").
- Judged on: clean modular design, edge cases/errors, readable code, real tests, requirements-to-tech reasoning. User must be able to explain every line on video: keep it simple, no over-engineering, no features beyond spec.
- Plan first, wait for the user's OK. Build order: backend, tests, frontend, README.
- Small logical commits with meaningful messages. No secrets in repo. No hardcoded API schemas.
- README is for the interviewer only (setup, API, decisions, AI tools used, production list, Loom placeholder, a short note on apcd: the user's own Claude Code skill that keeps project docs/progress for session resume). No process chatter.

<!-- apcd:protocol v1 -->
## Resume & upkeep
- Resume ("pick up where we left", "what's next"): verify Progress against `git status` and `git log <Checkpoint>..HEAD` (ignore docs-only commits); run `Check`, and on failure fix or flag it first (flip a regressed item back to `[ ]`); take the first Next item not `[!]`; say "Resuming: <item>"; open only the docs it needs; continue. Ask instead if the item is ambiguous, Progress contradicts the repo, or the step is irreversible, costly or the user's call. If nothing is unblocked, report the blockers.
- Upkeep, same pass as the work: rewrite Now; one Next item at a time, done only after its check, evidence in Done; append surprises and failed approaches to Notes; update README Status and affected docs. Notes and Decisions are append-only (supersede, don't delete).
- Session end: refresh Progress and `Checkpoint`; leave `Check` passing or say in Now why not; suggest a commit, never commit unasked.
- Only the main session edits Progress; subagents get a brief (objective, output, boundaries, done-criteria) and report back.
- Overflow (~20 Progress lines, ~150 entry-file lines): move the oldest entries verbatim to `<docs>/progress-archive.md`, leave a one-line pointer; never read it unless asked.
<!-- /apcd:protocol -->

## Layout (non-obvious only)
- `backend/`: Django (`config/`, `accounts/`, `submissions/`; rules in `submissions/services.py`); Python env: conda `env1` (`S:\Microsoft\DevSoftware\miniforge3\envs\env1`), deps from `backend/requirements.txt`; no project venv
- `frontend/`: Vite React; all HTTP via `src/api/client.js`
- root `package.json`: `npm test` runs both suites (env1 must be first on PATH: `python` resolves to the system 3.11 which lacks Django)

## Docs (read only when needed)
- `docs/spec.md`: verbatim take-home spec; read before every phase

## Progress
- Checkpoint: 9aa2db3 (2026-11-11)
- Check: `npm test` (66 backend + 21 frontend pass)
- Now: all phases built and committed except README commit; remaining user-side: Loom link, push to private repo, share with enghiring@springboard.com
- Next:
  1. [ ] User: record Loom, fill README placeholder, push, share repo access
- Done: backend + tests, frontend + tests, README (2026-11-11); manual E2E (login, create, approve) via browser pane (2026-11-11)
- Notes: Bash heredocs with long bodies failed to parse here; use Write tool. Test hasher swapped to MD5 under `manage.py test` (PBKDF2 made suite take 112s). DRF converts Http404 before the exception handler; use response.data["detail"].code, not exc.
- Open questions: none
- Notes (2026-11-12): earlier I used a `backend/.venv` off system Python 3.11 against the user's rule; removed it, all checks re-run on env1 (3.12.10): 66+21 pass.
