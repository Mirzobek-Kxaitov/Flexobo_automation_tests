#!/usr/bin/env python3
"""Send a compact GitHub Actions QA result notification to Telegram."""

from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request
from pathlib import Path


def read_log(path: str) -> str:
    if not path:
        return ""
    log_path = Path(path)
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8", errors="replace")


def pytest_summary(output: str) -> str:
    patterns = [
        r"=+ (?P<summary>.+? in [0-9.]+s) =+",
        r"=+ (?P<summary>.+?) =+",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, output)
        if matches:
            return matches[-1].strip()
    return "No pytest summary found"


def failed_tests(output: str, limit: int = 8) -> list[str]:
    failures: list[str] = []
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith(("FAILED ", "ERROR ")):
            failures.append(stripped)
        if len(failures) >= limit:
            break
    return failures


def build_message() -> str:
    status = os.getenv("TELEGRAM_TEST_STATUS", "unknown")
    workflow = os.getenv("TELEGRAM_WORKFLOW", "QA Tests")
    branch = os.getenv("TELEGRAM_BRANCH", "unknown")
    event = os.getenv("TELEGRAM_EVENT", "unknown")
    run_url = os.getenv("TELEGRAM_RUN_URL", "")
    log = read_log(os.getenv("PYTEST_LOG_PATH", "pytest-output.log"))

    status_icon = "OK" if status == "success" else "FAILED"
    lines = [
        f"Flexobo QA: {status_icon}",
        f"Workflow: {workflow}",
        f"Branch: {branch}",
        f"Event: {event}",
        f"Summary: {pytest_summary(log)}",
    ]

    failures = failed_tests(log)
    if failures:
        lines.append("")
        lines.append("Failed tests:")
        lines.extend(f"- {failure}" for failure in failures)

    allure_url = os.getenv("ALLURE_REPORT_URL", "")
    if allure_url:
        lines.append("")
        lines.append(f"Allure Report: {allure_url}")

    if run_url:
        lines.append(f"GitHub Run: {run_url}")

    message = "\n".join(lines)
    return message[:3900]


def send_message(token: str, chat_id: str, text: str) -> None:
    data = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=data,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        response.read()


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram notification skipped: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID missing.")
        return 0

    send_message(token=token, chat_id=chat_id, text=build_message())
    print("Telegram notification sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
