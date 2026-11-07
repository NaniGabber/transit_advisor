import json
import subprocess
import sys
from pathlib import Path
from typing import Any

BASE_DIR: Path = Path.cwd()
RESULT_PATH: Path = BASE_DIR / "tests" / "result.json"
TESTING_MD_PATH: Path = BASE_DIR / "docs" / "TESTING.md"


def run_pytest() -> int:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = [
        sys.executable,
        "-m",
        "pytest",
        "--cov=src",
        f"--cov-report=json:{RESULT_PATH}",
        "--cov-report=term-missing",
        "-q",
    ]

    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    return result.returncode


def load_report(path: Path) -> dict[str, Any]:
    text: str = path.read_text(encoding="utf-8")
    data: Any = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("result.json must contain an object")
    return data


def build_files_table(files: dict[str, Any]) -> str:
    rows: list[str] = []
    for file_path in sorted(files.keys()):
        info: Any = files[file_path]
        if not isinstance(info, dict):
            continue
        summary: Any = info.get("summary", {})
        if not isinstance(summary, dict):
            summary = {}

        stmts: int = int(summary.get("num_statements", 0))
        miss: int = int(summary.get("missing_lines", 0))
        cover: str = str(summary.get("percent_covered_display", "0"))
        rows.append(f"| `{file_path}` | {stmts} | {miss} | {cover}% |")

    if not rows:
        return "_No data._"
    return "\n".join(rows)


def build_uncovered_section(files: dict[str, Any]) -> str:
    lines: list[str] = []
    for file_path in sorted(files.keys()):
        info: Any = files[file_path]
        if not isinstance(info, dict):
            continue
        missing: Any = info.get("missing_lines", [])
        if isinstance(missing, list) and len(missing) > 0:
            nums: list[str] = [str(n) for n in missing]
            lines.append(f"- `{file_path}`: {', '.join(nums)}")

    if not lines:
        return "_All lines are covered._"
    return "\n".join(lines)


def main() -> int:
    exit_code: int = run_pytest()

    if not RESULT_PATH.exists():
        print(
            f"{RESULT_PATH} was not found. Install pytest-cov?",
            file=sys.stderr,
        )
        return 1

    report: dict[str, Any] = load_report(RESULT_PATH)

    # coverage.py JSON: totals/files на верхньому рівні
    totals: Any = report.get("totals", {})
    if not isinstance(totals, dict):
        totals = {}

    files: Any = report.get("files", {})
    if not isinstance(files, dict):
        files = {}

    percent: str = str(totals.get("percent_covered_display", "0"))
    num_statements: int = int(totals.get("num_statements", 0))
    covered_lines: int = int(totals.get("covered_lines", 0))
    missing_lines: int = int(totals.get("missing_lines", 0))
    excluded_lines: int = int(totals.get("excluded_lines", 0))

    status: str = "PASSED" if exit_code == 0 else f"FAILED (exit code: {exit_code})"

    files_table: str = build_files_table(files)
    uncovered: str = build_uncovered_section(files)

    content: str = f"""# Testing Report

## Result

{status}

## Coverage Overview

- **Total coverage:** {percent}%
- **Statements:** {num_statements}
- **Covered lines:** {covered_lines}
- **Missing lines:** {missing_lines}
- **Excluded lines:** {excluded_lines}

## Coverage by File

| File | Statements | Missing | Coverage |
|------|-----------:|--------:|---------:|
{files_table}

## Uncovered Lines

{uncovered}

## Environment

Generated automatically from pytest + pytest-cov results.
Raw report: `tests/result.json`
"""

    TESTING_MD_PATH.write_text(content, encoding="utf-8")
    print(f"OK, report saved to: {TESTING_MD_PATH}")
    print(f"Raw JSON: {RESULT_PATH}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
