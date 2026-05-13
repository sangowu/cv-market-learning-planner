from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from workspace_model import default_progress_map, default_stats, read_json, utc_now, write_json


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def parse_json_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("["):
        data = json.loads(raw)
        return [str(item) for item in data]
    return [item.strip() for item in raw.split(",") if item.strip()]


def ensure_progress_map(path: Path, catalog: dict) -> dict:
    if path.exists():
        progress_map = read_json(path)
    else:
        progress_map = default_progress_map()

    progress_map.setdefault("levels", {})
    progress_map.setdefault("exercises", {})
    for exercise in catalog.get("exercises", []):
        level_state = progress_map["levels"].setdefault(
            exercise["level_id"],
            {
                "status": "pending",
                "exercise_ids": [],
                "completed_exercises": [],
                "last_reviewed_at": None,
            },
        )
        if exercise["id"] not in level_state["exercise_ids"]:
            level_state["exercise_ids"].append(exercise["id"])
        progress_map["exercises"].setdefault(
            exercise["id"],
            {
                "level_id": exercise["level_id"],
                "mode": exercise.get("mode", "coding"),
                "status": "pending",
                "submission_count": 0,
                "review_count": 0,
                "last_submission": None,
                "last_review": None,
            },
        )
    return progress_map


def write_progress_md(path: Path, latest_review: dict | None, level_summaries: list[str], completed: int, issue_tags: list[str]) -> None:
    latest_line = "pending"
    if latest_review:
        latest_line = (
            f"{latest_review['timestamp']}: `{latest_review['exercise_id']}` -> "
            f"{latest_review['status']} ({latest_review['next_action']})"
        )
    focus_lines = "\n".join(f"- {tag}" for tag in issue_tags) or "- none"
    level_lines = "\n".join(f"- {line}" for line in level_summaries) or "- pending"
    content = (
        "# Progress\n\n"
        "## Current Focus\n"
        f"{focus_lines}\n\n"
        "## Latest Review\n"
        f"- {latest_line}\n\n"
        "## Level Status\n"
        f"{level_lines}\n\n"
        "## Completed\n"
        f"- {completed} exercise(s)\n"
    )
    path.write_text(content, encoding="utf-8")


def main() -> int:
    if len(sys.argv) < 10:
        print(
            "Usage: python update_progress.py <workspace_dir> <exercise_id> <submission_path> <status> <next_action> <score_or_dash> <issue_tags> <strengths> <issues> [recommended_regeneration_mode] [notes]"
        )
        return 1

    workspace = Path(sys.argv[1]).resolve()
    exercise_id = sys.argv[2]
    submission_path = sys.argv[3]
    status = sys.argv[4]
    next_action = sys.argv[5]
    score_raw = sys.argv[6]
    issue_tags = parse_json_list(sys.argv[7])
    strengths = parse_json_list(sys.argv[8])
    issues = parse_json_list(sys.argv[9])
    regeneration_mode = sys.argv[10] if len(sys.argv) > 10 else "targeted-refresh"
    notes = sys.argv[11] if len(sys.argv) > 11 else ""

    planning_dir = workspace / "planning"
    progress_dir = workspace / "progress"
    catalog_path = planning_dir / "exercise_catalog.json"
    progress_map_path = planning_dir / "progress_map.json"
    submissions_path = progress_dir / "submissions.jsonl"
    reviews_path = progress_dir / "reviews.jsonl"
    stats_path = progress_dir / "stats.json"
    progress_md_path = progress_dir / "progress.md"

    catalog = read_json(catalog_path) if catalog_path.exists() else {"exercises": []}
    exercise_lookup = {exercise["id"]: exercise for exercise in catalog.get("exercises", [])}
    if exercise_id not in exercise_lookup:
        print(f"Exercise `{exercise_id}` not found in {catalog_path}")
        return 2

    submission_record = {
        "timestamp": utc_now(),
        "exercise_id": exercise_id,
        "submission_path": submission_path,
        "notes": notes,
    }
    append_jsonl(submissions_path, submission_record)

    score = None if score_raw == "-" else float(score_raw)
    review_record = {
        "timestamp": utc_now(),
        "exercise_id": exercise_id,
        "status": status,
        "score": score,
        "strengths": strengths,
        "issues": issues,
        "issue_tags": issue_tags,
        "next_action": next_action,
        "recommended_regeneration_mode": regeneration_mode,
    }
    append_jsonl(reviews_path, review_record)

    progress_map = ensure_progress_map(progress_map_path, catalog)
    exercise_state = progress_map["exercises"][exercise_id]
    exercise_state["status"] = status
    exercise_state["submission_count"] += 1
    exercise_state["review_count"] += 1
    exercise_state["last_submission"] = submission_record["timestamp"]
    exercise_state["last_review"] = review_record["timestamp"]

    level_id = exercise_state["level_id"]
    level_state = progress_map["levels"][level_id]
    level_state["last_reviewed_at"] = review_record["timestamp"]
    if status in {"completed", "advance"} and exercise_id not in level_state["completed_exercises"]:
        level_state["completed_exercises"].append(exercise_id)
    if status == "blocked":
        level_state["status"] = "blocked"
    elif len(level_state["completed_exercises"]) == len(level_state["exercise_ids"]) and level_state["exercise_ids"]:
        level_state["status"] = "completed"
    else:
        level_state["status"] = "active"

    write_json(progress_map_path, progress_map)

    submission_rows = load_jsonl(submissions_path)
    review_rows = load_jsonl(reviews_path)
    tag_counter = Counter(tag for row in review_rows for tag in row.get("issue_tags", []))
    latest_by_exercise: dict[str, dict] = {}
    for row in review_rows:
        latest_by_exercise[row["exercise_id"]] = row
    completed = sum(
        1 for row in latest_by_exercise.values() if row.get("status") in {"completed", "advance"}
    )
    stats = default_stats()
    stats.update(
        {
            "total_submissions": len(submission_rows),
            "total_reviews": len(review_rows),
            "completed_exercises": completed,
            "latest_exercise": exercise_id,
            "last_review_status": status,
            "common_issue_tags": [tag for tag, _ in tag_counter.most_common(5)],
        }
    )
    write_json(stats_path, stats)

    level_summaries = []
    for current_level_id, level_state in progress_map["levels"].items():
        level_summaries.append(
            f"{current_level_id}: {level_state['status']} ({len(level_state['completed_exercises'])}/{len(level_state['exercise_ids'])} complete)"
        )
    write_progress_md(progress_md_path, review_record, level_summaries, completed, stats["common_issue_tags"])

    print(f"Updated progress for {exercise_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
