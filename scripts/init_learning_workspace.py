from __future__ import annotations

import sys
from pathlib import Path

from workspace_model import (
    ABSTRACT_LEVELS,
    CURRENT_ANALYSIS_FILES,
    default_exercise_catalog,
    default_learning_plan,
    default_level_map,
    default_progress_map,
    default_stats,
    ensure_dir,
    write_json_if_missing,
    write_text_if_missing,
)


def write_workspace_wrappers(root: Path) -> None:
    script_source_dir = Path(__file__).resolve().parent
    wrappers_dir = root / "scripts"
    ensure_dir(wrappers_dir)
    wrapper = wrappers_dir / "run_learning_tool.ps1"
    wrapper.write_text(
        (
            "param(\n"
            "  [Parameter(Mandatory=$true)][string]$Tool,\n"
            "  [Parameter(ValueFromRemainingArguments=$true)][string[]]$Args\n"
            ")\n\n"
            "$ErrorActionPreference = 'Stop'\n"
            "$workspace = Resolve-Path (Join-Path $PSScriptRoot '..')\n"
            f"$toolRoot = '{script_source_dir.as_posix()}'\n"
            "$toolMap = @{\n"
            "  'update-progress' = 'update_progress.py'\n"
            "  'generate-assets' = 'generate_exercise_assets.py'\n"
            "  'render-pages' = 'render_plan_pages.py'\n"
            "  'run-cycle' = 'run_cycle.py'\n"
            "  'validate-generation' = 'validate_generation.py'\n"
            "  'daily-status' = 'daily_status.py'\n"
            "  'generate-daily' = 'generate_daily_tasks.py'\n"
            "  'mark-daily' = 'mark_daily_task.py'\n"
            "}\n\n"
            "if (-not $toolMap.ContainsKey($Tool)) {\n"
            "  throw \"Unknown tool '$Tool'. Use one of: $($toolMap.Keys -join ', ')\"\n"
            "}\n\n"
            "$scriptPath = Join-Path $toolRoot $toolMap[$Tool]\n"
            "if (-not (Test-Path $scriptPath)) {\n"
            "  throw \"Missing script: $scriptPath\"\n"
            "}\n\n"
            "if ($Tool -eq 'run-cycle') {\n"
            "  & python $scriptPath $workspace @Args\n"
            "} elseif ($Tool -eq 'generate-assets') {\n"
            "  if ($Args.Count -eq 0) {\n"
            "    $catalog = Join-Path $workspace 'planning/exercise_catalog.json'\n"
            "    & python $scriptPath $catalog $workspace\n"
            "  } else {\n"
            "    & python $scriptPath @Args\n"
            "  }\n"
            "} else {\n"
            "  & python $scriptPath $workspace @Args\n"
            "}\n"
        ),
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) >= 2:
        root = Path(sys.argv[1]).resolve()
    else:
        root = (Path.cwd() / "learning_workspace").resolve()
    analysis_current = root / "analysis" / "current"
    analysis_history = root / "analysis" / "history"
    planning_dir = root / "planning"
    plan_dir = root / "plan"
    exercises_dir = root / "exercises"
    progress_dir = root / "progress"
    reports_dir = root / "reports"
    daily_dir = root / "daily"

    for path in [
        root / "input",
        analysis_current,
        analysis_history,
        planning_dir,
        plan_dir,
        exercises_dir,
        progress_dir,
        reports_dir,
        daily_dir,
    ]:
        ensure_dir(path)

    for level in ABSTRACT_LEVELS:
        ensure_dir(exercises_dir / f"level-{level['id']}")

    write_json_if_missing(analysis_current / CURRENT_ANALYSIS_FILES[0], {})
    write_json_if_missing(analysis_current / CURRENT_ANALYSIS_FILES[1], {})
    write_json_if_missing(analysis_current / CURRENT_ANALYSIS_FILES[2], {})
    write_json_if_missing(analysis_current / CURRENT_ANALYSIS_FILES[3], default_level_map())

    write_json_if_missing(planning_dir / "learning_plan.json", default_learning_plan())
    write_json_if_missing(planning_dir / "exercise_catalog.json", default_exercise_catalog())
    write_json_if_missing(planning_dir / "progress_map.json", default_progress_map())
    write_json_if_missing(daily_dir / "current.json", {"date": None, "status": "not_generated", "tasks": []})
    write_text_if_missing(daily_dir / "history.jsonl", "")

    write_text_if_missing(progress_dir / "submissions.jsonl", "")
    write_text_if_missing(progress_dir / "reviews.jsonl", "")
    write_json_if_missing(progress_dir / "stats.json", default_stats())
    write_text_if_missing(
        progress_dir / "progress.md",
        "# Progress\n\n## Current Focus\n- pending\n\n## Latest Review\n- pending\n\n## Level Status\n- pending\n",
    )

    write_text_if_missing(
        reports_dir / "latest-summary.html",
        "<!DOCTYPE html><html><body><p>Pending render.</p></body></html>\n",
    )
    write_workspace_wrappers(root)

    print(f"Initialized learning workspace at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
