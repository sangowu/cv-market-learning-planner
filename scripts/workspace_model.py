from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ABSTRACT_LEVELS = [
    {
        "id": "foundation-gaps",
        "label": "Foundation Gaps",
        "purpose": "Resolve missing fundamentals that limit reliable independent execution.",
        "default_support_level": "guided",
        "complexity_profile": {
            "objective_count": "low",
            "decision_density": "low",
            "statefulness": "low",
            "ambiguity": "low",
            "verification_difficulty": "low",
            "scaffolding_strength": "high",
            "delivery_scope": "narrow",
        },
        "complexity_constraints": {
            "objective_count": ["low"],
            "decision_density": ["low"],
            "statefulness": ["low"],
            "ambiguity": ["low"],
            "verification_difficulty": ["low"],
            "scaffolding_strength": ["high"],
            "delivery_scope": ["narrow", "contained"],
        },
    },
    {
        "id": "independent-implementation",
        "label": "Independent Implementation",
        "purpose": "Build end-to-end tasks with lighter scaffolding and stronger ownership.",
        "default_support_level": "scaffolded",
        "complexity_profile": {
            "objective_count": "medium",
            "decision_density": "medium",
            "statefulness": "medium",
            "ambiguity": "medium",
            "verification_difficulty": "medium",
            "scaffolding_strength": "medium",
            "delivery_scope": "contained",
        },
        "complexity_constraints": {
            "objective_count": ["low", "medium"],
            "decision_density": ["medium"],
            "statefulness": ["low", "medium"],
            "ambiguity": ["low", "medium"],
            "verification_difficulty": ["medium"],
            "scaffolding_strength": ["medium", "high"],
            "delivery_scope": ["contained", "broad"],
        },
    },
    {
        "id": "system-rigor",
        "label": "System Rigor",
        "purpose": "Increase debugging, testing, evaluation, and production-quality discipline.",
        "default_support_level": "sparse",
        "complexity_profile": {
            "objective_count": "medium",
            "decision_density": "high",
            "statefulness": "medium",
            "ambiguity": "medium",
            "verification_difficulty": "high",
            "scaffolding_strength": "low",
            "delivery_scope": "broad",
        },
        "complexity_constraints": {
            "objective_count": ["medium", "high"],
            "decision_density": ["medium", "high"],
            "statefulness": ["medium", "high"],
            "ambiguity": ["medium", "high"],
            "verification_difficulty": ["high"],
            "scaffolding_strength": ["low", "medium"],
            "delivery_scope": ["broad", "contained"],
        },
    },
    {
        "id": "interview-readiness",
        "label": "Interview Readiness",
        "purpose": "Practice timed explanation, live problem-solving, and challenge handling.",
        "default_support_level": "from-scratch",
        "complexity_profile": {
            "objective_count": "medium",
            "decision_density": "medium",
            "statefulness": "medium",
            "ambiguity": "medium",
            "verification_difficulty": "medium",
            "scaffolding_strength": "low",
            "delivery_scope": "timed",
        },
        "complexity_constraints": {
            "objective_count": ["low", "medium"],
            "decision_density": ["medium", "high"],
            "statefulness": ["low", "medium"],
            "ambiguity": ["medium", "high"],
            "verification_difficulty": ["medium", "high"],
            "scaffolding_strength": ["low"],
            "delivery_scope": ["timed"],
        },
    },
]

CURRENT_ANALYSIS_FILES = [
    "cv_profile.json",
    "market_demand.json",
    "gap_analysis.json",
    "level_map.json",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_json_if_missing(path: Path, payload: object) -> None:
    if not path.exists():
        write_json(path, payload)


def write_text_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def history_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def default_level_map() -> dict:
    return {
        "levels": [
            {
                "id": level["id"],
                "label": level["label"],
                "active": False,
                "priority": 0,
                "cv_evidence": [],
                "market_evidence": [],
                "why_now": "Pending Codex analysis.",
                "depends_on": [],
                "complexity_profile": level["complexity_profile"],
                "complexity_constraints": level["complexity_constraints"],
            }
            for level in ABSTRACT_LEVELS
        ]
    }


def default_learning_plan() -> dict:
    return {
        "title": "Adaptive Learning Plan",
        "summary": "Pending Codex analysis.",
        "active_levels": [],
        "level_order": [],
        "sequencing": [],
    }


def default_exercise_catalog() -> dict:
    return {"exercises": []}


def default_progress_map() -> dict:
    return {
        "levels": {
            level["id"]: {
                "status": "pending",
                "exercise_ids": [],
                "completed_exercises": [],
                "last_reviewed_at": None,
            }
            for level in ABSTRACT_LEVELS
        },
        "exercises": {},
    }


def default_stats() -> dict:
    return {
        "total_submissions": 0,
        "total_reviews": 0,
        "completed_exercises": 0,
        "latest_exercise": None,
        "last_review_status": None,
        "common_issue_tags": [],
    }
