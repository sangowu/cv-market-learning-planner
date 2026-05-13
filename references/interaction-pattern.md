# Interaction Pattern

## Initial generation

1. Run `scripts/run_cycle.py` to initialize the workspace, preserve any prior `analysis/current` snapshot, and extract the CV text.
2. Read the CV.
3. Infer role family and seniority from the CV.
4. Browse for current global market demand using that inferred target profile.
5. Produce `analysis/current/cv_profile.json`, `analysis/current/market_demand.json`, `analysis/current/gap_analysis.json`, and `analysis/current/level_map.json`.
6. For each active level, decide the intended complexity profile before choosing the concrete exercise topic.
7. For `foundation-gaps` coding tasks, choose the primary language from CV language evidence and prefer the most foundational language track first.
8. Decide whether prerequisites for each exercise should be taught, reminded, or assumed, based on level semantics and learner evidence.
9. For coding exercises, set the learner responsibility to implementation-only and keep tests system-generated and visible by default.
10. Produce `planning/learning_plan.json` and `planning/exercise_catalog.json`.
11. Run `scripts/generate_exercise_assets.py`, which should fail fast if an exercise falls outside the owning level's complexity constraints.
12. Run `scripts/render_plan_pages.py`.

## After a user submission

1. Read the submitted code or artifact.
2. Evaluate it against the exercise target and evidence for the owning level.
3. Save the raw submission path in `submissions.jsonl`.
4. Save a structured review in `reviews.jsonl`.
5. Update `stats.json`, `progress.md`, and `planning/progress_map.json`.
6. Decide one of:
   - mark complete
   - create a retry task
   - generate a harder variant
   - move to the next active level

## Update principles

- Never delete old submissions or reviews.
- Prefer additive records over mutable records.
- If the plan needs to change, update `analysis/current/level_map.json`, `planning/learning_plan.json`, and `planning/exercise_catalog.json` before re-rendering pages.
- Re-evaluate level fit through complexity semantics first, not through hard-coded topic rules.
- Regenerate only affected exercise folders unless the full plan changed.
- Codex owns the adaptive reasoning. Local scripts only scaffold files, render HTML, preserve history, and update deterministic progress state.
