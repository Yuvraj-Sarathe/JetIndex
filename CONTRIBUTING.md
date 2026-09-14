<!-- generated-by: gsd-doc-writer -->

# Contributing to JetIndex

Thank you for contributing to JetIndex (APIx) — the real-time airfare price index for India's CPI.

## Development Setup

See [README.md](README.md#quick-start) for prerequisites and first-run instructions.

```bash
git clone https://github.com/Yuvraj-Sarathe/JetIndex.git
cd JetIndex
cp .env.example .env
make setup
make up
```

## Branch Naming

```
feat/<yourname>/<topic>      # new features
fix/<yourname>/<topic>       # bug fixes
```

Never push directly to `main`. All changes go through Pull Requests.

## How to Submit a Pull Request

1. Create a branch from `main`
2. Make your changes
3. Run tests: `make test` (Python) or `cd frontend && npm run lint && npm run build` (frontend)
4. Push your branch and open a Pull Request
5. CI runs automatically — lint + tests must pass
6. Request review from @Yuvraj-Sarathe
7. After approval, squash-merge into `main`

## Coding Standards

### Python

- **Linter:** Ruff (`ruff check .`)
- **Formatter:** Ruff (`ruff format .`)
- **Type hints:** Required for all function signatures
- **Schemas:** `pipeline/schemas.py` is the frozen data contract — changes require a tagged PR

### Frontend

- **Linter:** ESLint (`npm run lint`)
- **Formatter:** Prettier (`npx prettier --write "src/**/*.{js,jsx,json,css}"`)
- **Build:** Must pass (`npm run build`)
- **Data:** Always fetch from API via `src/api/client.js` — never hard-code

## What NOT to Commit

- `.env` — contains secrets
- `data/raw/*` — raw scrape payloads
- `*.har` — network captures
- `node_modules/`, `__pycache__/`, `.venv/`

## Folder Ownership

| Folder | Owner |
|--------|-------|
| `app/`, `config/`, Docker files | Yuvraj |
| `scrapers/` | Sourabh + Abhay |
| `pipeline/` | Vanshika |
| `db/`, `engine/` | Sourabh + Abhay |
| `frontend/` | Mehak |
| `docs/`, `slides/`, `demo/` | Sneh |

Ask before modifying files outside your ownership area.

## Database Queries

Use `db/queries.py` for all database access. Do not write raw SQLAlchemy in your modules:

```python
# Correct
from db.queries import get_active_routes
routes = get_active_routes(session)

# Wrong
from sqlalchemy import select
from db.models import Route
routes = session.scalars(select(Route).where(Route.active == True)).all()
```

## Common Commands

| What | Command |
|------|---------|
| Start everything | `make up` |
| Stop everything | `docker compose down` |
| View logs | `docker compose logs -f api` |
| Run tests | `make test` |
| Lint Python | `ruff check .` |
| Format Python | `ruff format .` |
| Access database | `make psql` |

## Issue Reporting

Open an issue on [GitHub Issues](https://github.com/Yuvraj-Sarathe/JetIndex/issues) with:

- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Docker version, browser)
