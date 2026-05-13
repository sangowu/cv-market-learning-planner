---
name: cv-market-learning-planner
description: Use when the user wants a CV-aware adaptive learning system that reads a CV, compares it against current global market demand, generates HTML learning plans and scoped coding exercises, and maintains progress records, history, and evolving follow-up tasks.
---

# CV Market Learning Planner

Use this skill when the goal is to turn a CV plus current global market demand into an evolving practice system.

## What this skill does

- Reads a CV and extracts current strengths, experience signals, and likely skill gaps.
- Analyzes current global job-market demand using Codex live browsing.
- Produces a versioned learning workspace with HTML plan pages and exercise assets.
- Uses four fixed abstract containers:
  - `foundation-gaps`
  - `independent-implementation`
  - `system-rigor`
  - `interview-readiness`
- Generates the actual content of each level dynamically from CV evidence and market demand.
- Treats the four levels as complexity profiles rather than fixed topic tracks.
- Produces both coding exercises and interview-oriented exercises with one shared exercise model.
- Stores exercise history, structured reviews, and progress statistics.
- Stores structured review history in `progress/reviews.jsonl`.

## Trigger conditions

Use this skill when the user asks for any of the following:

- a skill-gap analysis based on their CV and the job market
- an adaptive study plan or learning roadmap
- HTML plan pages plus concrete exercises
- interview practice derived from CV, market demand, or project evidence
- exercise regeneration after reviewing completed work
- progress tracking, history retention, or stats for study work

## Required workflow

1. Read the CV or CV-derived source material first.
2. Browse the web for current market demand unless the user explicitly restricts sources.
3. Write the analysis artifacts before generating exercises:
   - `analysis/current/cv_profile.json`
   - `analysis/current/market_demand.json`
   - `analysis/current/gap_analysis.json`
   - `analysis/current/level_map.json`
4. Write the planning artifacts:
   - `planning/learning_plan.json`
   - `planning/exercise_catalog.json`
   - update `planning/progress_map.json` if needed
5. Generate the exercise directories and resource files.
6. Render the HTML plan pages and summary reports.
7. When the user submits results, preserve originals and append structured reviews instead of overwriting history.

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
- Infer the learner-facing content language from CV language evidence and user prompt language.
- Use the strongest CV-supported language as the default output language for learner-facing artifacts when no explicit user language preference is provided.
- Keep learner-facing language consistent across `planning/learning_plan.json` summaries, exercise prompts, review notes, and rendered plan/report pages for a single generation cycle.
- If the user explicitly requests a specific output language, follow that request and record the rationale in planning artifacts.
- For `foundation-gaps` coding exercises, choose the primary language from the language evidence already present in `analysis/current/cv_profile.json`.
- Within the CV-detected languages, prefer the most foundational and easiest-to-verify language track first rather than the most market-impressive or most engineering-heavy track.
- Do not introduce a new language for `foundation-gaps` unless the CV lacks any meaningful coding-language evidence.
- Keep `foundation-gaps` coding exercises single-language unless the CV evidence specifically justifies a multi-language task.
- Treat prerequisites as dependency contracts, not label lists.
- For each prerequisite, decide whether the learner needs `teach`, `remind`, or `assume` support based on the level, CV evidence, and task complexity.
- If prerequisite support mode is `teach`, expand prerequisites into short learnability units that explain what the learner needs, why it matters here, the minimum operational understanding, and a self-check.
- If a prerequisite cannot be explained briefly and concretely for the current level, simplify or split the exercise instead of leaving the prerequisite as an unexplained dependency.
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
  - `prerequisites`
  - `prerequisite_units`
  - `prerequisite_support_mode`
  - `readiness_expectation`
  - `fit_rationale`
  - `evaluation_method`
  - `expected_output_kind`
  - `verification`
  - `deliverables`
- Validate the exercise against level complexity semantics, not against hard-coded topic rules.
- Before generating assets, run an automatic level-fit check against each level's allowed complexity ranges and fail fast on mismatches.
- For coding exercises, also validate that the chosen language focus is justified by CV language evidence and by the level intent.
- For `foundation-gaps` coding exercises, fail generation if `language_focus` is not in the top CV language-evidence set (unless CV language evidence is missing entirely, where fallback is allowed).
- For `foundation-gaps` coding exercises, enforce `prerequisite_support_mode=teach` and require at least one structured `prerequisite_unit` with `concept`, `why_it_matters_here`, `quick_explanation`, and `self_check`.
- For normal coding exercises, validate that deliverables and verification instructions do not make the learner responsible for creating or extending the main tests.
- Recommended support levels:
  - `guided`
  - `scaffolded`
  - `sparse`
  - `from-scratch`
- Every generated coding file should include a complete exercise header at the top, similar to a LeetCode-style prompt, including goal, task, constraints or hints, deliverables, evaluation method, expected output, and verification notes.

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
