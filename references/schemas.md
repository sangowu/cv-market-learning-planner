# Schemas

## Workspace layout

```text
learning_workspace/
  input/
    cv.docx
    cv_extracted.txt

  analysis/
    current/
      cv_profile.json
      market_demand.json
      gap_analysis.json
      level_map.json
      exercise_mode_decision.json
    history/
      <timestamp>_cv_profile.json
      <timestamp>_market_demand.json
      <timestamp>_gap_analysis.json
      <timestamp>_level_map.json
      <timestamp>_exercise_mode_decision.json

  planning/
    learning_plan.json
    exercise_catalog.json
    progress_map.json

  plan/
    index.html
    level-foundation-gaps.html
    level-independent-implementation.html
    level-system-rigor.html
    level-interview-readiness.html
    style.css

  exercises/
    level-foundation-gaps/
    level-independent-implementation/
    level-system-rigor/
    level-interview-readiness/

  progress/
    submissions.jsonl
    reviews.jsonl
    stats.json
    progress.md

  reports/
    latest-summary.html
    snapshot-<timestamp>.html
    next_steps.md
```

`analysis/current/` is the active working state.

`analysis/history/` is append-only and stores pre-regeneration snapshots.

## `analysis/current/level_map.json`

```json
{
  "levels": [
    {
      "id": "foundation-gaps",
      "label": "Foundation Gaps",
      "active": true,
      "priority": 10,
      "cv_evidence": ["Limited direct testing evidence in recent roles"],
      "market_evidence": ["Most applied AI roles expect test-backed Python delivery"],
      "why_now": "Core implementation gaps are blocking independent execution.",
      "depends_on": [],
      "complexity_profile": {
        "objective_count": "low",
        "decision_density": "low",
        "statefulness": "low",
        "ambiguity": "low",
        "verification_difficulty": "low",
        "scaffolding_strength": "high",
        "delivery_scope": "narrow"
      },
      "complexity_constraints": {
        "objective_count": ["low"],
        "decision_density": ["low"],
        "statefulness": ["low"],
        "ambiguity": ["low"],
        "verification_difficulty": ["low"],
        "scaffolding_strength": ["high"],
        "delivery_scope": ["narrow", "contained"]
      }
    }
  ]
}
```

Required level ids:

- `foundation-gaps`
- `independent-implementation`
- `system-rigor`
- `interview-readiness`

These ids are fixed containers only. Concrete skills and exercise themes must come from CV evidence and current market demand.

The level ids are stable, but each level is fundamentally a complexity profile rather than a fixed topic bucket.

`complexity_constraints` defines the allowed range for automatic level-fit validation.

## `planning/learning_plan.json`

```json
{
  "title": "Adaptive AI Engineer Learning Plan",
  "summary": "A level-driven plan generated from the CV and current global market demand.",
  "active_levels": [
    "foundation-gaps",
    "system-rigor",
    "interview-readiness"
  ],
  "level_order": [
    "foundation-gaps",
    "system-rigor",
    "interview-readiness"
  ],
  "sequencing": [
    {
      "label": "Phase 1",
      "summary": "Close Python and testing fluency gaps before timed interview work.",
      "level_ids": ["foundation-gaps", "system-rigor"]
    }
  ]
}
```

Ordering rule:

- dependency constraints first
- market priority second
- CV weakness severity third

## `analysis/current/exercise_mode_decision.json`

This file records model-driven decisions about exercise-track mix for the current user profile.

```json
{
  "include_coding": true,
  "include_debugging": true,
  "mode_mix": {
    "coding": 0.5,
    "debugging": 0.2,
    "interview": 0.3
  },
  "level_quota": {
    "enforce": true,
    "min_total_per_level": 2,
    "max_total_per_level": 5
  },
  "confidence": 0.82,
  "rationale": "Target role and CV project evidence both require implementation and debugging fluency.",
  "evidence": {
    "cv": ["Python delivery evidence across recent projects"],
    "market": ["Role postings require coding interviews and debugging rounds"]
  }
}
```

Rules:

- Mode inclusion should be decided by model reasoning, not hard-coded role-family allow/deny lists.
- If `include_coding` or `include_debugging` is `true`, rationale and evidence must explicitly justify why.
- `mode_mix` should sum close to 1.0 and reflect the planned emphasis for the current cycle.
- `level_quota` supports two modes:
  - dynamic total-per-level allocation (recommended): set `min_total_per_level` and `max_total_per_level`; the system allocates more exercises to higher-difficulty active levels.
  - legacy split allocation: set `core_per_level` and `challenge_per_level` to enforce exact per-level counts by challenge flag.

## `planning/exercise_catalog.json`

```json
{
  "exercises": [
    {
      "id": "foundation-two-sum-variant",
      "level_id": "foundation-gaps",
      "mode": "coding",
      "type": "python",
      "source": "question_bank",
      "category": "algorithm",
      "style": "leetcode",
      "difficulty": "easy",
      "topics": ["array", "hash-map"],
      "title": "Find Two Matching Skill Scores",
      "summary": "Practice hash-map lookup with a small deterministic function.",
      "prompt": "Implement the function and pass the generated tests.",
      "problem": "Given a list of integer scores and a target score, return the indices of two distinct scores whose sum equals the target. Return the smaller index first. Exactly one valid answer exists.",
      "examples": [
        {
          "input": "scores = [2, 7, 11, 15], target = 9",
          "output": "[0, 1]"
        }
      ],
      "constraints": [
        "2 <= len(scores) <= 10000",
        "-100000 <= scores[i] <= 100000",
        "Exactly one answer exists",
        "Do not use third-party libraries"
      ],
      "function_signature": "def two_sum(scores: list[int], target: int) -> list[int]:",
      "starter_code": "def two_sum(scores: list[int], target: int) -> list[int]:\n    raise NotImplementedError",
      "tests": [
        {
          "name": "basic_pair",
          "call": "two_sum([2, 7, 11, 15], 9)",
          "expected": [0, 1]
        }
      ],
      "hints": [
        "Track values you have already seen.",
        "For each value, check whether target - value was seen before."
      ],
      "expected_complexity": {
        "time": "O(n)",
        "space": "O(n)"
      },
      "resources": [],
      "implementation_target": "starter.py",
      "user_responsibility": "implementation-only",
      "test_strategy": "system-generated-visible",
      "test_edit_policy": "do-not-edit",
      "verification_flow": [
        "Run the generated tests before editing code.",
        "Modify only the implementation target unless the exercise explicitly says otherwise.",
        "Re-run the generated tests until they pass, then add the required short explanation."
      ],
      "language_focus": "python",
      "language_selection_rationale": "Python is strongly evidenced in the CV and is the most direct language for a first-stage fundamentals exercise.",
      "complexity_profile": {
        "objective_count": "low",
        "decision_density": "low",
        "statefulness": "low",
        "ambiguity": "low",
        "verification_difficulty": "low",
        "scaffolding_strength": "high",
        "delivery_scope": "narrow"
      },
      "learning_objectives": ["hash-map lookup", "edge-case tracing"],
      "fit_rationale": "Single-function exercise with direct verification and high scaffolding.",
      "evaluation_method": "Run the generated tests and explain the edge cases.",
      "expected_output_kind": "python-module",
      "verification": "Run pytest against the generated test file.",
      "deliverables": ["starter.py", "tests", "short design notes"],
      "support_level": "guided"
    }
  ]
}
```

Every exercise object must include:

- `id`
- `level_id`
- `mode`
- `type`
- `title`
- `summary`
- `prompt`
- `resources`
- `implementation_target`
- `user_responsibility`
- `test_strategy`
- `test_edit_policy`
- `verification_flow`
- `language_focus`
- `language_selection_rationale`
- `complexity_profile`
- `learning_objectives`
- `source`
- `category`
- `style`
- `difficulty`
- `topics`
- `fit_rationale`
- `evaluation_method`
- `expected_output_kind`
- `verification`
- `deliverables`

LeetCode-style coding exercises must also include:

- `problem`
- `examples`
- `constraints`
- `function_signature`
- `starter_code`
- `tests`
- `hints`
- `expected_complexity`

`complexity_profile` should describe the shape of the task rather than the topic. Recommended keys:

- `objective_count`
- `decision_density`
- `statefulness`
- `ambiguity`
- `verification_difficulty`
- `scaffolding_strength`
- `delivery_scope`

- `source` should identify where the task came from, such as `plan`, `question_bank`, `market_gap`, `project_gap`, or `generated_then_saved`.
- `category` should identify the task family, such as `python-basics`, `algorithm`, `sql`, `project-defense`, `debugging`, `system-design`, or `mock-interview`.
- `style` for normal coding fundamentals and classic algorithm tasks should be `leetcode`.
- `difficulty` should use `easy`, `medium`, or `hard`.
- `topics` should be a list of searchable practice tags.
- `language_focus` should identify the primary implementation language or language-family focus for the exercise.
- `language_selection_rationale` should explain why that language is the right fit based on CV evidence and current level intent.
- `implementation_target` should identify the file or code surface the learner is expected to edit.
- `user_responsibility` for normal coding exercises should default to `implementation-only`.
- `test_strategy` for normal coding exercises should default to `system-generated-visible`.
- `test_edit_policy` for normal coding exercises should default to `do-not-edit`.
- `verification_flow` should describe how the learner uses the pre-generated tests to iterate on the implementation.

Supported `mode` values:

- `coding`
- `interview`

Supported example `type` values:

- `python`
- `fastapi`
- `sql`
- `debugging`
- `llm-systems`
- `live-coding`
- `debugging-interview`
- `system-design`
- `project-defense`
- `cv-challenge`
- `behavioral`

Recommended `support_level` values:

- `guided`
- `scaffolded`
- `sparse`
- `from-scratch`

Resource policy:

- coding exercises generate `prompt.md`, starter code, tests, and a `submissions/` folder
- interview exercises generate `prompt.md`, `answer_notes.md`, `review_notes.md`, and a `submissions/` folder

Generated coding starter files must keep a full LeetCode-style header with difficulty, topics, problem statement, examples, constraints, function signature, expected complexity, hints, deliverables, evaluation method, expected output, and verification notes.

Default coding exercise responsibility:

- the system generates and maintains the main tests
- the learner edits the implementation target
- the learner may run visible tests but should not edit them unless the exercise explicitly trains test design

Exercise generation rule:

- decide the level-fit complexity profile first
- then instantiate a concrete topic from CV evidence, project evidence, supplied JD evidence, market demand, or the question bank
- for `foundation-gaps` coding exercises, anchor the task in a language already evidenced in the CV and prefer the most foundational option first
- do not create a separate prerequisite teaching module; if a task needs too much prior explanation, simplify or split it
- add newly generated reusable foundation, algorithm, or SQL tasks to `question_bank/` before using them as recurring daily practice
- set coding exercise responsibility fields so testing remains system-generated and learner effort stays focused on implementation
- reject generation if the exercise profile falls outside the level's `complexity_constraints`

## `daily/current.json`

```json
{
  "date": "2026-05-14",
  "status": "pending",
  "tasks": [
    {
      "id": "daily-20260514-001",
      "exercise_id": "foundation-two-sum-variant",
      "title": "Find Two Matching Skill Scores",
      "category": "algorithm",
      "difficulty": "easy",
      "status": "pending",
      "selected_from": "planning/exercise_catalog.json",
      "reason": "Keeps hash-map coding fluency active while the main plan focuses on project-defense work."
    }
  ]
}
```

Daily task rules:

- Daily tasks are selected from `planning/exercise_catalog.json`.
- Daily tasks may include project-plan tasks, Python/SQL basics, classic algorithm tasks, debugging prompts, or interview simulations.
- Missed daily tasks should not accumulate indefinitely; regenerate a fresh small set for the current date.
- Completion changes append to `daily/history.jsonl` and update `progress/stats.json`.

## `question_bank/*.jsonl`

Each JSONL record should be a reusable exercise seed. Coding basics and classic algorithms should follow the same LeetCode-style fields as catalog exercises:

```json
{"id":"algo-two-sum-easy","category":"algorithm","style":"leetcode","difficulty":"easy","topics":["array","hash-map"],"title":"Two Sum","problem":"Given an integer array nums and an integer target, return indices of the two numbers such that they add up to target.","examples":[{"input":"nums = [2,7,11,15], target = 9","output":"[0,1]"}],"constraints":["2 <= len(nums) <= 10000"],"function_signature":"def two_sum(nums: list[int], target: int) -> list[int]:","starter_code":"def two_sum(nums: list[int], target: int) -> list[int]:\n    raise NotImplementedError","tests":[{"name":"basic","call":"two_sum([2,7,11,15], 9)","expected":[0,1]}],"hints":["Use a hash map."],"expected_complexity":{"time":"O(n)","space":"O(n)"}}
```

Question bank rules:

- Prefer selecting basics and classic algorithms from the bank before generating new ones.
- If Codex generates a reusable foundation, SQL, or algorithm problem, append it to the relevant bank with a stable id.
- The bank stores reusable seeds; `planning/exercise_catalog.json` stores the active plan instances.

## `planning/progress_map.json`

```json
{
  "levels": {
    "foundation-gaps": {
      "status": "active",
      "exercise_ids": ["foundation-pipeline-debug"],
      "completed_exercises": [],
      "last_reviewed_at": null
    }
  },
  "exercises": {
    "foundation-pipeline-debug": {
      "level_id": "foundation-gaps",
      "mode": "coding",
      "status": "pending",
      "submission_count": 0,
      "review_count": 0,
      "last_submission": null,
      "last_review": null
    }
  }
}
```

## `progress/submissions.jsonl`

One JSON object per line:

```json
{"timestamp":"2026-05-11T14:10:00Z","exercise_id":"foundation-pipeline-debug","submission_path":"exercises/level-foundation-gaps/foundation-pipeline-debug/submissions/attempt_01.py","notes":"first pass"}
```

## `progress/reviews.jsonl`

```json
{"timestamp":"2026-05-11T14:15:00Z","exercise_id":"foundation-pipeline-debug","status":"retry","score":62.0,"strengths":["Clear decomposition"],"issues":["Missed null handling"],"issue_tags":["testing","edge-cases"],"next_action":"retry with explicit normalization tests","recommended_regeneration_mode":"targeted-refresh"}
```

Review status values:

- `completed`
- `retry`
- `advance`
- `blocked`

## `progress/stats.json`

```json
{
  "total_submissions": 3,
  "total_reviews": 3,
  "completed_exercises": 1,
  "latest_exercise": "foundation-pipeline-debug",
  "last_review_status": "retry",
  "common_issue_tags": ["testing", "edge-cases"]
}
```

## `progress/progress.md`

Human-readable summary:

```md
# Progress

## Current Focus
- testing
- edge-cases

## Latest Review
- 2026-05-11T14:15:00Z: `foundation-pipeline-debug` -> retry (retry with explicit normalization tests)

## Level Status
- foundation-gaps: active (0/1 complete)

## Completed
- 0 exercise(s)
```
