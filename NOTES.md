# QA Automation Notes

## Project
- Flexobo.uz automation tests are written with Python, Playwright, pytest, and Allure.
- Test project root: `/Users/mirzobek/Flexobo- Project`.
- Backend project is separate: `/Users/mirzobek/flexobo-backend`.
- Use the project virtualenv for test commands: `.venv/bin/pytest`.
- Global `pytest` currently fails because `allure` is not installed globally.

## Current Test Structure
- Page objects live in `pages/`.
- Tests live in `tests/`.
- Permission tests live in `tests/permissions/`.
- Validation tests live in `tests/validation/`.
- Main page objects currently exist for landing, login, profile, loads, and trips.

## Fixtures And Roles
- Role fixtures are defined in `conftest.py`.
- Available logged-in fixtures:
  - `logged_in_broker`
  - `logged_in_load_owner`
  - `logged_in_carrier`
  - `logged_in_owner_operator`
- Multi-user tests use separate browser contexts through separate fixtures.
- Old compatibility fixture `logged_in` uses `EMAIL` and `PASSWORD`.

## Test Patterns
- Tests use Allure decorators: `feature`, `story`, and sometimes `severity`.
- Page Object methods usually return `self` for chaining.
- Role-based checks use pytest parametrization and matrix dictionaries.
- Multi-user bid flows use unique prices to identify created loads.
- Some SPA pages behave better through sidebar navigation than direct `goto`.
- `pytest.ini` excludes `setup` tests by default with `-m "not setup"`.

## Important Commands
- Collect tests: `.venv/bin/pytest --collect-only -q`
- Run all default tests: `.venv/bin/pytest`
- Run setup test explicitly: `.venv/bin/pytest tests/test_setup_broker_bid_limit.py -m setup -v -s`

## Current Collection Snapshot
- Last checked: 2026-05-07.
- `.venv/bin/pytest --collect-only -q` collected 171 tests.
- 1 setup test was deselected by default, 170 selected.

## Backend Map
- `main-service`: loads, trips, bids, boards, companies, roles.
- `tms-service`: fleet, drivers, orders, transports, TMS roles.
- `billing-service`: usage counters, plan limits, bid limits.
- `users-service`: auth, profile, user roles.

## Working Decisions
- Do not revert or overwrite existing user changes.
- Prefer adding or reusing Page Object methods instead of duplicating locators in tests.
- Prefer explicit waits and `expect` checks over new `wait_for_timeout` calls when practical.
- Keep new tests consistent with the existing Uzbek comments and current project style.
- Keep important requirements, commands, decisions, and known issues in this file as work continues.

## Known Improvement Areas
- Several tests use fixed `wait_for_timeout`; replace gradually with deterministic waits.
- Bid, usage, received bids, and my bids flows may benefit from dedicated Page Objects.
- Hardcoded unique prices can eventually be replaced with dynamic values.
- Permission tests can be cross-checked against backend controller and guard behavior.
