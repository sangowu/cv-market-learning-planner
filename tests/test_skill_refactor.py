from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = SKILL_ROOT / "scripts"


def run_script(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def run_script_allow_failure(script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_level_map() -> dict:
    return {
        "levels": [
            {
                "id": "foundation-gaps",
                "label": "Foundation Gaps",
                "active": True,
                "priority": 10,
                "cv_evidence": ["Testing depth is implicit rather than explicit in the CV."],
                "market_evidence": ["Roles expect reliable Python implementation with tests."],
                "why_now": "Missing fundamentals are the first blocker.",
                "depends_on": [],
                "complexity_profile": {
                    "objective_count": "low",
                    "decision_density": "low",
                    "statefulness": "low",
                    "ambiguity": "low",
                    "verification_difficulty": "low",
                    "scaffolding_strength": "high",
                    "delivery_scope": "narrow",
                },
            },
            {
                "id": "system-rigor",
                "label": "System Rigor",
                "active": True,
                "priority": 8,
                "cv_evidence": ["Debugging and observability evidence is thinner than delivery evidence."],
                "market_evidence": ["Production AI roles demand reliability and evaluation discipline."],
                "why_now": "The CV needs stronger evidence of test and failure-mode handling.",
                "depends_on": ["foundation-gaps"],
                "complexity_profile": {
                    "objective_count": "medium",
                    "decision_density": "high",
                    "statefulness": "medium",
                    "ambiguity": "medium",
                    "verification_difficulty": "high",
                    "scaffolding_strength": "low",
                    "delivery_scope": "broad",
                },
            },
            {
                "id": "interview-readiness",
                "label": "Interview Readiness",
                "active": True,
                "priority": 6,
                "cv_evidence": ["Projects need tighter defense narratives."],
                "market_evidence": ["Interview loops include live coding and project defense."],
                "why_now": "The user needs direct practice for interview pressure.",
                "depends_on": ["system-rigor"],
                "complexity_profile": {
                    "objective_count": "medium",
                    "decision_density": "medium",
                    "statefulness": "medium",
                    "ambiguity": "medium",
                    "verification_difficulty": "medium",
                    "scaffolding_strength": "low",
                    "delivery_scope": "timed",
                },
            },
            {
                "id": "independent-implementation",
                "label": "Independent Implementation",
                "active": False,
                "priority": 0,
                "cv_evidence": [],
                "market_evidence": [],
                "why_now": "Skipped for this snapshot.",
                "depends_on": ["foundation-gaps"],
                "complexity_profile": {
                    "objective_count": "medium",
                    "decision_density": "medium",
                    "statefulness": "medium",
                    "ambiguity": "medium",
                    "verification_difficulty": "medium",
                    "scaffolding_strength": "medium",
                    "delivery_scope": "contained",
                },
            },
        ]
    }


def build_learning_plan() -> dict:
    return {
        "title": "Adaptive AI Engineer Learning Plan",
        "summary": "A level-driven plan aligned to CV evidence and current global demand.",
        "active_levels": [
            "foundation-gaps",
            "system-rigor",
            "interview-readiness",
        ],
        "level_order": [
            "foundation-gaps",
            "system-rigor",
            "interview-readiness",
        ],
        "sequencing": [
            {
                "label": "Phase 1",
                "summary": "Repair fundamentals before reliability and interview pressure.",
                "level_ids": ["foundation-gaps", "system-rigor"],
            },
            {
                "label": "Phase 2",
                "summary": "Run timed interview simulations on top of the repaired base.",
                "level_ids": ["interview-readiness"],
            },
        ],
    }


def build_catalog() -> dict:
    return {
        "exercises": [
            {
                "id": "foundation-pipeline-debug",
                "level_id": "foundation-gaps",
                "mode": "coding",
                "type": "python",
                "title": "Repair a brittle ETL transform",
                "summary": "Practice reliable Python data shaping with tests.",
                "prompt": "Implement normalization and validation for inconsistent records.",
                "resources": [],
                "implementation_target": "starter.py",
                "user_responsibility": "implementation-only",
                "test_strategy": "system-generated-visible",
                "test_edit_policy": "do-not-edit",
                "verification_flow": [
                    "Run the generated tests before editing code.",
                    "Modify only the implementation target unless the exercise explicitly says otherwise.",
                    "Re-run the generated tests until they pass, then add the required short explanation.",
                ],
                "language_focus": "python",
                "language_selection_rationale": "Python is strongly evidenced in the CV and is the most direct fundamentals track.",
                "complexity_profile": {
                    "objective_count": "low",
                    "decision_density": "low",
                    "statefulness": "low",
                    "ambiguity": "low",
                    "verification_difficulty": "low",
                    "scaffolding_strength": "high",
                    "delivery_scope": "narrow",
                },
                "learning_objectives": ["dict grouping", "edge-case handling"],
                "prerequisites": ["basic Python collections"],
                "prerequisite_units": [
                    {
                        "concept": "Python sets",
                        "why_it_matters_here": "The task needs fast deduplication and membership checks.",
                        "quick_explanation": "A set stores unique items and supports average O(1) membership checks in typical use.",
                        "tiny_example": "required = {'python', 'sql'}",
                        "self_check": "Why is a set a better fit than repeatedly scanning a list here?",
                    }
                ],
                "prerequisite_support_mode": "teach",
                "readiness_expectation": "The learner should be able to trace a small set-based example by hand before coding.",
                "fit_rationale": "Single-function exercise with direct verification and high scaffolding.",
                "evaluation_method": "Run the generated tests and explain the edge cases.",
                "expected_output_kind": "python-module",
                "verification": "Run pytest against the generated test file.",
                "deliverables": ["starter.py", "tests", "notes"],
                "support_level": "guided",
            },
            {
                "id": "rigor-observability-drill",
                "level_id": "system-rigor",
                "mode": "coding",
                "type": "debugging",
                "title": "Stabilize a flaky service path",
                "summary": "Find the failure mode and codify the fix with regression coverage.",
                "prompt": "Document the failure and implement a narrow corrective change.",
                "resources": [],
                "implementation_target": "starter.py",
                "user_responsibility": "implementation-only",
                "test_strategy": "system-generated-visible",
                "test_edit_policy": "do-not-edit",
                "verification_flow": [
                    "Run the generated tests before editing code.",
                    "Modify only the implementation target unless the exercise explicitly says otherwise.",
                    "Re-run the generated tests until they pass, then add the required short explanation.",
                ],
                "language_focus": "python",
                "language_selection_rationale": "Python remains the dominant implementation language in the CV for debugging practice.",
                "complexity_profile": {
                    "objective_count": "medium",
                    "decision_density": "high",
                    "statefulness": "medium",
                    "ambiguity": "medium",
                    "verification_difficulty": "high",
                    "scaffolding_strength": "low",
                    "delivery_scope": "broad",
                },
                "learning_objectives": ["trace a failure mode", "add regression coverage"],
                "prerequisites": ["basic testing workflow"],
                "prerequisite_support_mode": "remind",
                "readiness_expectation": "The learner should already know how to run and read a simple failing test.",
                "fit_rationale": "Requires diagnosis plus verification rather than just first-pass implementation.",
                "evaluation_method": "Explain the root cause and show how the fix is verified.",
                "expected_output_kind": "python-module",
                "verification": "Run the generated tests and describe the failure mode.",
                "deliverables": ["starter.py", "tests", "write-up"],
                "support_level": "sparse",
            },
            {
                "id": "interview-live-debug",
                "level_id": "interview-readiness",
                "mode": "interview",
                "type": "debugging-interview",
                "title": "Timed debugging interview",
                "summary": "Practice explaining an investigation path under time pressure.",
                "prompt": "Walk through how you would isolate the defect and justify the fix.",
                "resources": [],
                "implementation_target": "answer_notes.md",
                "user_responsibility": "implementation-only",
                "test_strategy": "system-generated-visible",
                "test_edit_policy": "do-not-edit",
                "verification_flow": [
                    "Read the prompt and answer notes scaffold.",
                    "Draft your response in the implementation target.",
                    "Review your answer against the provided review notes.",
                ],
                "language_focus": "python",
                "language_selection_rationale": "The CV shows the strongest implementation evidence in Python-based project work.",
                "complexity_profile": {
                    "objective_count": "medium",
                    "decision_density": "medium",
                    "statefulness": "medium",
                    "ambiguity": "medium",
                    "verification_difficulty": "medium",
                    "scaffolding_strength": "low",
                    "delivery_scope": "timed",
                },
                "learning_objectives": ["structure a debugging explanation", "defend trade-offs aloud"],
                "prerequisites": ["basic debugging vocabulary"],
                "prerequisite_support_mode": "assume",
                "readiness_expectation": "The learner should already be able to explain a simple bug investigation without tutorial support.",
                "fit_rationale": "The emphasis is explanation under interview pressure rather than system breadth.",
                "evaluation_method": "Self-review against the prompt and follow-up questions.",
                "expected_output_kind": "written-response",
                "verification": "Answer the prompt and review the notes against the rubric.",
                "deliverables": ["prompt.md", "answer_notes.md", "review_notes.md"],
                "support_level": "from-scratch",
            },
        ]
    }


def extract_hrefs(path: Path) -> list[str]:
    return re.findall(r'href="([^"]+)"', path.read_text(encoding="utf-8"))


def test_workspace_init_and_run_cycle_snapshot(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    cv_path = tmp_path / "cv.txt"
    cv_path.write_text("Saige Wu\nPython\nFastAPI\n", encoding="utf-8")

    run_script("init_learning_workspace.py", str(workspace))

    assert (workspace / "analysis" / "current").is_dir()
    assert (workspace / "analysis" / "history").is_dir()
    assert (workspace / "planning").is_dir()
    assert (workspace / "plan").is_dir()
    assert (workspace / "reports").is_dir()
    assert (workspace / "exercises" / "level-foundation-gaps").is_dir()
    assert (workspace / "planning" / "learning_plan.json").exists()
    assert (workspace / "progress" / "reviews.jsonl").exists()
    wrapper_path = workspace / "scripts" / "run_learning_tool.ps1"
    assert wrapper_path.exists()
    wrapper_text = wrapper_path.read_text(encoding="utf-8")
    assert "update_progress.py" in wrapper_text

    write_json(workspace / "analysis" / "current" / "cv_profile.json", {"name": "Saige"})
    write_json(workspace / "analysis" / "current" / "market_demand.json", {"scope": "global"})
    write_json(workspace / "analysis" / "current" / "gap_analysis.json", {"priority_gaps": ["testing"]})
    write_json(workspace / "analysis" / "current" / "level_map.json", build_level_map())

    run_script("run_cycle.py", str(workspace), str(cv_path))

    history_files = list((workspace / "analysis" / "history").glob("*_cv_profile.json"))
    assert history_files, "expected run_cycle to snapshot prior current analysis"
    assert "Saige Wu" in (workspace / "input" / "cv_extracted.txt").read_text(encoding="utf-8")
    next_steps = (workspace / "reports" / "next_steps.md").read_text(encoding="utf-8")
    assert "analysis/current/level_map.json" in next_steps
    assert "planning/exercise_catalog.json" in next_steps


def test_init_workspace_defaults_to_learning_workspace(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "init_learning_workspace.py")],
        check=True,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    workspace = tmp_path / "learning_workspace"
    assert workspace.is_dir()
    assert (workspace / "planning" / "learning_plan.json").exists()
    assert (workspace / "scripts" / "run_learning_tool.ps1").exists()
    assert "Initialized learning workspace at" in result.stdout


def test_generate_assets_and_render_pages(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    learning_plan = build_learning_plan()
    level_map = build_level_map()
    catalog = build_catalog()
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}, {"language": "sql", "weight": 0.6}]},
    )
    write_json(workspace / "planning" / "learning_plan.json", learning_plan)
    write_json(workspace / "planning" / "exercise_catalog.json", catalog)
    write_json(workspace / "analysis" / "current" / "level_map.json", level_map)

    run_script("generate_exercise_assets.py", str(workspace / "planning" / "exercise_catalog.json"), str(workspace))
    run_script(
        "render_plan_pages.py",
        str(workspace / "planning" / "learning_plan.json"),
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace / "analysis" / "current" / "level_map.json"),
        str(workspace / "plan"),
    )

    starter = workspace / "exercises" / "level-foundation-gaps" / "foundation-pipeline-debug" / "starter.py"
    assert starter.exists()
    starter_text = starter.read_text(encoding="utf-8")
    assert 'Title: Repair a brittle ETL transform' in starter_text
    assert "Language Focus: python" in starter_text
    assert "Implementation Target: starter.py" in starter_text
    assert "User Responsibility: implementation-only" in starter_text
    assert "Test Strategy: system-generated-visible" in starter_text
    assert "Test Edit Policy: do-not-edit" in starter_text
    assert "Tests are pre-generated and visible." in starter_text
    assert "Prerequisite Support Mode:" in starter_text
    assert "Readiness Expectation:" in starter_text
    assert "Training Goal:" in starter_text
    assert "Complexity Profile:" in starter_text
    assert "Why This Fits The Level:" in starter_text
    assert "Verification:" in starter_text

    rigor_starter = workspace / "exercises" / "level-system-rigor" / "rigor-observability-drill" / "starter.py"
    assert rigor_starter.exists()

    prompt = workspace / "exercises" / "level-interview-readiness" / "interview-live-debug" / "prompt.md"
    notes = workspace / "exercises" / "level-interview-readiness" / "interview-live-debug" / "answer_notes.md"
    assert prompt.exists()
    assert notes.exists()

    index_html = workspace / "plan" / "index.html"
    level_html = workspace / "plan" / "level-foundation-gaps.html"
    summary_html = workspace / "reports" / "latest-summary.html"
    snapshot_files = list((workspace / "reports").glob("snapshot-*.html"))
    assert index_html.exists()
    assert level_html.exists()
    assert summary_html.exists()
    assert snapshot_files

    level_page = level_html.read_text(encoding="utf-8")
    assert "Missing fundamentals are the first blocker." in level_page
    assert "Roles expect reliable Python implementation with tests." in level_page
    assert "objective_count" in level_page

    summary_page = summary_html.read_text(encoding="utf-8")
    assert "Repair a brittle ETL transform" in summary_page
    assert "Stabilize a flaky service path" in summary_page
    assert "Timed debugging interview" in summary_page

    for href in extract_hrefs(level_html):
        if href.startswith("../exercises/"):
            target = (workspace / "plan" / href).resolve()
            assert target.exists(), f"missing linked resource {href}"

    updated_catalog = load_json(workspace / "planning" / "exercise_catalog.json")
    assert updated_catalog["exercises"][0]["resources"], "generator should resolve resource links"
    assert updated_catalog["exercises"][0]["complexity_profile"]["objective_count"] == "low"
    assert updated_catalog["exercises"][0]["language_focus"] == "python"
    assert updated_catalog["exercises"][0]["prerequisite_support_mode"] == "teach"
    assert updated_catalog["exercises"][0]["user_responsibility"] == "implementation-only"
    assert updated_catalog["exercises"][0]["test_edit_policy"] == "do-not-edit"


def test_update_progress_updates_reviews_and_progress_map(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))
    write_json(workspace / "planning" / "exercise_catalog.json", build_catalog())

    run_script(
        "update_progress.py",
        str(workspace),
        "foundation-pipeline-debug",
        "exercises/level-foundation-gaps/foundation-pipeline-debug/submissions/attempt_01.py",
        "retry",
        "retry with explicit normalization tests",
        "62",
        "testing,edge-cases",
        '["Clear decomposition"]',
        '["Missed null handling"]',
        "targeted-refresh",
        "first pass",
    )

    reviews = (workspace / "progress" / "reviews.jsonl").read_text(encoding="utf-8").splitlines()
    submissions = (workspace / "progress" / "submissions.jsonl").read_text(encoding="utf-8").splitlines()
    stats = load_json(workspace / "progress" / "stats.json")
    progress_map = load_json(workspace / "planning" / "progress_map.json")
    progress_md = (workspace / "progress" / "progress.md").read_text(encoding="utf-8")

    assert len(reviews) == 1
    assert len(submissions) == 1
    review_record = json.loads(reviews[0])
    assert review_record["status"] == "retry"
    assert review_record["strengths"] == ["Clear decomposition"]
    assert review_record["recommended_regeneration_mode"] == "targeted-refresh"

    assert stats["total_submissions"] == 1
    assert stats["total_reviews"] == 1
    assert stats["latest_exercise"] == "foundation-pipeline-debug"
    assert "testing" in stats["common_issue_tags"]

    exercise_state = progress_map["exercises"]["foundation-pipeline-debug"]
    assert exercise_state["status"] == "retry"
    assert exercise_state["review_count"] == 1
    assert progress_map["levels"]["foundation-gaps"]["status"] == "active"
    assert "retry with explicit normalization tests" in progress_md


def test_generate_assets_rejects_level_fit_mismatch(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    invalid_catalog["exercises"][0]["complexity_profile"]["objective_count"] = "medium"
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "does not fit level `foundation-gaps`" in error_text
    assert "objective_count='medium'" in error_text


def test_generate_assets_rejects_test_authoring_deliverables(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}]},
    )
    invalid_catalog["exercises"][0]["deliverables"].append("write tests for extra edge cases")
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "violates implementation-only responsibility" in error_text


def test_generate_assets_rejects_non_cv_foundation_language(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    invalid_catalog["exercises"][0]["language_focus"] = "java"
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}, {"language": "sql", "weight": 0.6}]},
    )
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "is not aligned with CV language evidence" in error_text


def test_generate_assets_rejects_missing_foundation_prerequisite_units(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    invalid_catalog["exercises"][0]["prerequisite_support_mode"] = "teach"
    invalid_catalog["exercises"][0]["prerequisite_units"] = []
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}]},
    )
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "must include at least one prerequisite unit" in error_text


def test_generate_assets_rejects_test_authoring_verification(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}]},
    )
    invalid_catalog["exercises"][0]["verification"] = "Run tests and add new tests for edge cases."
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "violates implementation-only responsibility via verification instructions" in error_text


def test_generate_assets_rejects_interview_live_coding_without_opt_in(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    invalid_catalog = build_catalog()
    invalid_catalog["exercises"][2]["type"] = "live-coding"
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}]},
    )
    write_json(workspace / "planning" / "exercise_catalog.json", invalid_catalog)

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "live-coding" in error_text
    assert "explicit opt-in" in error_text


def test_generate_assets_rejects_level_quota_mismatch_with_mode_decision(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    write_json(workspace / "planning" / "learning_plan.json", build_learning_plan())
    write_json(
        workspace / "analysis" / "current" / "exercise_mode_decision.json",
        {
            "include_coding": True,
            "include_debugging": True,
            "mode_mix": {"coding": 0.5, "debugging": 0.2, "interview": 0.3},
            "confidence": 0.8,
            "rationale": "quota check",
            "evidence": {"cv": ["python"], "market": ["coding interview"]},
        },
    )
    write_json(
        workspace / "analysis" / "current" / "cv_profile.json",
        {"language_evidence": [{"language": "python", "weight": 0.9}]},
    )
    write_json(workspace / "planning" / "exercise_catalog.json", build_catalog())

    result = run_script_allow_failure(
        "generate_exercise_assets.py",
        str(workspace / "planning" / "exercise_catalog.json"),
        str(workspace),
    )

    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "Level quota validation failed" in error_text


def test_validate_generation_passes_with_balanced_catalog(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))

    plan = {
        "title": "Plan",
        "summary": "summary",
        "active_levels": ["foundation-gaps", "system-rigor", "interview-readiness"],
        "level_order": ["foundation-gaps", "system-rigor", "interview-readiness"],
        "sequencing": [],
    }
    write_json(workspace / "planning" / "learning_plan.json", plan)
    write_json(
        workspace / "analysis" / "current" / "exercise_mode_decision.json",
        {
            "include_coding": True,
            "include_debugging": True,
            "mode_mix": {"coding": 0.4, "debugging": 0.2, "interview": 0.4},
            "mode_mix_tolerance": 0.3,
            "level_quota": {"core_per_level": 3, "challenge_per_level": 2, "enforce": True},
        },
    )
    write_json(workspace / "analysis" / "current" / "cv_profile.json", {"language_evidence": [{"language": "python"}]})
    write_json(workspace / "analysis" / "current" / "market_demand.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "gap_analysis.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "level_map.json", build_level_map())

    exercises = []
    level_base = {
        "foundation-gaps": ("low", "low", "low", "low"),
        "system-rigor": ("medium", "medium", "medium", "high"),
        "interview-readiness": ("medium", "high", "high", "medium"),
    }
    for level_id, (obj, dec, amb, ver) in level_base.items():
        for idx in range(3):
            ex_id = f"{level_id}-core-{idx+1}"
            track = "coding" if idx < 2 else "interview"
            ex = {
                "id": ex_id,
                "level_id": level_id,
                "mode": "coding" if track == "coding" else "interview",
                "type": "debugging" if (level_id == "system-rigor" and idx == 0) else "python",
                "track": "debugging" if (level_id == "system-rigor" and idx == 0) else track,
                "is_challenge": False,
                "complexity_profile": {
                    "objective_count": obj,
                    "decision_density": dec,
                    "statefulness": "low" if level_id == "foundation-gaps" else "medium",
                    "ambiguity": amb,
                    "verification_difficulty": ver,
                    "scaffolding_strength": "high" if level_id == "foundation-gaps" else "low",
                    "delivery_scope": "narrow" if level_id == "foundation-gaps" else "timed",
                },
            }
            exercises.append(ex)
        for idx in range(2):
            ex_id = f"{level_id}-challenge-{idx+1}"
            ex = {
                "id": ex_id,
                "level_id": level_id,
                "mode": "interview",
                "type": "system-design",
                "track": "interview",
                "is_challenge": True,
                "complexity_profile": {
                    "objective_count": "high",
                    "decision_density": "high",
                    "statefulness": "medium",
                    "ambiguity": "high",
                    "verification_difficulty": "high",
                    "scaffolding_strength": "low",
                    "delivery_scope": "timed",
                },
            }
            exercises.append(ex)

    write_json(workspace / "planning" / "exercise_catalog.json", {"exercises": exercises})

    for ex in exercises:
        if ex["mode"] != "coding":
            continue
        prompt_path = workspace / "exercises" / f"level-{ex['level_id']}" / ex["id"] / "prompt.md"
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(
            "\n".join(
                [
                    "## Function Contract",
                    "## Input Schema",
                    "## Output Schema",
                    "## Metric Definitions",
                    "## Edge Cases",
                    "## Constraints",
                    "## Acceptance Criteria",
                ]
            ),
            encoding="utf-8",
        )

    result = run_script("validate_generation.py", str(workspace))
    assert "Generation validation passed" in result.stdout


def test_validate_generation_rejects_quota_mismatch(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))
    write_json(
        workspace / "analysis" / "current" / "exercise_mode_decision.json",
        {
            "include_coding": True,
            "include_debugging": True,
            "mode_mix": {"coding": 0.6, "debugging": 0.2, "interview": 0.2},
            "level_quota": {"core_per_level": 3, "challenge_per_level": 2, "enforce": True},
        },
    )
    write_json(workspace / "analysis" / "current" / "cv_profile.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "market_demand.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "gap_analysis.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "level_map.json", build_level_map())
    write_json(workspace / "planning" / "learning_plan.json", build_learning_plan())
    write_json(workspace / "planning" / "exercise_catalog.json", build_catalog())

    result = run_script_allow_failure("validate_generation.py", str(workspace))
    assert result.returncode != 0
    error_text = result.stderr or result.stdout
    assert "Level quota mismatch" in error_text


def test_validate_generation_passes_with_dynamic_level_quota(tmp_path: Path) -> None:
    workspace = tmp_path / "learning_workspace"
    run_script("init_learning_workspace.py", str(workspace))
    write_json(workspace / "analysis" / "current" / "cv_profile.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "market_demand.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "gap_analysis.json", {"ok": True})
    write_json(workspace / "analysis" / "current" / "level_map.json", build_level_map())
    write_json(workspace / "planning" / "learning_plan.json", build_learning_plan())
    write_json(
        workspace / "analysis" / "current" / "exercise_mode_decision.json",
        {
            "include_coding": False,
            "include_debugging": False,
            "mode_mix": {"interview": 1.0},
            "level_quota": {
                "enforce": True,
                "min_total_per_level": 2,
                "max_total_per_level": 5,
            },
        },
    )

    exercises = []
    for level_id, total, profile in [
        ("foundation-gaps", 2, {"objective_count": "low", "decision_density": "low", "ambiguity": "low", "verification_difficulty": "low"}),
        ("system-rigor", 5, {"objective_count": "medium", "decision_density": "high", "ambiguity": "medium", "verification_difficulty": "high"}),
        ("interview-readiness", 4, {"objective_count": "medium", "decision_density": "high", "ambiguity": "high", "verification_difficulty": "high"}),
    ]:
        for idx in range(total):
            exercises.append(
                {
                    "id": f"{level_id}-dyn-{idx+1}",
                    "level_id": level_id,
                    "mode": "interview",
                    "type": "behavioral",
                    "track": "interview",
                    "is_challenge": False,
                    "complexity_profile": {
                        **profile,
                        "statefulness": "medium",
                        "scaffolding_strength": "low",
                        "delivery_scope": "timed",
                    },
                }
            )
    write_json(workspace / "planning" / "exercise_catalog.json", {"exercises": exercises})

    result = run_script("validate_generation.py", str(workspace))
    assert "Generation validation passed" in result.stdout


def test_static_validation_and_docs_consistency() -> None:
    script_paths = sorted(str(path) for path in SCRIPTS_DIR.glob("*.py"))
    env = os.environ.copy()
    with tempfile.TemporaryDirectory() as pycache_prefix:
        env["PYTHONPYCACHEPREFIX"] = pycache_prefix
        subprocess.run([sys.executable, "-m", "py_compile", *script_paths], check=True, env=env)

    for path in SCRIPTS_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert "from openai" not in text
        assert "import openai" not in text
        assert "OpenAI(" not in text
        assert "OPENAI_API_KEY" not in text

    skill_md = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    schemas_md = (SKILL_ROOT / "references" / "schemas.md").read_text(encoding="utf-8")
    interaction_md = (SKILL_ROOT / "references" / "interaction-pattern.md").read_text(encoding="utf-8")

    for required in [
        "analysis/current/level_map.json",
        "planning/learning_plan.json",
        "planning/exercise_catalog.json",
        "planning/progress_map.json",
        "reviews.jsonl",
        "implementation_target",
        "user_responsibility",
        "test_strategy",
        "test_edit_policy",
        "verification_flow",
        "complexity_profile",
        "complexity_constraints",
        "language_focus",
        "language_selection_rationale",
        "prerequisite_support_mode",
        "readiness_expectation",
        "fit_rationale",
    ]:
        assert required in skill_md
        assert required in schemas_md or required in interaction_md

    assert "analysis/plan.json" not in skill_md
    assert "feedback.jsonl" not in schemas_md
