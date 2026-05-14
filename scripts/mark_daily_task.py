from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_STATUS = {"pending", "in_progress", "submitted", "reviewed", "done", "skipped", "missed", "retry"}


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def main() -> int:
    if len(sys.argv) < 4:
        print("Usage: python mark_daily_task.py <workspace_dir> <exercise_id_or_daily_task_id> <status> [note]")
        return 1
    workspace = Path(sys.argv[1]).resolve()
    target = sys.argv[2]
    status = sys.argv[3]
    note = sys.argv[4] if len(sys.argv) >= 5 else ""
    if status not in VALID_STATUS:
        print(f"Invalid status `{status}`. Use one of: {', '.join(sorted(VALID_STATUS))}")
        return 1
    current_path = workspace / "daily" / "current.json"
    current = read_json(current_path, {"date": None, "status": "not_generated", "tasks": []})
    tasks = current.get("tasks", []) if isinstance(current.get("tasks"), list) else []
    matched = False
    for task in tasks:
        if target in {task.get("daily_task_id"), task.get("exercise_id")}:
            task["status"] = status
            task["updated_at"] = datetime.now(timezone.utc).isoformat()
            if note:
                task["note"] = note
            matched = True
            break
    if not matched:
        print(f"No daily task matched `{target}`")
        return 1
    if tasks and all(task.get("status") in {"done", "skipped"} for task in tasks):
        current["status"] = "done"
    elif any(task.get("status") == "done" for task in tasks):
        current["status"] = "partial"
    else:
        current["status"] = "pending"
    current_path.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")
    history = workspace / "daily" / "history.jsonl"
    history.parent.mkdir(parents=True, exist_ok=True)
    history.write_text(history.read_text(encoding="utf-8") + json.dumps({"target": target, "status": status, "note": note, "timestamp": datetime.now(timezone.utc).isoformat()}, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Marked {target} as {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
