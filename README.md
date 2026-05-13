# CV Market Learning Planner

A Codex skill that turns CV evidence plus current market demand into a structured learning workspace:

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

No OpenAI key is required for deterministic scripts in this skill.

## Installation

Install this repository under your Codex skills directory as `cv-market-learning-planner`.

Typical Windows path:

```powershell
cd C:\Users\40568\.codex\skills
git clone https://github.com/sangowu/cv-market-learning-planner.git cv-market-learning-planner
```

Typical macOS/Linux path:

```bash
cd ~/.codex/skills
git clone https://github.com/sangowu/cv-market-learning-planner.git cv-market-learning-planner
```

After installation, start a new Codex session so the skill is loaded.

## Natural-Language Trigger

After the skill is installed and loaded, users can trigger it directly with natural language, for example:

```text
Based on <path-to-cv-file> and the current global <target-role> job market, generate an adaptive interview-focused learning plan.
```

If auto-trigger does not fire, explicitly mention the skill:

```text
Use the cv-market-learning-planner skill. Based on <path-to-cv-file> and the current global <target-role> job market, generate an adaptive interview-focused learning plan.
```

## Quick Start

From this directory:

```powershell
python scripts/init_learning_workspace.py
python scripts/run_cycle.py .\learning_workspace .\path\to\cv.docx
```

Then have Codex complete:

1. `analysis/current/*.json` artifacts
2. `planning/learning_plan.json`
3. `planning/exercise_catalog.json`

Render pages and scaffold exercises:

```powershell
python scripts/generate_exercise_assets.py .\learning_workspace\planning\exercise_catalog.json .\learning_workspace
python scripts/render_plan_pages.py .\learning_workspace\planning\learning_plan.json .\learning_workspace\planning\exercise_catalog.json .\learning_workspace\analysis\current\level_map.json .\learning_workspace\plan
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
