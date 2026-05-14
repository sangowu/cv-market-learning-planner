from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_MIX = ["foundation", "project_takeover", "interview"]


def read_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else dict(default)


def task_source(exercise: dict) -> str:
    source = str(exercise.get("source", "plan"))
    category = str(exercise.get("category", ""))
    mode = str(exercise.get("mode", ""))
    if source == "foundation" or category in {"python_basics", "algorithms", "sql_basics", "ai_engineering"}:
        return "foundation"
    if mode == "interview" or category in {"mock_interview", "jd_triage", "project_defense"}:
        return "interview"
    return "project_takeover"


def select_tasks(exercises: list[dict], mode: str) -> list[dict]:
    required_count = 1 if mode == "low-pressure" else 2
    optional_count = 1
    selected: list[dict] = []
    used_ids: set[str] = set()
    for wanted in DEFAULT_MIX:
        for exercise in exercises:
            if exercise.get("id") in used_ids:
                continue
            if task_source(exercise) == wanted:
                selected.append(exercise)
                used_ids.add(str(exercise.get("id")))
                break
        if len(selected) >= required_count + optional_count:
            break
    for exercise in exercises:
        if len(selected) >= required_count + optional_count:
            break
        if exercise.get("id") not in used_ids:
            selected.append(exercise)
            used_ids.add(str(exercise.get("id")))
    tasks = []
    today = date.today().isoformat()
    for idx, exercise in enumerate(selected, start=1):
        role = "required" if idx <= required_count else "optional"
        tasks.append(
            {
                "daily_task_id": f"{today}-{idx:03d}",
                "exercise_id": exercise.get("id"),
                "source": task_source(exercise),
                "daily_role": role,
                "status": "pending",
                "title": exercise.get("title", exercise.get("id")),
                "estimated_minutes": exercise.get("estimated_minutes", 20),
            }
        )
    return tasks


def main() -> int:
    workspace = Path(sys.argv[1]).resolve() if len(sys.argv) >= 2 else (Path.cwd() / "learning_workspace").resolve()
    mode = sys.argv[2] if len(sys.argv) >= 3 else "low-pressure"
    catalog = read_json(workspace / "planning" / "exercise_catalog.json", {"exercises": []})
    exercises = catalog.get("exercises", []) if isinstance(catalog.get("exercises"), list) else []
    daily_dir = workspace / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    current_path = daily_dir / "current.json"
    current = read_json(current_path, {"date": None, "status": "not_generated", "tasks": []})
    if current.get("date") == today and current.get("tasks"):
        print(f"Daily tasks already exist for {today}")
        return 0
    payload = {
        "date": today,
        "status": "pending",
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "missed_day_policy": "do-not-accumulate-debt",
        "tasks": select_tasks(exercises, mode),
    }
    current_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Generated {len(payload['tasks'])} daily tasks for {today}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
