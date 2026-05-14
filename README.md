# CV Market Learning Planner

A multi-agent compatible skill that turns CV evidence plus current market demand into a structured learning workspace:

- gap analysis artifacts
- level-based learning plan pages (HTML)
- scoped coding and interview exercises
- append-only submission/review history
- progress summaries and stats

## What It Generates

Workspace structure:

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

Primary outputs:

- `analysis/current/cv_profile.json`
- `analysis/current/market_demand.json`
- `analysis/current/gap_analysis.json`
- `analysis/current/level_map.json`
- `planning/learning_plan.json`
- `planning/exercise_catalog.json`
- `plan/*.html`
- `reports/latest-summary.html`

## Requirements

- Python 3.11+ (tested on 3.13)
- `pytest` for running tests

## Installation

Install this repository into a skills/plugins directory that your agent runtime can load from, using the folder name `cv-market-learning-planner`.

Example (Windows):

```powershell
cd <agent-home>\skills
git clone https://github.com/sangowu/cv-market-learning-planner.git cv-market-learning-planner
```

Example (macOS/Linux):

```bash
cd <agent-home>/skills
git clone https://github.com/sangowu/cv-market-learning-planner.git cv-market-learning-planner
```

After installation, start a new agent session (or reload skills/plugins) so the runtime can discover and load this skill.

## Quick Start (Natural Language)

After installation, provide:

- `<path-to-cv-file>`
- `<target-role>`

Then trigger with a single prompt:

```text
Based on <path-to-cv-file> and the current global <target-role> job market, generate an adaptive interview-focused learning plan.
```

Advanced prompt example:

```text
Please generate an interview-focused adaptive learning plan based on <cv-placeholder> and the current global <target-role-placeholder> job market for <target-seniority>. Include coding exercises, debugging exercises, system design/project defense exercises, and progress tracking. Coding difficulty should progress from easy to hard by level, with 3 problems per level plus 2 challenge problems (beyond the learner's current level or project depth, but still partially knowledge-related). For coding exercises, include prerequisite knowledge explanations and hints to support solving and review.
```

## Advanced: Scripted Workflow (Optional)

Use this only for maintainer debugging, offline reproduction, or custom pipeline runs.

From this directory:

```powershell
python scripts/init_learning_workspace.py
python scripts/run_cycle.py .\learning_workspace .\path\to\cv.docx
```

Then have your agent complete:

1. `analysis/current/*.json` artifacts
2. `planning/learning_plan.json`
3. `planning/exercise_catalog.json`

Render pages and scaffold exercises:

```powershell
python scripts/generate_exercise_assets.py .\learning_workspace\planning\exercise_catalog.json .\learning_workspace
python scripts/render_plan_pages.py .\learning_workspace\planning\learning_plan.json .\learning_workspace\planning\exercise_catalog.json .\learning_workspace\analysis\current\level_map.json .\learning_workspace\plan
```

## Exercise Quota (Per Level)

Configure exercise count policy in `analysis/current/exercise_mode_decision.json` via `level_quota`.

Recommended dynamic mode (difficulty-aware):

```json
{
  "level_quota": {
    "enforce": true,
    "min_total_per_level": 2,
    "max_total_per_level": 5
  }
}
```

With this mode, active levels receive different total exercise counts based on level complexity (higher difficulty gets more exercises, lower difficulty gets fewer), constrained to the configured min/max range.

Legacy fixed-split mode is still supported:

```json
{
  "level_quota": {
    "enforce": true,
    "core_per_level": 3,
    "challenge_per_level": 2
  }
}
```

## Testing

```powershell
python -m pytest -q
```

## Cross-Platform Notes

- Python scripts are cross-platform.
- `run_learning_tool.ps1` is a Windows convenience wrapper generated into each workspace.
- On Linux/macOS, run Python script entry points directly.

## Repository Hygiene

This project ignores Python caches and pytest caches via `.gitignore`.
