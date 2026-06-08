#!/usr/bin/env python3
"""
Flexobo QA runner.

Runs the existing pytest + Playwright suite with useful defaults and writes a
small Markdown report that is easy to paste into a bug/QA update.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_ROOT = ROOT / "qa-artifacts"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Flexobo Playwright QA tests.")
    parser.add_argument(
        "targets",
        nargs="*",
        default=["tests"],
        help="Pytest targets, for example tests/test_login.py or tests/permissions.",
    )
    parser.add_argument("-m", "--mark", help="Pytest marker expression, for example smoke.")
    parser.add_argument("-k", "--keyword", help="Pytest -k expression.")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode.")
    parser.add_argument("--browser", default="chromium", help="Browser name. Default: chromium.")
    parser.add_argument("--reruns", type=int, default=0, help="Retry failed tests N times.")
    parser.add_argument("--timeout", type=int, help="Per-test timeout in seconds. Requires pytest-timeout.")
    parser.add_argument(
        "--trace",
        default="retain-on-failure",
        choices=["on", "off", "retain-on-failure"],
        help="Playwright trace mode.",
    )
    parser.add_argument(
        "--screenshot",
        default="only-on-failure",
        choices=["on", "off", "only-on-failure"],
        help="Playwright screenshot mode.",
    )
    parser.add_argument(
        "--video",
        default="retain-on-failure",
        choices=["on", "off", "retain-on-failure"],
        help="Playwright video mode.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=None,
        help="Where to store run output. Default: qa-artifacts/<timestamp>.",
    )
    parser.add_argument(
        "--extra",
        default="",
        help="Extra raw pytest arguments, for example '--maxfail=1 -s'.",
    )
    return parser.parse_args()


def pytest_command() -> list[str]:
    local = ROOT / ".venv" / "bin" / "pytest"
    if local.exists():
        return [str(local)]
    return [sys.executable, "-m", "pytest"]


def make_artifact_dir(value: str | None) -> Path:
    if value:
        artifact_dir = Path(value).expanduser()
        if not artifact_dir.is_absolute():
            artifact_dir = ROOT / artifact_dir
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        artifact_dir = DEFAULT_ARTIFACT_ROOT / stamp
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def build_command(args: argparse.Namespace, artifact_dir: Path) -> list[str]:
    command = pytest_command()
    command.extend(args.targets)
    command.extend(
        [
            f"--browser={args.browser}",
            f"--tracing={args.trace}",
            f"--screenshot={args.screenshot}",
            f"--video={args.video}",
            f"--alluredir={artifact_dir / 'allure-results'}",
        ]
    )

    if args.timeout:
        command.append(f"--timeout={args.timeout}")
    if args.mark:
        command.extend(["-m", args.mark])
    if args.keyword:
        command.extend(["-k", args.keyword])
    if args.headed:
        command.append("--headed")
    if args.reruns:
        command.append(f"--reruns={args.reruns}")
    if args.extra:
        command.extend(shlex.split(args.extra))

    return command


def summarize_output(output: str) -> dict[str, str]:
    summary_patterns = [
        r"=+ (?P<summary>.+? in [0-9.]+s) =+",
        r"=+ (?P<summary>.+?) =+",
    ]
    for pattern in summary_patterns:
        matches = re.findall(pattern, output)
        if matches:
            return {"pytest_summary": matches[-1].strip()}
    return {"pytest_summary": "No pytest summary found."}


def extract_failures(output: str, limit: int = 12) -> list[str]:
    failures: list[str] = []
    for line in output.splitlines():
        if line.startswith("FAILED "):
            failures.append(line.strip())
        if len(failures) >= limit:
            break
    return failures


def write_report(
    artifact_dir: Path,
    command: list[str],
    exit_code: int,
    output: str,
    started_at: datetime,
    finished_at: datetime,
) -> Path:
    status = "PASSED" if exit_code == 0 else "FAILED"
    summary = summarize_output(output)
    failures = extract_failures(output)
    log_path = artifact_dir / "pytest.log"
    report_path = artifact_dir / "qa-report.md"

    lines = [
        "# Flexobo QA Report",
        "",
        f"- Status: {status}",
        f"- Exit code: {exit_code}",
        f"- Started: {started_at.isoformat(timespec='seconds')}",
        f"- Finished: {finished_at.isoformat(timespec='seconds')}",
        f"- Duration: {(finished_at - started_at).total_seconds():.1f}s",
        f"- Pytest summary: {summary['pytest_summary']}",
        f"- Command: `{' '.join(shlex.quote(part) for part in command)}`",
        f"- Log: `{log_path}`",
        f"- Allure results: `{artifact_dir / 'allure-results'}`",
        "",
    ]

    if failures:
        lines.append("## Failed Tests")
        lines.append("")
        lines.extend(f"- `{failure}`" for failure in failures)
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Playwright trace/video/screenshot are configured by this runner.",
            "- Allure failure screenshots from `plugins.allure_plugin` are still attached.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    args = parse_args()
    artifact_dir = make_artifact_dir(args.artifacts_dir)
    command = build_command(args, artifact_dir)

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    started_at = datetime.now()
    process = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    finished_at = datetime.now()

    output = process.stdout
    log_path = artifact_dir / "pytest.log"
    log_path.write_text(output, encoding="utf-8")
    report_path = write_report(
        artifact_dir=artifact_dir,
        command=command,
        exit_code=process.returncode,
        output=output,
        started_at=started_at,
        finished_at=finished_at,
    )

    print(output)
    print(f"\nQA report: {report_path}")
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
