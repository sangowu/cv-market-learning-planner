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
    history/
      <timestamp>_cv_profile.json
      <timestamp>_market_demand.json
      <timestamp>_gap_analysis.json
      <timestamp>_level_map.json

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

## `planning/exercise_catalog.json`

```json
{
  "exercises": [
    {
      "id": "foundation-pipeline-debug",
      "level_id": "foundation-gaps",
      "mode": "coding",
      "type": "python",
      "title": "Repair a brittle ETL transform",
      "summary": "Practice reliable Python data shaping with explicit tests.",
      "prompt": "Implement the missing normalization and validation behavior.",
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
      "learning_objectives": ["dict grouping", "edge-case handling"],
      "prerequisites": ["basic Python collections"],
      "prerequisite_units": [
        {
          "concept": "Python sets",
          "why_it_matters_here": "The exercise needs quick deduplication and membership checks.",
          "quick_explanation": "A set stores unique items and supports average O(1) membership checks for typical cases.",
          "tiny_example": "required = {'python', 'sql'}",
          "self_check": "Why is a set a better fit than repeatedly scanning a list for this task?"
        }
      ],
      "prerequisite_support_mode": "teach",
      "readiness_expectation": "The learner should understand basic collection operations well enough to trace a small example by hand.",
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
- `prerequisites`
- `prerequisite_units`
- `prerequisite_support_mode`
- `readiness_expectation`
- `fit_rationale`
- `evaluation_method`
- `expected_output_kind`
- `verification`
- `deliverables`

`complexity_profile` should describe the shape of the task rather than the topic. Recommended keys:

- `objective_count`
- `decision_density`
- `statefulness`
- `ambiguity`
- `verification_difficulty`
- `scaffolding_strength`
- `delivery_scope`

- `language_focus` should identify the primary implementation language or language-family focus for the exercise.
- `language_selection_rationale` should explain why that language is the right fit based on CV evidence and current level intent.
- `implementation_target` should identify the file or code surface the learner is expected to edit.
- `user_responsibility` for normal coding exercises should default to `implementation-only`.
- `test_strategy` for normal coding exercises should default to `system-generated-visible`.
- `test_edit_policy` for normal coding exercises should default to `do-not-edit`.
- `verification_flow` should describe how the learner uses the pre-generated tests to iterate on the implementation.
- `prerequisite_support_mode` should be one of:
  - `teach`
  - `remind`
  - `assume`
- `readiness_expectation` should describe the minimum operational understanding required before the learner starts coding.
- `prerequisite_units` should be used when the prerequisite needs active teaching support rather than a short reminder.

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

Generated coding starter files must keep a full LeetCode-style header with goal, task, hints, deliverables, evaluation method, expected output, and verification notes.

Default coding exercise responsibility:

- the system generates and maintains the main tests
- the learner edits the implementation target
- the learner may run visible tests but should not edit them unless the exercise explicitly trains test design

Exercise generation rule:

- decide the level-fit complexity profile first
- then instantiate a concrete topic from CV evidence and market demand
- for `foundation-gaps` coding exercises, anchor the task in a language already evidenced in the CV and prefer the most foundational option first
- decide whether prerequisites should be taught, reminded, or assumed before finalizing the exercise text
- set coding exercise responsibility fields so testing remains system-generated and learner effort stays focused on implementation
- reject generation if the exercise profile falls outside the level's `complexity_constraints`

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
