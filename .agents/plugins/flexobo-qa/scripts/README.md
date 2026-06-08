# Flexobo QA Plugin Scripts

The plugin intentionally reuses the repository runner at:

```bash
scripts/qa_runner.py
```

Keeping the executable runner in the project root lets the same command work from
Codex, the terminal, and CI without duplicating test execution logic inside the
plugin folder.
