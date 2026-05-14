---
name: cv-market-learning-planner
description: Use when the user wants a CV/project/JD-aware adaptive learning system that compares evidence against current market demand, generates HTML plans, LeetCode-style practice, daily tasks, interview simulations, and progress history.
---

# CV Market Learning Planner

Use this skill when the goal is to turn a CV plus current global market demand into an evolving practice system.

## What this skill does

- Reads a CV plus optional local project repositories and extracts current strengths, evidence signals, and likely skill gaps.
- Analyzes current global job-market demand using Codex live browsing, or a supplied JD when provided.
- Produces a versioned learning workspace with HTML plan pages, exercise assets, daily tasks, and interview simulation files.
- Uses four fixed abstract containers:
  - `foundation-gaps`
  - `independent-implementation`
  - `system-rigor`
  - `interview-readiness`
- Generates the actual content of each level dynamically from CV evidence and market demand.
- Treats the four levels as complexity profiles rather than fixed topic tracks.
- Produces both coding exercises and interview-oriented exercises with one shared exercise model.
- Keeps coding exercises LeetCode-style by default: problem statement, examples, constraints, function signature, starter code, generated tests, hints, and expected complexity.
- Maintains a reusable question bank for basics, algorithms, SQL, project-defense, and market-derived tasks.
- Selects daily tasks from the shared exercise catalog instead of creating a separate exercise universe.
- Stores exercise history, structured reviews, daily completion records, and progress statistics.
- Stores structured review history in `progress/reviews.jsonl`.

## Trigger conditions

Use this skill when the user asks for any of the following:

- a skill-gap analysis based on their CV and the job market
- an adaptive study plan or learning roadmap
- HTML plan pages plus concrete exercises
- interview practice derived from CV, market demand, or project evidence
- exercise regeneration after reviewing completed work
- progress tracking, daily practice reminders, history retention, or stats for study work

## Required workflow

1. Read the CV or CV-derived source material first.
2. Inspect provided local project directories when available and extract implementation evidence from code, docs, tests, deployment files, and agent-skill files.
3. Browse the web for current market demand unless the user explicitly restricts sources, and incorporate supplied JD text when provided.
4. Write the analysis artifacts before generating exercises:
   - `analysis/current/cv_profile.json`
   - `analysis/current/market_demand.json`
   - `analysis/current/gap_analysis.json`
   - `analysis/current/level_map.json`
   - `analysis/current/exercise_mode_decision.json`
5. Write the planning artifacts:
   - `planning/learning_plan.json`
   - `planning/exercise_catalog.json`
   - update `planning/progress_map.json` if needed
6. Generate the exercise directories, daily-task state, and resource files.
7. Render the HTML plan pages and summary reports.
8. When the user submits results, preserve originals and append structured reviews instead of overwriting history.

## Workspace structure

Initialize the workspace with:

```text
learning_workspace/
  input/
  analysis/current/
  analysis/history/
  planning/
  plan/
  exercises/
  daily/
    current.json
    history.jsonl
  progress/
  reports/
```

Directory details and file schemas are in `references/schemas.md`.

## Deterministic helpers

- Run `scripts/init_learning_workspace.py` to scaffold a new workspace.
- Run `scripts/run_cycle.py` to initialize the workspace, extract the CV text, and snapshot prior current analysis before regeneration.
- Run `scripts/generate_exercise_assets.py` after producing `planning/exercise_catalog.json`.
- Run `scripts/render_plan_pages.py` after producing `planning/learning_plan.json`, `planning/exercise_catalog.json`, and `analysis/current/level_map.json`.
- Run `scripts/update_progress.py` after a submission is reviewed.
- Use `daily/current.json` for the active daily queue and `daily/history.jsonl` for append-only daily completion history.
- Run `scripts/daily_status.py` to check whether today has pending tasks.
- Run `scripts/generate_daily_tasks.py` to select today's low-pressure practice set from the shared catalog.
- Run `scripts/mark_daily_task.py` to mark one daily task as complete and append history.

## Bundled UI assets

- The legacy `exercise_roadmap` front-end has been merged into `assets/roadmap-ui/`.
- Generated plan pages should use those bundled assets through `render_plan_pages.py`.
- Treat the skill assets as the canonical HTML style source going forward.

## Reporting rule

- `reports/latest-summary.html` must include the overall summary plus every active level, its `why_now` rationale, and its exercise titles.
- `reports/snapshot-<timestamp>.html` must preserve rendered summary history for each regeneration.

## Market-analysis rules

- First analyze the CV. Infer likely role family and seniority from the CV before searching the market.
- Treat market demand as temporally unstable. Browse every time unless the user explicitly says not to.
- Use primary or high-signal sources when possible: official company job pages, major recruiting platforms, or credible market summaries.
- Keep the market scope global unless the user narrows it.
- Preserve `current_location` from the CV when present.
- Allow an explicit user-specified target region when provided.
- Do not generate a dedicated `region_strategy` planning dimension.

## Level-model rules

- The abstract level ids are fixed and may be hard-coded as containers.
- The contents, priorities, and exercise mix of those levels must be generated from the CV and market analysis.
- `analysis/current/level_map.json` must include:
  - `id`
  - `label`
  - `active`
  - `priority`
  - `cv_evidence`
  - `market_evidence`
  - `why_now`
  - `depends_on`
- Each level should also carry a complexity profile that describes the intended learning shape:
  - `objective_count`
  - `decision_density`
  - `statefulness`
  - `ambiguity`
  - `verification_difficulty`
  - `scaffolding_strength`
  - `delivery_scope`
- Each level should also define `complexity_constraints` so automatic level-fit validation can reject exercises that drift outside the intended range.
- Level ordering must respect dependencies first, then market priority, then CV weakness severity.

## Exercise-generation rules

- Let the exercise scope come from the gap analysis and level map.
- First decide the exercise complexity profile for the level, then instantiate the topic from CV evidence and market demand.
- Let the model decide whether coding/debugging tracks should be generated for the current user profile. Do not hard-code role-family allow/deny lists for exercise modes.
- Before exercise generation, write `analysis/current/exercise_mode_decision.json` with at least:
  - `include_coding`
  - `include_debugging`
  - `mode_mix`
  - `confidence`
  - `rationale`
  - `evidence`
- If coding/debugging is enabled by the model, the rationale must cite concrete CV evidence and/or target-role market evidence.
- If coding/debugging is disabled by the model, prioritize interview, case, communication, project-defense, and role-relevant decision exercises.
- Infer the learner-facing content language from CV language evidence and user prompt language.
- Use the strongest CV-supported language as the default output language for learner-facing artifacts when no explicit user language preference is provided.
- Keep learner-facing language consistent across `planning/learning_plan.json` summaries, exercise prompts, review notes, and rendered plan/report pages for a single generation cycle.
- If the user explicitly requests a specific output language, follow that request and record the rationale in planning artifacts.
- For `foundation-gaps` coding exercises, choose the primary language from the language evidence already present in `analysis/current/cv_profile.json`.
- Within the CV-detected languages, prefer the most foundational and easiest-to-verify language track first rather than the most market-impressive or most engineering-heavy track.
- Do not introduce a new language for `foundation-gaps` unless the CV lacks any meaningful coding-language evidence.
- Keep `foundation-gaps` coding exercises single-language unless the CV evidence specifically justifies a multi-language task.
- Do not generate a separate prerequisite teaching module. If a task needs too much explanation before starting, simplify or split the task.
- For coding fundamentals and classic algorithm practice, use LeetCode-style prompts by default.
- Foundation and algorithm tasks should come from the reusable `question_bank/` where possible. If the model creates a new foundation or algorithm task, save it into the question bank before using it again.
- Daily practice tasks must reference entries from `planning/exercise_catalog.json`; they are a scheduled view of the same exercise universe, not a second independent plan.
- Support both coding and interview exercise tracks as first-class outputs.
- For coding exercises, the system owns test generation and baseline verification scaffolding.
- Default coding-exercise responsibility is `implementation-only`: the learner should modify the implementation target, not design or expand the main test suite.
- Generated tests should remain visible and runnable in the workspace, but prompt text should tell the learner not to edit them unless the exercise is explicitly a testing-design exercise.
- Every exercise must include:
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
  - `problem` for LeetCode-style coding exercises
  - `examples` for LeetCode-style coding exercises
  - `constraints` for LeetCode-style coding exercises
  - `function_signature` for LeetCode-style coding exercises
  - `starter_code` for LeetCode-style coding exercises
  - `tests` for LeetCode-style coding exercises
  - `hints` for LeetCode-style coding exercises
  - `expected_complexity` for LeetCode-style coding exercises
  - `fit_rationale`
  - `evaluation_method`
  - `expected_output_kind`
  - `verification`
  - `deliverables`
- Validate the exercise against level complexity semantics, not against hard-coded topic rules.
- Before generating assets, run an automatic level-fit check against each level's allowed complexity ranges and fail fast on mismatches.
- For coding exercises, also validate that the chosen language focus is justified by CV language evidence and by the level intent.
- For `foundation-gaps` coding exercises, fail generation if `language_focus` is not in the top CV language-evidence set (unless CV language evidence is missing entirely, where fallback is allowed).
- For `foundation-gaps` coding exercises, enforce LeetCode-style fields and keep the problem small enough to solve through the prompt, examples, constraints, hints, and generated tests without a separate teaching unit.
- For normal coding exercises, validate that deliverables and verification instructions do not make the learner responsible for creating or extending the main tests.
- Recommended support levels:
  - `guided`
  - `scaffolded`
  - `sparse`
  - `from-scratch`
- Every generated coding file should include a complete LeetCode-style header at the top, including difficulty, topics, problem statement, examples, constraints, function signature, expected complexity, hints, deliverables, evaluation method, expected output, and verification notes.

## Progress-update rules

- Preserve raw submissions in append-only history.
- Preserve structured reviews in `progress/reviews.jsonl`.
- Update `planning/progress_map.json`, `progress/stats.json`, and `progress/progress.md` without deleting older records.

## Codex-native execution rule

- Do not require the user to configure `OPENAI_API_KEY` for normal skill usage.
- Do not call OpenAI directly from local scripts for CV analysis or market analysis.
- Codex should perform the reasoning and web-search steps itself, then write the resulting JSON artifacts locally.
- Local scripts are only for deterministic file preparation, HTML rendering, exercise scaffolding, history snapshotting, and progress bookkeeping.

## References

- Read `references/schemas.md` for file formats and directory semantics.
- Read `references/interaction-pattern.md` when updating exercises after user submissions.
