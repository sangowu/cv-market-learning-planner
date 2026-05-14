from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def main() -> int:
    workspace = Path(sys.argv[1]).resolve() if len(sys.argv) >= 2 else (Path.cwd() / "learning_workspace").resolve()
    daily_dir = workspace / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    current_path = daily_dir / "current.json"
    current = read_json(current_path, {"date": None, "status": "not_generated", "tasks": []})
    today = date.today().isoformat()
    if current.get("date") != today:
        print(json.dumps({"date": today, "status": "not_generated", "message": "No daily practice has been generated for today."}, ensure_ascii=False))
        return 0
    tasks = current.get("tasks", []) if isinstance(current.get("tasks"), list) else []
    pending = [task for task in tasks if task.get("status") not in {"done", "skipped"}]
    status = "done" if tasks and not pending else current.get("status", "pending")
    print(json.dumps({"date": today, "status": status, "pending_count": len(pending), "tasks": tasks}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
