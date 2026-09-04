## What

<!-- Brief description of the change. What does this PR do? -->

## Why

<!-- Why is this change needed? Link to issue if applicable. -->

## Module / Owner

- **Module:** <!-- app/ | scrapers/ | pipeline/ | db/ | engine/ | frontend/ | docs/ -->
- **Owner:** <!-- @who should review? -->

## How Tested

<!-- How did you verify this works? Paste the exact commands you ran. -->

```bash
# Examples:
# make test
# pytest tests/test_pipeline/ -v
# cd frontend && npm run lint && npm run build
# curl -H "Authorization: Bearer <token>" http://localhost:8000/health
```

## Screenshots / Screen Recording

<!-- If UI changed, paste screenshots or a short recording here. -->
<!-- Delete this section if no UI changes. -->

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Refactor (no functional changes)
- [ ] Documentation update
- [ ] CI/CD or build change

## Checklist

- [ ] I have tested this change locally (`make test` / `npm run build`)
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] I have updated documentation if needed
- [ ] No secrets, tokens, or `.env` files committed
- [ ] Code follows the project's style guidelines (`ruff check .` / `npm run lint`)
- [ ] This PR does NOT modify `pipeline/schemas.py` (data contract is frozen)

> **Note:** If this PR modifies `pipeline/schemas.py`, add `data-contract` to the PR title and ping @Yuvraj-Sarathe and @VanshikaShrivastava-web before merging.
