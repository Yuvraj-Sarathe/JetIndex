# `.github/`

- `workflows/backend-ci.yml` — ruff + pytest on every PR.
- `workflows/frontend-ci.yml` — eslint + build on `frontend/**` changes.
- `PULL_REQUEST_TEMPLATE.md` — what/why/how-tested/screenshots checklist.
- `ISSUE_TEMPLATE/` — `task.md` (owner, module, DoD) and `bug.md`.

Branch protection on `main`: PR required, 1 approval, CI green. Yuvraj is admin.
