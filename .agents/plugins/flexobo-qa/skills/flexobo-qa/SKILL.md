---
name: flexobo-qa
description: Run and analyze this repository's Flexobo Python Playwright automation suite with pytest, Allure artifacts, Playwright traces, screenshots, videos, and a Markdown QA report.
---

# Flexobo QA

Use this skill when the user asks Codex to test the Flexobo website, run automation, run Playwright tests, check regression/smoke flows, debug failed QA tests, or analyze the latest QA output in this repository.

## Project Shape

- Test project root: `/Users/mirzobek/Flexobo- Project`.
- Tests use Python, pytest, pytest-playwright, Playwright, and Allure.
- Page Objects live in `pages/`.
- Tests live in `tests/`.
- Role fixtures live in `conftest.py`.
- The preferred entrypoint is `scripts/qa_runner.py`.
- Test outputs are written under `qa-artifacts/<timestamp>/`.

## Default Workflow

1. Start from the project root:

   ```bash
   cd "/Users/mirzobek/Flexobo- Project"
   ```

2. Check the working tree before edits or broad runs:

   ```bash
   git status --short
   ```

3. Prefer the QA runner instead of calling pytest directly:

   ```bash
   .venv/bin/python scripts/qa_runner.py tests
   ```

4. For a focused request, pass the requested file, folder, marker, or keyword:

   ```bash
   .venv/bin/python scripts/qa_runner.py tests/test_login.py
   .venv/bin/python scripts/qa_runner.py tests/permissions
   .venv/bin/python scripts/qa_runner.py tests -k login
   .venv/bin/python scripts/qa_runner.py tests -m smoke
   ```

5. For visual debugging, use headed mode:

   ```bash
   .venv/bin/python scripts/qa_runner.py tests/test_login.py --headed
   ```

6. After a run, open the generated report:

   ```bash
   sed -n '1,220p' qa-artifacts/<timestamp>/qa-report.md
   ```

7. If tests fail, inspect:

   - `qa-artifacts/<timestamp>/qa-report.md`
   - `qa-artifacts/<timestamp>/pytest.log`
   - `qa-artifacts/<timestamp>/allure-results/`
   - Playwright trace/video/screenshot paths mentioned in pytest output.

## Commands

Collect only:

```bash
.venv/bin/python scripts/qa_runner.py tests --extra "--collect-only -q -p no:plugins.allure_plugin"
```

Run one file:

```bash
.venv/bin/python scripts/qa_runner.py tests/test_login.py
```

Run with retries:

```bash
.venv/bin/python scripts/qa_runner.py tests/test_login.py --reruns 1
```

Run with timeout if `pytest-timeout` is installed:

```bash
.venv/bin/python scripts/qa_runner.py tests/test_login.py --timeout 180
```

## Reporting Rules

When reporting back to the user:

- Say which command ran.
- Include the generated `qa-report.md` path.
- Summarize pass/fail counts from pytest output.
- For failures, list the failed test names first.
- Explain likely cause using logs/traces/screenshots when available.
- Mention any test-data or environment caveat, especially `.env` credentials or live backend state.

## Editing Rules

- Do not modify user tests unless the user asks for fixes.
- Do not touch `.env`.
- Do not revert unrelated dirty files.
- Prefer fixing selectors or Page Object methods over duplicating locators in tests.
- Prefer `expect(...)` and deterministic waits over new `wait_for_timeout(...)`.
