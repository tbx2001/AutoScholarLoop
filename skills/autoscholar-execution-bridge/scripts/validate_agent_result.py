from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"completed", "blocked", "failed"}
VALID_CLAIM_SUPPORT = {"real_result", "smoke_result", "scaffold_only", "blocked"}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_agent_result.py path/to/task.json", file=sys.stderr)
        return 2
    task_path = Path(sys.argv[1])
    task = _read_json(task_path)
    workspace = Path(task["workspace"])
    result_path = task_path.parent / "agent_result.json"
    if not result_path.exists():
        print(f"missing result file: {result_path}", file=sys.stderr)
        return 1
    result = _read_json(result_path)
    errors = _validate_result(task, result, workspace)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("agent_result.json is valid")
    return 0


def _validate_result(task: dict[str, Any], result: dict[str, Any], workspace: Path) -> list[str]:
    errors: list[str] = []
    if result.get("schema") != "autoscholarloop.agent_result.v1":
        errors.append("schema must be autoscholarloop.agent_result.v1")
    if result.get("status") not in VALID_STATUSES:
        errors.append(f"status must be one of {sorted(VALID_STATUSES)}")
    if result.get("claim_support") not in VALID_CLAIM_SUPPORT:
        errors.append(f"claim_support must be one of {sorted(VALID_CLAIM_SUPPORT)}")
    allowed_roots = [str(item).replace("\\", "/").strip("/") for item in task.get("allowed_write_roots", [])]
    for key in ["changed_files", "evidence_files"]:
        value = result.get(key)
        if not isinstance(value, list):
            errors.append(f"{key} must be a list")
            continue
        for relpath in value:
            if not isinstance(relpath, str):
                errors.append(f"{key} entries must be strings")
                continue
            if not _is_allowed_relative_path(relpath, allowed_roots):
                errors.append(f"{key} entry is outside allowed roots: {relpath}")
            full_path = workspace / relpath
            if key == "evidence_files" and result.get("status") == "completed" and not full_path.exists():
                errors.append(f"evidence file does not exist: {relpath}")
    if result.get("status") == "completed" and not result.get("changed_files"):
        errors.append("completed result must list changed_files")
    if result.get("claim_support") == "real_result" and not result.get("evidence_files"):
        errors.append("real_result requires at least one evidence file")
    return errors


def _is_allowed_relative_path(path: str, allowed_roots: list[str]) -> bool:
    normalized = path.replace("\\", "/").strip("/")
    parts = Path(normalized).parts
    if not normalized or Path(normalized).is_absolute() or ".." in parts:
        return False
    return any(normalized == root or normalized.startswith(f"{root}/") for root in allowed_roots)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    raise SystemExit(main())
