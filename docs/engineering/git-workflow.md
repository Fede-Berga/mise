## Git Workflow for Mise

To keep the project maintainable and "enterprise ready", we recommend a simple, disciplined branching model:

- `main` — always deployable, tagged releases come from here.
- `develop` — integration branch for ongoing work.
- `feature/*` — short-lived branches for specific tasks.
- `hotfix/*` — urgent fixes branched from `main`.

### Branching Rules

- Create branches from:
  - `develop` for normal features (`feature/menu-builder`, `feature/ai-forecasting`).
  - `main` for production hotfixes (`hotfix/fix-order-timeout`).
- Keep branches small and focused; prefer multiple small PRs over one very large one.

### Pull Requests

- Target `develop` for feature work; target `main` for hotfixes.
- Require:
  - Passing CI (`CI` workflow).
  - At least one review when possible (for solo work, treat CI as your "second pair of eyes").

### Releases

- When `develop` is stable:
  - Merge `develop` into `main` via PR.
  - Tag `main` with semantic version: `v0.x.y`.
  - Use release notes to summarize:
    - New features.
    - Breaking changes.
    - Migration steps (DB changes, config changes).

### Commit Style

- Use clear, action-oriented messages:
  - `feat(order): add order state machine`
  - `fix(inventory): correct stock deduction`
  - `chore(ci): add web build to CI`
- Group refactors, tests, and behavior changes in separate commits when practical.

