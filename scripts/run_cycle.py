from __future__ import annotations

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from workspace_model import (
    CURRENT_ANALYSIS_FILES,
    default_exercise_catalog,
    default_learning_plan,
    default_level_map,
    default_progress_map,
    ensure_dir,
    history_timestamp,
    read_json,
    write_json_if_missing,
)


SCRIPT_DIR = Path(__file__).resolve().parent


def extract_docx_text(path: Path) -> str:
    with ZipFile(path) as archive:
        data = archive.read("word/document.xml")
    root = ET.fromstring(data)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        texts = [node.text for node in para.findall(".//w:t", ns) if node.text]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return "\n".join(paragraphs)


def extract_cv_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return extract_docx_text(path)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported CV format: {suffix}. Use .docx, .txt, or .md.")


def ensure_workspace(workspace: Path) -> None:
    subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "init_learning_workspace.py"), str(workspace)],
        check=True,
    )


def snapshot_current_analysis(workspace: Path) -> list[Path]:
    current_dir = workspace / "analysis" / "current"
    history_dir = workspace / "analysis" / "history"
    ensure_dir(history_dir)
    existing = [current_dir / name for name in CURRENT_ANALYSIS_FILES if (current_dir / name).exists()]
    if not existing:
        return []

    stamp = history_timestamp()
    written: list[Path] = []
    for path in existing:
        target = history_dir / f"{stamp}_{path.name}"
        shutil.copy2(path, target)
        written.append(target)
    return written


def create_missing_placeholders(workspace: Path) -> None:
    current_dir = workspace / "analysis" / "current"
    planning_dir = workspace / "planning"
    write_json_if_missing(current_dir / "cv_profile.json", {})
    write_json_if_missing(current_dir / "market_demand.json", {})
    write_json_if_missing(current_dir / "gap_analysis.json", {})
    write_json_if_missing(current_dir / "level_map.json", default_level_map())
    write_json_if_missing(planning_dir / "learning_plan.json", default_learning_plan())
    write_json_if_missing(planning_dir / "exercise_catalog.json", default_exercise_catalog())
    write_json_if_missing(planning_dir / "progress_map.json", default_progress_map())


def write_next_steps(workspace: Path, snapshot_paths: list[Path]) -> None:
    reports_dir = workspace / "reports"
    ensure_dir(reports_dir)
    snapshot_note = (
        "\nPrevious analysis snapshots:\n"
        + "\n".join(f"- `analysis/history/{path.name}`" for path in snapshot_paths)
        if snapshot_paths
        else "\nNo previous analysis snapshot was needed."
    )
    (reports_dir / "next_steps.md").write_text(
        "# Next Steps\n\n"
        "This workspace has been initialized for a Codex-native regeneration cycle.\n"
        f"{snapshot_note}\n\n"
        "Codex should now:\n"
        "1. Read `input/cv_extracted.txt`\n"
        "2. Write `analysis/current/cv_profile.json`\n"
        "3. Browse the current global market and write `analysis/current/market_demand.json`\n"
        "4. Write `analysis/current/gap_analysis.json`\n"
        "5. Write `analysis/current/level_map.json`\n"
        "6. Write `planning/learning_plan.json`\n"
        "7. Write `planning/exercise_catalog.json`\n"
        "8. Update `planning/progress_map.json` if the exercise set changed\n"
        "9. Run `render_plan_pages.py` with the planning and level-map artifacts\n"
        "10. Run `generate_exercise_assets.py` with `planning/exercise_catalog.json`\n",
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python run_cycle.py <workspace_dir> <cv_path>  OR  python run_cycle.py <cv_path>")
        return 1

    if len(sys.argv) >= 3:
        workspace = Path(sys.argv[1]).resolve()
        cv_path = Path(sys.argv[2]).resolve()
    else:
        workspace = (Path.cwd() / "learning_workspace").resolve()
        cv_path = Path(sys.argv[1]).resolve()

    ensure_workspace(workspace)
    snapshot_paths = snapshot_current_analysis(workspace)

    input_dir = workspace / "input"
    ensure_dir(input_dir)
    target_cv_path = input_dir / cv_path.name
    if cv_path != target_cv_path:
        shutil.copy2(cv_path, target_cv_path)

    cv_text = extract_cv_text(cv_path)
    (input_dir / "cv_extracted.txt").write_text(cv_text, encoding="utf-8")

    create_missing_placeholders(workspace)
    write_next_steps(workspace, snapshot_paths)

    print(f"Prepared workspace for Codex-native analysis at {workspace}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
