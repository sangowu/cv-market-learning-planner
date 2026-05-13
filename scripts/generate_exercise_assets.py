from __future__ import annotations

import json
import re
import sys
from pathlib import Path

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


def validate_foundation_prerequisites(exercise: dict) -> None:
    if exercise.get("level_id") != "foundation-gaps" or exercise.get("mode") != "coding":
        return
    if exercise.get("prerequisite_support_mode") != "teach":
        raise ValueError(
            f"Exercise `{exercise['id']}` in level `foundation-gaps` must use `prerequisite_support_mode=teach`."
        )
    units = exercise.get("prerequisite_units")
    if not isinstance(units, list) or not units:
        raise ValueError(
            f"Exercise `{exercise['id']}` in level `foundation-gaps` must include at least one prerequisite unit."
        )
    required_fields = ("concept", "why_it_matters_here", "quick_explanation", "self_check")
    for idx, unit in enumerate(units, start=1):
        if not isinstance(unit, dict):
            raise ValueError(
                f"Exercise `{exercise['id']}` prerequisite unit #{idx} must be an object."
            )
        missing = [field for field in required_fields if not str(unit.get(field, "")).strip()]
        if missing:
            raise ValueError(
                f"Exercise `{exercise['id']}` prerequisite unit #{idx} missing required fields: {', '.join(missing)}"
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


def starter_extension(exercise: dict) -> str:
    if exercise.get("starter_ext"):
        return exercise["starter_ext"]
    if exercise.get("type") == "sql":
        return "sql"
    if exercise.get("mode") == "interview":
        return "md"
    return "py"


def render_prerequisite_units_text(exercise: dict, prefix: str = "- ") -> str:
    units = exercise.get("prerequisite_units", [])
    if units:
        sections = []
        for unit in units:
            lines = [
                f"{prefix}Concept: {unit.get('concept', '')}",
                f"{prefix}Why it matters: {unit.get('why_it_matters_here', '')}",
                f"{prefix}Quick explanation: {unit.get('quick_explanation', '')}",
                f"{prefix}Tiny example: {unit.get('tiny_example', '')}",
                f"{prefix}Self-check: {unit.get('self_check', '')}",
            ]
            sections.append("\n".join(lines))
        return "\n\n".join(sections)
    prerequisites = exercise.get("prerequisites", [])
    return "\n".join(f"{prefix}{item}" for item in prerequisites) or f"{prefix}none"


def render_prerequisite_units_markdown(exercise: dict) -> str:
    units = exercise.get("prerequisite_units", [])
    if units:
        sections = []
        for idx, unit in enumerate(units, start=1):
            sections.append(
                f"### {idx}. {unit.get('concept', 'Prerequisite')}\n"
                f"- Why it matters: {unit.get('why_it_matters_here', '')}\n"
                f"- Quick explanation: {unit.get('quick_explanation', '')}\n"
                f"- Tiny example: {unit.get('tiny_example', '')}\n"
                f"- Self-check: {unit.get('self_check', '')}"
            )
        return "\n\n".join(sections)
    prerequisites = exercise.get("prerequisites", [])
    return "\n".join(f"- {item}" for item in prerequisites) or "- none"


def build_code_header(exercise: dict) -> str:
    deliverables = "\n".join(f"- {item}" for item in exercise.get("deliverables", [])) or "- Complete the task."
    profile_lines = "\n".join(
        f"- {key}: {value}" for key, value in exercise.get("complexity_profile", {}).items()
    ) or "- pending"
    objective_lines = "\n".join(
        f"- {item}" for item in exercise.get("learning_objectives", [])
    ) or "- pending"
    prerequisite_block = render_prerequisite_units_text(exercise)
    return (
        '"""\n'
        f"Title: {exercise['title']}\n"
        f"Level: {exercise['level_id']}\n"
        f"Mode: {exercise.get('mode', 'coding')}\n"
        f"Type: {exercise.get('type', 'exercise')}\n"
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
        "Prerequisite Support Mode:\n"
        f"{exercise.get('prerequisite_support_mode', '')}\n\n"
        "Readiness Expectation:\n"
        f"{exercise.get('readiness_expectation', '')}\n\n"
        "Prerequisites:\n"
        f"{prerequisite_block}\n\n"
        "Complexity Profile:\n"
        f"{profile_lines}\n\n"
        "Verification Flow:\n"
        f"{chr(10).join(f'- {step}' for step in exercise.get('verification_flow', [])) or '- pending'}\n\n"
        "Task:\n"
        f"{exercise.get('prompt', '')}\n\n"
        "Constraints / Hints:\n"
        "- Work from the provided evidence and verification target.\n"
        "- Keep the implementation narrow and testable.\n"
        "- Prefer explicit trade-offs over hidden complexity.\n\n"
        "- Tests are pre-generated and visible.\n"
        "- Do not edit the tests unless the exercise explicitly says it is a test-design exercise.\n\n"
        "Deliverables:\n"
        f"{deliverables}\n\n"
        "Evaluation Method:\n"
        f"{exercise.get('evaluation_method', '')}\n\n"
        "Expected Output:\n"
        f"{exercise.get('expected_output_kind', '')}\n\n"
        "Verification:\n"
        f"{exercise.get('verification', '')}\n"
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
    prerequisite_block = render_prerequisite_units_text(exercise, prefix="-- - ")
    return (
        f"-- Title: {exercise['title']}\n"
        f"-- Level: {exercise['level_id']}\n"
        f"-- Mode: {exercise.get('mode', 'coding')}\n"
        f"-- Type: {exercise.get('type', 'exercise')}\n"
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
        "-- Why This Fits The Level:\n"
        f"-- {exercise.get('fit_rationale', '')}\n"
        "--\n"
        "-- Language Selection Rationale:\n"
        f"-- {exercise.get('language_selection_rationale', '')}\n"
        "--\n"
        "-- Learning Objectives:\n"
        f"{objective_lines}\n"
        "--\n"
        "-- Prerequisite Support Mode:\n"
        f"-- {exercise.get('prerequisite_support_mode', '')}\n"
        "--\n"
        "-- Readiness Expectation:\n"
        f"-- {exercise.get('readiness_expectation', '')}\n"
        "--\n"
        "-- Prerequisites:\n"
        f"{prerequisite_block}\n"
        "--\n"
        "-- Complexity Profile:\n"
        f"{profile_lines}\n"
        "--\n"
        "-- Verification Flow:\n"
        f"{chr(10).join(f'-- - {step}' for step in exercise.get('verification_flow', [])) or '-- - pending'}\n"
        "--\n"
        "-- Task:\n"
        f"-- {exercise.get('prompt', '')}\n"
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
    prerequisite_lines = render_prerequisite_units_markdown(exercise)
    return (
        f"# {exercise['title']}\n\n"
        f"## Level\n{exercise['level_id']}\n\n"
        f"## Mode\n{exercise.get('mode', 'coding')}\n\n"
        f"## Type\n{exercise.get('type', 'exercise')}\n\n"
        f"## Language Focus\n{exercise.get('language_focus', '')}\n\n"
        f"## Implementation Target\n{exercise.get('implementation_target', '')}\n\n"
        f"## User Responsibility\n{exercise.get('user_responsibility', '')}\n\n"
        f"## Test Strategy\n{exercise.get('test_strategy', '')}\n\n"
        f"## Test Edit Policy\n{exercise.get('test_edit_policy', '')}\n\n"
        f"## Summary\n{exercise.get('summary', '')}\n\n"
        f"## Why This Fits The Level\n{exercise.get('fit_rationale', '')}\n\n"
        f"## Language Selection Rationale\n{exercise.get('language_selection_rationale', '')}\n\n"
        f"## Learning Objectives\n{objective_lines}\n\n"
        f"## Prerequisite Support Mode\n{exercise.get('prerequisite_support_mode', '')}\n\n"
        f"## Readiness Expectation\n{exercise.get('readiness_expectation', '')}\n\n"
        f"## Prerequisites\n{prerequisite_lines}\n\n"
        f"## Complexity Profile\n{profile_lines}\n\n"
        f"## Prompt\n{exercise.get('prompt', '')}\n\n"
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
        f"- Prerequisite support mode: {exercise.get('prerequisite_support_mode', '')}\n"
        f"- Readiness expectation: {exercise.get('readiness_expectation', '')}\n"
        f"- Evaluation method: {exercise.get('evaluation_method', '')}\n"
        f"- Expected output: {exercise.get('expected_output_kind', '')}\n"
        f"- Verification target: {exercise.get('verification', '')}\n"
        f"- Complexity profile:\n{profile_lines}\n"
    )


def render_starter(exercise: dict) -> str:
    base = STARTER_BY_TYPE.get(exercise.get("type", "python"), "# Implement the exercise here.\n")
    ext = starter_extension(exercise)
    if ext == "sql":
        return build_sql_header(exercise) + base
    if ext == "py":
        return build_code_header(exercise) + base
    return base


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
        write_text(exercise_dir / test_name, build_test_header(exercise) + TEST_BY_TYPE.get(exercise.get("type", "python"), "def test_placeholder() -> None:\n    assert True\n"))
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
    normalized["support_level"] = normalized.get(
        "support_level",
        DEFAULT_SUPPORT_BY_LEVEL.get(normalized["level_id"], "scaffolded"),
    )
    normalized.setdefault(
        "complexity_profile",
        dict(DEFAULT_COMPLEXITY_BY_LEVEL.get(normalized["level_id"], {})),
    )
    normalized.setdefault("learning_objectives", [])
    normalized.setdefault("prerequisites", [])
    normalized.setdefault("prerequisite_units", [])
    normalized.setdefault(
        "prerequisite_support_mode",
        DEFAULT_PREREQ_SUPPORT_BY_LEVEL.get(normalized["level_id"], "remind"),
    )
    normalized.setdefault("readiness_expectation", "Pending readiness expectation from Codex.")
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
        validate_foundation_prerequisites(normalized)
        validate_foundation_language(normalized, cv_language_evidence)
        validate_coding_responsibility(normalized)
        level_dir = exercises_root / f"level-{normalized['level_id']}"
        exercise_dir = level_dir / normalized["id"]
        exercise_dir.mkdir(parents=True, exist_ok=True)
        write_text(exercise_dir / "prompt.md", render_prompt(normalized))
        (exercise_dir / "submissions").mkdir(exist_ok=True)
        normalized["resources"] = build_resources(normalized, exercise_dir, workspace)
        normalized_exercises.append(normalized)

    catalog["exercises"] = normalized_exercises
    write_json(catalog_path, catalog)
    print(f"Generated exercise assets under {exercises_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
