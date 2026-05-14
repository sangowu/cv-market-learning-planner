from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from workspace_model import ABSTRACT_LEVELS, write_json

STARTER_BY_TYPE = {
    "python": "def solve() -> object:\n    raise NotImplementedError('Implement the exercise here.')\n",
    "fastapi": "from fastapi import FastAPI\n\napp = FastAPI()\n\n\n@app.get('/health')\ndef health() -> dict[str, str]:\n    return {'status': 'ok'}\n",
    "sql": "-- Write your SQL solution here.\n",
    "debugging": "def investigate() -> str:\n    raise NotImplementedError('Document or implement the fix here.')\n",
    "llm-systems": "def run_pipeline() -> dict:\n    raise NotImplementedError('Implement the pipeline here.')\n",
    "live-coding": "def solve() -> object:\n    raise NotImplementedError('Implement the interview exercise here.')\n",
    "debugging-interview": "# Debugging interview notes\n\n## Root cause\n\n## Fix plan\n\n## Verification\n",
    "system-design": "# System design notes\n\n## Requirements\n\n## Architecture\n\n## Trade-offs\n",
    "project-defense": "# Project defense notes\n\n## Core answer\n\n## Evidence\n\n## Risks\n",
    "cv-challenge": "# CV challenge notes\n\n## Main answer\n\n## Evidence\n\n## Stronger version\n",
    "behavioral": "# Behavioral notes\n\n## Situation\n\n## Task\n\n## Action\n\n## Result\n",
}


TEST_BY_TYPE = {
    "python": "def test_placeholder() -> None:\n    assert True\n",
    "fastapi": "def test_placeholder() -> None:\n    assert True\n",
    "sql": "def test_placeholder() -> None:\n    assert True\n",
    "debugging": "def test_placeholder() -> None:\n    assert True\n",
    "llm-systems": "def test_placeholder() -> None:\n    assert True\n",
    "live-coding": "def test_placeholder() -> None:\n    assert True\n",
}


DEFAULT_SUPPORT_BY_LEVEL = {
    level["id"]: level["default_support_level"] for level in ABSTRACT_LEVELS
}

DEFAULT_COMPLEXITY_BY_LEVEL = {
    level["id"]: level["complexity_profile"] for level in ABSTRACT_LEVELS
}

COMPLEXITY_CONSTRAINTS_BY_LEVEL = {
    level["id"]: level["complexity_constraints"] for level in ABSTRACT_LEVELS
}

DEFAULT_PREREQ_SUPPORT_BY_LEVEL = {
    "foundation-gaps": "teach",
    "independent-implementation": "remind",
    "system-rigor": "remind",
    "interview-readiness": "assume",
}

RANK_3 = {"low": 0, "medium": 1, "high": 2}
DIFFICULTY_DIMS = [
    "objective_count",
    "decision_density",
    "ambiguity",
    "verification_difficulty",
]


def normalize_language_name(value: str) -> str:
    return value.strip().lower().replace("_", "-")


def extract_cv_language_evidence(cv_profile: dict) -> list[str]:
    candidates: list[str] = []
    structured_sources = [
        cv_profile.get("language_evidence"),
        cv_profile.get("languages"),
        cv_profile.get("skills", {}).get("languages") if isinstance(cv_profile.get("skills"), dict) else None,
    ]
    for source in structured_sources:
        if isinstance(source, list):
            for item in source:
                if isinstance(item, str):
                    candidates.append(item)
                elif isinstance(item, dict):
                    label = item.get("language") or item.get("name") or item.get("id")
                    if isinstance(label, str):
                        candidates.append(label)
    seen = set()
    normalized = []
    for item in candidates:
        key = normalize_language_name(item)
        if key and key not in seen:
            seen.add(key)
            normalized.append(key)
    return normalized


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate_level_fit(exercise: dict) -> None:
    level_id = exercise["level_id"]
    constraints = COMPLEXITY_CONSTRAINTS_BY_LEVEL.get(level_id)
    if not constraints:
        raise ValueError(f"Unknown level_id `{level_id}` for exercise `{exercise['id']}`")
    if not isinstance(constraints, dict):
        raise ValueError(f"Invalid complexity constraints for level `{level_id}`")

    profile = exercise.get("complexity_profile", {})
    missing = [key for key in constraints if key not in profile]
    if missing:
        raise ValueError(
            f"Exercise `{exercise['id']}` is missing complexity_profile keys for level-fit validation: {', '.join(missing)}"
        )

    mismatches = []
    for key, allowed_values in constraints.items():
        value = profile.get(key)
        if value not in allowed_values:
            mismatches.append(f"{key}={value!r} not in {allowed_values}")

    if mismatches:
        raise ValueError(
            f"Exercise `{exercise['id']}` does not fit level `{level_id}`: " + "; ".join(mismatches)
        )


def validate_coding_responsibility(exercise: dict) -> None:
    if exercise.get("mode") != "coding":
        return

    is_test_design_exercise = bool(exercise.get("is_test_design_exercise"))
    if exercise.get("user_responsibility") == "implementation-only" and not is_test_design_exercise:
        lower_deliverables = [item.lower() for item in exercise.get("deliverables", []) if isinstance(item, str)]
        lower_verification = str(exercise.get("verification", "")).lower()
        banned_tokens = [
            "write test",
            "design test",
            "add test",
            "expand test",
            "pytest case",
            "unit test",
            "new test",
            "more test",
        ]
        for item in lower_deliverables:
            if any(token in item for token in banned_tokens):
                raise ValueError(
                    f"Exercise `{exercise['id']}` violates implementation-only responsibility via deliverable `{item}`"
                )
        if any(token in lower_verification for token in banned_tokens):
            raise ValueError(
                f"Exercise `{exercise['id']}` violates implementation-only responsibility via verification instructions."
            )

    if not is_test_design_exercise and exercise.get("test_strategy") != "system-generated-visible":
        raise ValueError(
            f"Exercise `{exercise['id']}` must use `system-generated-visible` test_strategy for normal coding exercises."
        )

    if not is_test_design_exercise and exercise.get("test_edit_policy") != "do-not-edit":
        raise ValueError(
            f"Exercise `{exercise['id']}` must use `do-not-edit` test_edit_policy for normal coding exercises."
        )



def validate_foundation_language(exercise: dict, cv_language_evidence: list[str]) -> None:
    if exercise.get("level_id") != "foundation-gaps" or exercise.get("mode") != "coding":
        return
    language_focus = normalize_language_name(str(exercise.get("language_focus", "")))
    if not language_focus:
        raise ValueError(
            f"Exercise `{exercise['id']}` in level `foundation-gaps` must define `language_focus`."
        )
    if cv_language_evidence and language_focus not in cv_language_evidence:
        top_candidates = ", ".join(cv_language_evidence[:3])
        raise ValueError(
            f"Exercise `{exercise['id']}` language_focus `{exercise.get('language_focus')}` is not aligned with CV language evidence. "
            f"Top CV evidence languages: {top_candidates}"
        )


def validate_leetcode_style(exercise: dict) -> None:
    if exercise.get("mode") != "coding" or exercise.get("style") != "leetcode":
        return
    required = ["title", "problem", "function_signature", "starter_code"]
    missing = [field for field in required if not str(exercise.get(field, "")).strip()]
    if missing:
        raise ValueError(
            f"Exercise `{exercise['id']}` is missing LeetCode-style fields: {', '.join(missing)}"
        )
    for field in ["topics", "examples", "constraints", "tests", "hints"]:
        value = exercise.get(field)
        if value is None:
            exercise[field] = []
            continue
        if not isinstance(value, list):
            raise ValueError(f"Exercise `{exercise['id']}` field `{field}` must be a list.")
    expected_complexity = exercise.get("expected_complexity", {})
    if expected_complexity and not isinstance(expected_complexity, dict):
        raise ValueError(f"Exercise `{exercise['id']}` field `expected_complexity` must be an object.")


def validate_live_coding_policy(exercise: dict) -> None:
    if exercise.get("mode") == "interview" and exercise.get("type") == "live-coding":
        if not bool(exercise.get("allow_live_coding_talk_through")):
            raise ValueError(
                f"Exercise `{exercise['id']}` uses interview `live-coding` type without explicit opt-in. "
                "Set `allow_live_coding_talk_through=true` if intentionally required."
            )


def load_mode_decision(workspace: Path) -> dict | None:
    path = workspace / "analysis" / "current" / "exercise_mode_decision.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def load_active_levels(workspace: Path) -> list[str]:
    plan_path = workspace / "planning" / "learning_plan.json"
    if not plan_path.exists():
        return []
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return []
    active = payload.get("active_levels")
    if not isinstance(active, list):
        return []
    return [item for item in active if isinstance(item, str)]


def load_level_map_lookup(workspace: Path) -> dict[str, dict]:
    path = workspace / "analysis" / "current" / "level_map.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {}
    levels = payload.get("levels")
    if not isinstance(levels, list):
        return {}
    return {
        level.get("id"): level
        for level in levels
        if isinstance(level, dict) and isinstance(level.get("id"), str)
    }


def level_difficulty_score(level: dict) -> float:
    profile = level.get("complexity_profile", {})
    if not isinstance(profile, dict):
        return 0.0
    values = [RANK_3.get(str(profile.get(dim, "")).lower(), 0) for dim in DIFFICULTY_DIMS]
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
    scored = []
    for level_id in active_levels:
        scored.append((level_id, level_difficulty_score(level_lookup.get(level_id, {}))))
    scored.sort(key=lambda item: item[1], reverse=True)
    if len(scored) == 1:
        return {scored[0][0]: max_total}

    span = max_total - min_total
    quotas: dict[str, int] = {}
    for idx, (level_id, _) in enumerate(scored):
        ratio = (len(scored) - 1 - idx) / (len(scored) - 1)
        quotas[level_id] = int(round(min_total + span * ratio))
    return quotas


def validate_mode_decision_alignment(exercises: list[dict], mode_decision: dict) -> None:
    include_coding = mode_decision.get("include_coding")
    include_debugging = mode_decision.get("include_debugging")

    coding_count = sum(1 for ex in exercises if ex.get("mode") == "coding")
    debugging_count = sum(
        1 for ex in exercises
        if str(ex.get("track", "")).lower() == "debugging" or str(ex.get("type", "")).lower() == "debugging"
    )

    if include_coding is True and coding_count == 0:
        raise ValueError("Mode decision requires coding exercises, but none were generated.")
    if include_coding is False and coding_count > 0:
        raise ValueError("Mode decision disables coding exercises, but coding exercises were generated.")

    if include_debugging is True and debugging_count == 0:
        raise ValueError("Mode decision requires debugging exercises, but none were generated.")
    if include_debugging is False and debugging_count > 0:
        raise ValueError("Mode decision disables debugging exercises, but debugging exercises were generated.")


def validate_level_quota(
    exercises: list[dict],
    active_levels: list[str],
    mode_decision: dict | None,
    level_lookup: dict[str, dict],
) -> None:
    if not active_levels or mode_decision is None:
        return

    quota = mode_decision.get("level_quota")
    if not isinstance(quota, dict):
        quota = {}
    has_legacy_split = "core_per_level" in quota or "challenge_per_level" in quota
    core_required = int(quota.get("core_per_level", 3))
    challenge_required = int(quota.get("challenge_per_level", 2))
    min_total = int(quota.get("min_total_per_level", 2))
    max_total = int(quota.get("max_total_per_level", 5))
    dynamic_quota = {} if has_legacy_split else build_dynamic_total_quota(active_levels, level_lookup, min_total, max_total)
    enforce = bool(quota.get("enforce", True))
    if not enforce:
        return

    errors: list[str] = []
    for level_id in active_levels:
        level_items = [ex for ex in exercises if ex.get("level_id") == level_id]
        if has_legacy_split:
            challenge_items = [ex for ex in level_items if bool(ex.get("is_challenge"))]
            core_items = [ex for ex in level_items if not bool(ex.get("is_challenge"))]
            if len(core_items) != core_required or len(challenge_items) != challenge_required:
                errors.append(
                    f"{level_id}: core={len(core_items)} (required {core_required}), "
                    f"challenge={len(challenge_items)} (required {challenge_required})"
                )
            continue

        expected = dynamic_quota.get(level_id, min_total)
        if len(level_items) != expected:
            errors.append(f"{level_id}: total={len(level_items)} (required {expected})")
    if errors:
        raise ValueError("Level quota validation failed: " + " | ".join(errors))


def starter_extension(exercise: dict) -> str:
    if exercise.get("starter_ext"):
        return exercise["starter_ext"]
    if exercise.get("type") == "sql":
        return "sql"
    if exercise.get("mode") == "interview":
        return "md"
    return "py"



def render_lines(items: list[str], fallback: str, prefix: str = "- ") -> str:
    if items:
        return "\n".join(f"{prefix}{item}" for item in items)
    return f"{prefix}{fallback}"


def render_schema_block(value: object, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list) and value:
        return "\n".join(f"- {item}" for item in value if str(item).strip())
    return fallback


def coding_spec_sections(exercise: dict) -> dict:
    return {
        "function_contract": str(
            exercise.get("function_contract")
            or f"{exercise.get('implementation_target', 'starter.py')}: implement the required public function(s)."
        ),
        "input_schema": render_schema_block(
            exercise.get("input_schema"),
            "Use the fields described in the task prompt and validate required keys.",
        ),
        "output_schema": render_schema_block(
            exercise.get("output_schema"),
            "Return a JSON-serializable structure that matches the verification target.",
        ),
        "metric_definitions": render_schema_block(
            exercise.get("metric_definitions"),
            "Use exact-match behavior where applicable and keep calculations deterministic.",
        ),
        "edge_cases": render_lines(
            [str(item) for item in exercise.get("edge_cases", []) if str(item).strip()],
            "Handle empty input safely.",
        ),
        "constraints": render_lines(
            [str(item) for item in exercise.get("constraints", []) if str(item).strip()],
            "Do not use third-party libraries.",
        ),
        "acceptance_criteria": render_lines(
            [str(item) for item in exercise.get("acceptance_criteria", []) if str(item).strip()],
            "All generated tests pass.",
        ),
    }


def render_leetcode_block(exercise: dict) -> str:
    if exercise.get("style") != "leetcode":
        return ""
    topics = ", ".join(str(item) for item in exercise.get("topics", []) if str(item).strip()) or "general"
    examples = exercise.get("examples", [])
    example_lines = []
    for idx, example in enumerate(examples, start=1):
        if isinstance(example, dict):
            example_lines.append(f"Example {idx}:\nInput: {example.get('input', '')}\nOutput: {example.get('output', '')}")
        else:
            example_lines.append(f"Example {idx}: {example}")
    constraints = "\n".join(f"- {item}" for item in exercise.get("constraints", []) if str(item).strip()) or "- none"
    hints = "\n".join(f"- {item}" for item in exercise.get("hints", []) if str(item).strip()) or "- none"
    complexity = exercise.get("expected_complexity", {})
    if isinstance(complexity, dict) and complexity:
        complexity_text = "\n".join(f"- {key}: {value}" for key, value in complexity.items())
    else:
        complexity_text = "- not specified"
    return (
        "LeetCode Style\n"
        f"Difficulty: {exercise.get('difficulty', 'easy')}\n"
        f"Topics: {topics}\n\n"
        "Problem Statement:\n"
        f"{exercise.get('problem', exercise.get('prompt', ''))}\n\n"
        "Examples:\n"
        f"{chr(10).join(example_lines) or 'No examples provided.'}\n\n"
        "Constraints:\n"
        f"{constraints}\n\n"
        "Function Signature:\n"
        f"{exercise.get('function_signature', '')}\n\n"
        "Expected Complexity:\n"
        f"{complexity_text}\n\n"
        "Hints:\n"
        f"{hints}\n\n"
    )


def build_code_header(exercise: dict) -> str:
    deliverables = "\n".join(f"- {item}" for item in exercise.get("deliverables", [])) or "- Complete the task."
    profile_lines = "\n".join(
        f"- {key}: {value}" for key, value in exercise.get("complexity_profile", {}).items()
    ) or "- pending"
    objective_lines = "\n".join(
        f"- {item}" for item in exercise.get("learning_objectives", [])
    ) or "- pending"
    spec = coding_spec_sections(exercise)
    leetcode_block = render_leetcode_block(exercise)
    return (
        '"""\n'
        f"Title: {exercise['title']}\n"
        f"Level: {exercise['level_id']}\n"
        f"Mode: {exercise.get('mode', 'coding')}\n"
        f"Type: {exercise.get('type', 'exercise')}\n"
        f"Source: {exercise.get('source', 'plan')}\n"
        f"Style: {exercise.get('style', 'exercise')}\n"
        f"Support Level: {exercise.get('support_level', '')}\n\n"
        f"Language Focus: {exercise.get('language_focus', '')}\n\n"
        f"Implementation Target: {exercise.get('implementation_target', '')}\n"
        f"User Responsibility: {exercise.get('user_responsibility', '')}\n"
        f"Test Strategy: {exercise.get('test_strategy', '')}\n"
        f"Test Edit Policy: {exercise.get('test_edit_policy', '')}\n\n"
        "Training Goal:\n"
        f"{exercise.get('summary', '')}\n\n"
        "Why This Fits The Level:\n"
        f"{exercise.get('fit_rationale', '')}\n\n"
        "Language Selection Rationale:\n"
        f"{exercise.get('language_selection_rationale', '')}\n\n"
        "Learning Objectives:\n"
        f"{objective_lines}\n\n"
        f"{leetcode_block}"
        "Complexity Profile:\n"
        f"{profile_lines}\n\n"
        "Verification Flow:\n"
        f"{chr(10).join(f'- {step}' for step in exercise.get('verification_flow', [])) or '- pending'}\n\n"
        "Task:\n"
        f"{exercise.get('prompt', '')}\n\n"
        "Function Contract:\n"
        f"{spec['function_contract']}\n\n"
        "Input Schema:\n"
        f"{spec['input_schema']}\n\n"
        "Output Schema:\n"
        f"{spec['output_schema']}\n\n"
        "Metric Definitions:\n"
        f"{spec['metric_definitions']}\n\n"
        "Edge Cases:\n"
        f"{spec['edge_cases']}\n\n"
        "Constraints / Hints:\n"
        "- Work from the provided evidence and verification target.\n"
        "- Keep the implementation narrow and testable.\n"
        "- Tests are pre-generated and visible.\n"
        "- Do not edit the tests unless the exercise explicitly says it is a test-design exercise.\n\n"
        f"{spec['constraints']}\n\n"
        "Deliverables:\n"
        f"{deliverables}\n\n"
        "Evaluation Method:\n"
        f"{exercise.get('evaluation_method', '')}\n\n"
        "Expected Output:\n"
        f"{exercise.get('expected_output_kind', '')}\n\n"
        "Verification:\n"
        f"{exercise.get('verification', '')}\n"
        "\n"
        "Acceptance Criteria:\n"
        f"{spec['acceptance_criteria']}\n"
        '"""\n\n'
    )
def build_sql_header(exercise: dict) -> str:
    deliverables = "\n".join(f"-- - {item}" for item in exercise.get("deliverables", [])) or "-- - Complete the task."
    profile_lines = "\n".join(
        f"-- - {key}: {value}" for key, value in exercise.get("complexity_profile", {}).items()
    ) or "-- - pending"
    objective_lines = "\n".join(
        f"-- - {item}" for item in exercise.get("learning_objectives", [])
    ) or "-- - pending"
    return (
        f"-- Title: {exercise['title']}\n"
        f"-- Level: {exercise['level_id']}\n"
        f"-- Mode: {exercise.get('mode', 'coding')}\n"
        f"-- Type: {exercise.get('type', 'exercise')}\n"
        f"-- Source: {exercise.get('source', 'plan')}\n"
        f"-- Style: {exercise.get('style', 'exercise')}\n"
        f"-- Support Level: {exercise.get('support_level', '')}\n"
        f"-- Language Focus: {exercise.get('language_focus', '')}\n"
        f"-- Implementation Target: {exercise.get('implementation_target', '')}\n"
        f"-- User Responsibility: {exercise.get('user_responsibility', '')}\n"
        f"-- Test Strategy: {exercise.get('test_strategy', '')}\n"
        f"-- Test Edit Policy: {exercise.get('test_edit_policy', '')}\n"
        "--\n"
        "-- Training Goal:\n"
        f"-- {exercise.get('summary', '')}\n"
        "--\n"
        "-- Problem Statement:\n"
        f"-- {exercise.get('problem', exercise.get('prompt', ''))}\n"
        "--\n"
        "-- Learning Objectives:\n"
        f"{objective_lines}\n"
        "--\n"
        "-- Complexity Profile:\n"
        f"{profile_lines}\n"
        "--\n"
        "-- Verification Flow:\n"
        f"{chr(10).join(f'-- - {step}' for step in exercise.get('verification_flow', [])) or '-- - pending'}\n"
        "--\n"
        "-- Deliverables:\n"
        f"{deliverables}\n"
        "--\n"
        "-- Evaluation Method:\n"
        f"-- {exercise.get('evaluation_method', '')}\n"
        "--\n"
        "-- Expected Output:\n"
        f"-- {exercise.get('expected_output_kind', '')}\n"
        "--\n"
        "-- Verification:\n"
        f"-- {exercise.get('verification', '')}\n\n"
    )
def build_test_header(exercise: dict) -> str:
    return (
        '"""\n'
        f"Test scaffold for: {exercise['title']}\n"
        f"Verification target: {exercise.get('verification', '')}\n"
        '"""\n\n'
    )


def render_prompt(exercise: dict) -> str:
    deliverables = "\n".join(f"- {item}" for item in exercise.get("deliverables", [])) or "- Complete the task."
    profile_lines = "\n".join(
        f"- `{key}`: {value}" for key, value in exercise.get("complexity_profile", {}).items()
    ) or "- pending"
    objective_lines = "\n".join(
        f"- {item}" for item in exercise.get("learning_objectives", [])
    ) or "- pending"
    spec = coding_spec_sections(exercise) if exercise.get("mode") == "coding" else None
    coding_details = ""
    if spec:
        leetcode = ""
        if exercise.get("style") == "leetcode":
            topics = ", ".join(str(item) for item in exercise.get("topics", []) if str(item).strip()) or "general"
            examples = []
            for idx, example in enumerate(exercise.get("examples", []), start=1):
                if isinstance(example, dict):
                    examples.append(f"### Example {idx}\nInput: `{example.get('input', '')}`\n\nOutput: `{example.get('output', '')}`")
                else:
                    examples.append(f"### Example {idx}\n{example}")
            constraints = "\n".join(f"- {item}" for item in exercise.get("constraints", []) if str(item).strip()) or "- none"
            hints = "\n".join(f"- {item}" for item in exercise.get("hints", []) if str(item).strip()) or "- none"
            complexity = exercise.get("expected_complexity", {})
            complexity_text = "\n".join(f"- {key}: {value}" for key, value in complexity.items()) if isinstance(complexity, dict) and complexity else "- not specified"
            leetcode = (
                f"\n## Difficulty\n{exercise.get('difficulty', 'easy')}\n\n"
                f"## Topics\n{topics}\n\n"
                f"## Problem Statement\n{exercise.get('problem', exercise.get('prompt', ''))}\n\n"
                f"## Examples\n{chr(10).join(examples) or 'No examples provided.'}\n\n"
                f"## Constraints\n{constraints}\n\n"
                f"## Function Signature\n{exercise.get('function_signature', '')}\n\n"
                f"## Expected Complexity\n{complexity_text}\n\n"
                f"## Hints\n{hints}\n\n"
            )
        coding_details = (
            f"{leetcode}"
            f"## Function Contract\n{spec['function_contract']}\n\n"
            f"## Input Schema\n{spec['input_schema']}\n\n"
            f"## Output Schema\n{spec['output_schema']}\n\n"
            f"## Metric Definitions\n{spec['metric_definitions']}\n\n"
            f"## Edge Cases\n{spec['edge_cases']}\n\n"
            f"## Acceptance Criteria\n{spec['acceptance_criteria']}\n"
        )
    return (
        f"# {exercise['title']}\n\n"
        f"## Level\n{exercise['level_id']}\n\n"
        f"## Mode\n{exercise.get('mode', 'coding')}\n\n"
        f"## Type\n{exercise.get('type', 'exercise')}\n\n"
        f"## Source\n{exercise.get('source', 'plan')}\n\n"
        f"## Style\n{exercise.get('style', 'exercise')}\n\n"
        f"## Language Focus\n{exercise.get('language_focus', '')}\n\n"
        f"## Implementation Target\n{exercise.get('implementation_target', '')}\n\n"
        f"## User Responsibility\n{exercise.get('user_responsibility', '')}\n\n"
        f"## Test Strategy\n{exercise.get('test_strategy', '')}\n\n"
        f"## Test Edit Policy\n{exercise.get('test_edit_policy', '')}\n\n"
        f"## Summary\n{exercise.get('summary', '')}\n\n"
        f"## Why This Fits The Level\n{exercise.get('fit_rationale', '')}\n\n"
        f"## Language Selection Rationale\n{exercise.get('language_selection_rationale', '')}\n\n"
        f"## Learning Objectives\n{objective_lines}\n\n"
        f"## Complexity Profile\n{profile_lines}\n\n"
        f"## Prompt\n{exercise.get('prompt', '')}\n\n"
        f"{coding_details}"
        f"## Verification Flow\n"
        f"{chr(10).join(f'- {step}' for step in exercise.get('verification_flow', [])) or '- pending'}\n\n"
        f"## Evaluation Method\n{exercise.get('evaluation_method', '')}\n\n"
        f"## Expected Output\n{exercise.get('expected_output_kind', '')}\n\n"
        f"## Verification\n{exercise.get('verification', '')}\n\n"
        f"## Deliverables\n{deliverables}\n"
    )
def render_rubric(exercise: dict) -> str:
    profile_lines = "\n".join(
        f"- {key}: {value}" for key, value in exercise.get("complexity_profile", {}).items()
    ) or "- pending"
    return (
        f"# Review Notes for {exercise['title']}\n\n"
        f"- Fit rationale: {exercise.get('fit_rationale', '')}\n"
        f"- Language focus: {exercise.get('language_focus', '')}\n"
        f"- Language selection rationale: {exercise.get('language_selection_rationale', '')}\n"
        f"- User responsibility: {exercise.get('user_responsibility', '')}\n"
        f"- Test strategy: {exercise.get('test_strategy', '')}\n"
        f"- Test edit policy: {exercise.get('test_edit_policy', '')}\n"
        f"- Evaluation method: {exercise.get('evaluation_method', '')}\n"
        f"- Expected output: {exercise.get('expected_output_kind', '')}\n"
        f"- Verification target: {exercise.get('verification', '')}\n"
        f"- Complexity profile:\n{profile_lines}\n"
    )


def render_starter(exercise: dict) -> str:
    base = exercise.get("starter_code") or STARTER_BY_TYPE.get(exercise.get("type", "python"), "# Implement the exercise here.\n")
    ext = starter_extension(exercise)
    if ext == "sql":
        return build_sql_header(exercise) + base
    if ext == "py":
        return build_code_header(exercise) + base
    return base


def render_generated_tests(exercise: dict) -> str:
    tests = exercise.get("tests", [])
    signature = str(exercise.get("function_signature", ""))
    match = re.search(r"def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", signature)
    function_name = match.group(1) if match else "solve"
    if not tests:
        return TEST_BY_TYPE.get(exercise.get("type", "python"), "def test_placeholder() -> None:\n    assert True\n")
    lines = ["import pytest\n\n", "from starter import " + function_name + "\n\n"]
    for idx, case in enumerate(tests, start=1):
        if not isinstance(case, dict):
            continue
        args = case.get("input", [])
        expected = case.get("expected")
        if not isinstance(args, list):
            args = [args]
        lines.append(f"def test_case_{idx}() -> None:\n")
        lines.append(f"    assert {function_name}(*{args!r}) == {expected!r}\n\n")
    return "".join(lines) if len(lines) > 2 else TEST_BY_TYPE.get(exercise.get("type", "python"), "def test_placeholder() -> None:\n    assert True\n")


def build_resources(exercise: dict, exercise_dir: Path, workspace: Path) -> list[dict]:
    level_dir_name = f"level-{exercise['level_id']}"
    prompt_rel = Path("exercises") / level_dir_name / exercise["id"] / "prompt.md"
    resources = [
        {"label": "Prompt", "kind": "prompt", "path": prompt_rel.as_posix()},
    ]

    if exercise.get("mode") == "coding":
        ext = starter_extension(exercise)
        starter_name = f"starter.{ext}"
        starter_rel = Path("exercises") / level_dir_name / exercise["id"] / starter_name
        test_name = exercise.get("test_file", f"test_{slugify(exercise['id'])}.py")
        test_rel = Path("exercises") / level_dir_name / exercise["id"] / test_name
        write_text(exercise_dir / starter_name, render_starter(exercise))
        write_text(exercise_dir / test_name, build_test_header(exercise) + render_generated_tests(exercise))
        resources.extend(
            [
                {"label": "Starter", "kind": "starter", "path": starter_rel.as_posix()},
                {"label": "Tests", "kind": "tests", "path": test_rel.as_posix()},
            ]
        )
    else:
        notes_rel = Path("exercises") / level_dir_name / exercise["id"] / "answer_notes.md"
        rubric_rel = Path("exercises") / level_dir_name / exercise["id"] / "review_notes.md"
        write_text(exercise_dir / "answer_notes.md", render_starter(exercise))
        write_text(exercise_dir / "review_notes.md", render_rubric(exercise))
        resources.extend(
            [
                {"label": "Answer Notes", "kind": "answer-notes", "path": notes_rel.as_posix()},
                {"label": "Review Notes", "kind": "review-notes", "path": rubric_rel.as_posix()},
            ]
        )
    return resources


def normalize_exercise(exercise: dict) -> dict:
    normalized = dict(exercise)
    base_complexity: dict[str, Any] = {}
    complexity_candidate = DEFAULT_COMPLEXITY_BY_LEVEL.get(normalized["level_id"], {})
    if isinstance(complexity_candidate, dict):
        base_complexity = dict(complexity_candidate)
    normalized["support_level"] = normalized.get(
        "support_level",
        DEFAULT_SUPPORT_BY_LEVEL.get(normalized["level_id"], "scaffolded"),
    )
    normalized.setdefault(
        "complexity_profile",
        base_complexity,
    )
    normalized.setdefault("source", "plan")
    normalized.setdefault("category", normalized.get("track", normalized.get("mode", "exercise")))
    normalized.setdefault("style", "leetcode" if normalized.get("mode") == "coding" else "project_drill")
    normalized.setdefault("difficulty", "easy")
    normalized.setdefault("topics", [])
    normalized.setdefault("examples", [])
    normalized.setdefault("constraints", [])
    normalized.setdefault("hints", [])
    normalized.setdefault("tests", [])
    normalized.setdefault("expected_complexity", {})
    normalized.setdefault("learning_objectives", [])
    if normalized.get("mode") == "coding" and normalized.get("style") == "leetcode":
        normalized.setdefault("problem", normalized.get("prompt", ""))
        normalized.setdefault("function_signature", "def solve() -> object:")
        normalized.setdefault("starter_code", STARTER_BY_TYPE.get(normalized.get("type", "python"), STARTER_BY_TYPE["python"]))
    normalized.setdefault("fit_rationale", "Pending fit rationale from Codex.")
    normalized.setdefault("implementation_target", f"starter.{starter_extension(normalized)}")
    normalized.setdefault("user_responsibility", "implementation-only")
    normalized.setdefault("test_strategy", "system-generated-visible")
    normalized.setdefault("test_edit_policy", "do-not-edit")
    normalized.setdefault(
        "verification_flow",
        [
            "Run the generated tests before editing code.",
            "Modify only the implementation target unless the exercise explicitly says otherwise.",
            "Re-run the generated tests until they pass, then add the required short explanation.",
        ],
    )
    normalized.setdefault("language_focus", normalized.get("type", "coding"))
    normalized.setdefault(
        "language_selection_rationale",
        "Pending language selection rationale from Codex.",
    )
    normalized.setdefault("evaluation_method", "Manual review against prompt and verification target.")
    normalized.setdefault("expected_output_kind", "code")
    normalized.setdefault("verification", "Review the output against the exercise requirements.")
    normalized.setdefault("deliverables", ["Completed exercise assets"])
    normalized.setdefault("is_challenge", False)
    if "track" not in normalized:
        if normalized.get("mode") == "coding" and normalized.get("type") == "debugging":
            normalized["track"] = "debugging"
        elif normalized.get("mode") == "coding":
            normalized["track"] = "coding"
        elif normalized.get("type") in {"system-design", "project-defense"}:
            normalized["track"] = normalized["type"]
        else:
            normalized["track"] = "interview"
    return normalized


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python generate_exercise_assets.py <exercise_catalog_json> <workspace_dir>")
        return 1

    catalog_path = Path(sys.argv[1]).resolve()
    workspace = Path(sys.argv[2]).resolve()
    exercises_root = workspace / "exercises"
    exercises_root.mkdir(parents=True, exist_ok=True)

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    mode_decision = load_mode_decision(workspace)
    active_levels = load_active_levels(workspace)
    level_lookup = load_level_map_lookup(workspace)
    cv_profile_path = workspace / "analysis" / "current" / "cv_profile.json"
    cv_language_evidence: list[str] = []
    if cv_profile_path.exists():
        cv_profile = json.loads(cv_profile_path.read_text(encoding="utf-8"))
        if isinstance(cv_profile, dict):
            cv_language_evidence = extract_cv_language_evidence(cv_profile)

    normalized_exercises = []
    for exercise in catalog.get("exercises", []):
        normalized = normalize_exercise(exercise)
        validate_level_fit(normalized)
        validate_foundation_language(normalized, cv_language_evidence)
        validate_leetcode_style(normalized)
        validate_coding_responsibility(normalized)
        validate_live_coding_policy(normalized)
        level_dir = exercises_root / f"level-{normalized['level_id']}"
        exercise_dir = level_dir / normalized["id"]
        exercise_dir.mkdir(parents=True, exist_ok=True)
        write_text(exercise_dir / "prompt.md", render_prompt(normalized))
        (exercise_dir / "submissions").mkdir(exist_ok=True)
        normalized["resources"] = build_resources(normalized, exercise_dir, workspace)
        normalized_exercises.append(normalized)

    if mode_decision is not None:
        validate_mode_decision_alignment(normalized_exercises, mode_decision)
    validate_level_quota(normalized_exercises, active_levels, mode_decision, level_lookup)

    catalog["exercises"] = normalized_exercises
    write_json(catalog_path, catalog)
    print(f"Generated exercise assets under {exercises_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
