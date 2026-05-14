from __future__ import annotations

import json
import sys
from pathlib import Path

RANK_3 = {"low": 0, "medium": 1, "high": 2}
DEFAULT_MONOTONIC_DIMS = [
    "objective_count",
    "decision_density",
    "ambiguity",
    "verification_difficulty",
]
CODING_PROMPT_REQUIRED_HEADERS = [
    "## Function Contract",
    "## Input Schema",
    "## Output Schema",
    "## Metric Definitions",
    "## Edge Cases",
    "## Constraints",
    "## Acceptance Criteria",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def complexity_score(exercise: dict) -> float:
    profile = exercise.get("complexity_profile", {})
    values = [RANK_3.get(str(profile.get(dim, "")).lower(), 0) for dim in DEFAULT_MONOTONIC_DIMS]
    return sum(values) / max(len(values), 1)


def group_by_level(exercises: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for ex in exercises:
        grouped.setdefault(str(ex.get("level_id")), []).append(ex)
    return grouped


def build_level_lookup(level_map: dict) -> dict[str, dict]:
    levels = level_map.get("levels", []) if isinstance(level_map, dict) else []
    if not isinstance(levels, list):
        return {}
    return {
        level.get("id"): level
        for level in levels
        if isinstance(level, dict) and isinstance(level.get("id"), str)
    }


def actual_mode_mix(exercises: list[dict]) -> dict[str, float]:
    total = len(exercises)
    if total == 0:
        return {}
    counts: dict[str, int] = {}
    for ex in exercises:
        track = str(ex.get("track", ex.get("mode", "unknown"))).strip().lower()
        counts[track] = counts.get(track, 0) + 1
    return {k: v / total for k, v in counts.items()}


def level_difficulty_score(level: dict) -> float:
    profile = level.get("complexity_profile", {}) if isinstance(level, dict) else {}
    values = [RANK_3.get(str(profile.get(dim, "")).lower(), 0) for dim in DEFAULT_MONOTONIC_DIMS]
    return sum(values) / max(len(values), 1)


def build_dynamic_total_quota(
    active_levels: list[str],
    level_lookup: dict[str, dict],
    min_total: int,
    max_total: int,
) -> dict[str, int]:
    if not active_levels:
        return {}
    if min_total > max_total:
        min_total, max_total = max_total, min_total
    scored = [(level_id, level_difficulty_score(level_lookup.get(level_id, {}))) for level_id in active_levels]
    scored.sort(key=lambda item: item[1], reverse=True)
    if len(scored) == 1:
        return {scored[0][0]: max_total}
    span = max_total - min_total
    result: dict[str, int] = {}
    for idx, (level_id, _) in enumerate(scored):
        ratio = (len(scored) - 1 - idx) / (len(scored) - 1)
        result[level_id] = int(round(min_total + span * ratio))
    return result


def validate_required_files(workspace: Path) -> None:
    required = [
        workspace / "analysis" / "current" / "cv_profile.json",
        workspace / "analysis" / "current" / "market_demand.json",
        workspace / "analysis" / "current" / "gap_analysis.json",
        workspace / "analysis" / "current" / "level_map.json",
        workspace / "analysis" / "current" / "exercise_mode_decision.json",
        workspace / "planning" / "learning_plan.json",
        workspace / "planning" / "exercise_catalog.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    require(not missing, f"Missing required generation files: {', '.join(missing)}")


def validate_level_quota(exercises: list[dict], active_levels: list[str], mode_decision: dict, level_lookup: dict[str, dict]) -> None:
    quota = mode_decision.get("level_quota", {}) if isinstance(mode_decision, dict) else {}
    if not isinstance(quota, dict):
        quota = {}
    if not bool(quota.get("enforce", True)):
        return
    has_legacy_split = "core_per_level" in quota or "challenge_per_level" in quota
    core_required = int(quota.get("core_per_level", 3))
    challenge_required = int(quota.get("challenge_per_level", 2))
    min_total = int(quota.get("min_total_per_level", 2))
    max_total = int(quota.get("max_total_per_level", 5))
    dynamic_quota = {} if has_legacy_split else build_dynamic_total_quota(active_levels, level_lookup, min_total, max_total)
    grouped = group_by_level(exercises)
    errors: list[str] = []
    for level_id in active_levels:
        items = grouped.get(level_id, [])
        if has_legacy_split:
            core = [x for x in items if not bool(x.get("is_challenge"))]
            challenge = [x for x in items if bool(x.get("is_challenge"))]
            if len(core) != core_required or len(challenge) != challenge_required:
                errors.append(
                    f"{level_id}: core={len(core)}/{core_required}, challenge={len(challenge)}/{challenge_required}"
                )
            continue

        expected = dynamic_quota.get(level_id, min_total)
        if len(items) != expected:
            errors.append(f"{level_id}: total={len(items)}/{expected}")
    require(not errors, "Level quota mismatch: " + " | ".join(errors))


def validate_challenge_strength(exercises: list[dict], active_levels: list[str]) -> None:
    grouped = group_by_level(exercises)
    errors: list[str] = []
    for level_id in active_levels:
        items = grouped.get(level_id, [])
        core = [x for x in items if not bool(x.get("is_challenge"))]
        challenge = [x for x in items if bool(x.get("is_challenge"))]
        if not core or not challenge:
            continue
        core_avg = sum(complexity_score(x) for x in core) / len(core)
        for ex in challenge:
            if complexity_score(ex) <= core_avg:
                errors.append(
                    f"{level_id}/{ex.get('id')}: challenge score {complexity_score(ex):.2f} <= core avg {core_avg:.2f}"
                )
    require(not errors, "Challenge difficulty not above core baseline: " + " | ".join(errors))


def validate_progression(exercises: list[dict], level_order: list[str]) -> None:
    grouped = group_by_level(exercises)
    previous: float | None = None
    for level_id in level_order:
        items = grouped.get(level_id, [])
        if not items:
            continue
        avg = sum(complexity_score(x) for x in items) / len(items)
        if previous is not None:
            require(
                avg + 0.01 >= previous,
                f"Non-monotonic complexity progression: level `{level_id}` avg {avg:.2f} < previous {previous:.2f}",
            )
        previous = avg


def validate_mode_mix(exercises: list[dict], mode_decision: dict) -> None:
    target = mode_decision.get("mode_mix", {})
    if not isinstance(target, dict) or not target:
        return
    tolerance = float(mode_decision.get("mode_mix_tolerance", 0.2))
    actual = actual_mode_mix(exercises)
    errors: list[str] = []
    for key, target_value in target.items():
        k = str(key).lower()
        try:
            expected = float(target_value)
        except (TypeError, ValueError):
            continue
        delta = abs(actual.get(k, 0.0) - expected)
        if delta > tolerance:
            errors.append(f"{k}: actual={actual.get(k, 0.0):.2f}, target={expected:.2f}, delta={delta:.2f}")
    require(not errors, "Mode mix deviation too high: " + " | ".join(errors))


def validate_live_coding_policy(exercises: list[dict]) -> None:
    violations = [
        str(ex.get("id"))
        for ex in exercises
        if ex.get("mode") == "interview"
        and ex.get("type") == "live-coding"
        and not bool(ex.get("allow_live_coding_talk_through"))
    ]
    require(
        not violations,
        "Interview live-coding requires explicit opt-in (`allow_live_coding_talk_through=true`): "
        + ", ".join(violations),
    )


def validate_coding_prompt_sections(workspace: Path, exercises: list[dict]) -> None:
    errors: list[str] = []
    for ex in exercises:
        if ex.get("mode") != "coding":
            continue
        prompt_path = workspace / "exercises" / f"level-{ex['level_id']}" / ex["id"] / "prompt.md"
        if not prompt_path.exists():
            errors.append(f"{ex['id']}: missing prompt.md")
            continue
        text = prompt_path.read_text(encoding="utf-8")
        for header in CODING_PROMPT_REQUIRED_HEADERS:
            if header not in text:
                errors.append(f"{ex['id']}: missing `{header}`")
    require(not errors, "Coding prompt section validation failed: " + " | ".join(errors))


def main() -> int:
    if len(sys.argv) >= 2:
        workspace = Path(sys.argv[1]).resolve()
    else:
        workspace = (Path.cwd() / "learning_workspace").resolve()

    validate_required_files(workspace)

    learning_plan = read_json(workspace / "planning" / "learning_plan.json")
    mode_decision = read_json(workspace / "analysis" / "current" / "exercise_mode_decision.json")
    level_map = read_json(workspace / "analysis" / "current" / "level_map.json")
    level_lookup = build_level_lookup(level_map)
    catalog = read_json(workspace / "planning" / "exercise_catalog.json")
    exercises = catalog.get("exercises", [])
    require(isinstance(exercises, list) and bool(exercises), "Exercise catalog is empty.")

    active_levels = [x for x in learning_plan.get("active_levels", []) if isinstance(x, str)]
    level_order = [x for x in learning_plan.get("level_order", []) if isinstance(x, str)]
    require(bool(active_levels), "learning_plan.active_levels is empty.")

    validate_live_coding_policy(exercises)
    validate_level_quota(exercises, active_levels, mode_decision, level_lookup)
    validate_challenge_strength(exercises, active_levels)
    validate_progression(exercises, level_order)
    validate_mode_mix(exercises, mode_decision)
    validate_coding_prompt_sections(workspace, exercises)

    print(f"Generation validation passed for {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
