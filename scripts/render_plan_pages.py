from __future__ import annotations

import html
import json
import shutil
import sys
from pathlib import Path

ASSET_DIR = Path(__file__).resolve().parent.parent / "assets" / "roadmap-ui"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def group_exercises_by_level(catalog: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for exercise in catalog.get("exercises", []):
        grouped.setdefault(exercise["level_id"], []).append(exercise)
    return grouped


def level_lookup(level_map: dict) -> dict[str, dict]:
    return {level["id"]: level for level in level_map.get("levels", [])}


def render_resource_links(exercise: dict) -> str:
    links = []
    for resource in exercise.get("resources", []):
        label = html.escape(resource.get("label", resource.get("kind", "resource")))
        path = html.escape(resource["path"])
        links.append(f'<a href="../{path}">{label}</a>')
    return " | ".join(links) or "Pending resources"


def render_profile(profile: dict) -> str:
    if not profile:
        return "<li>Pending complexity profile.</li>"
    return "".join(
        f"<li><strong>{html.escape(key)}</strong>: {html.escape(str(value))}</li>"
        for key, value in profile.items()
    )


def render_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f"<li>{html.escape(empty_text)}</li>"
    return "".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_index(plan: dict, levels: dict[str, dict], exercises_by_level: dict[str, list[dict]]) -> str:
    cards = []
    ordered_level_ids = plan.get("level_order", [])
    for level_id in ordered_level_ids:
        level = levels.get(level_id, {})
        exercises = exercises_by_level.get(level_id, [])
        cards.append(
            f"""
            <article class="week-card">
              <span class="tag">{html.escape(level_id)}</span>
              <h3>{html.escape(level.get("label", level_id))}</h3>
              <p class="goal">{html.escape(level.get("why_now", "Pending rationale."))}</p>
              <p class="meta">Priority: {html.escape(str(level.get("priority", "n/a")))}</p>
              <p class="meta">Exercises: {len(exercises)}</p>
              <div class="cta-row">
                <a class="button" href="level-{html.escape(level_id)}.html">Open Level</a>
              </div>
            </article>
            """
        )
    sequencing = []
    for phase in plan.get("sequencing", []):
        sequencing.append(
            f"<li>{html.escape(phase.get('label', 'Phase'))}: {html.escape(phase.get('summary', ''))}</li>"
        )
    sequencing_html = "".join(sequencing) or "<li>Sequencing pending.</li>"
    active_levels = len(plan.get("active_levels", []))
    exercise_total = sum(len(items) for items in exercises_by_level.values())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(plan.get("title", "Adaptive Learning Plan"))}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">Adaptive Plan</span>
      <h1>{html.escape(plan.get("title", "Adaptive Learning Plan"))}</h1>
      <p>{html.escape(plan.get("summary", ""))}</p>
      <div class="summary-grid">
        <article class="card">
          <span class="tag">Active Levels</span>
          <h3>{active_levels}</h3>
          <p>Abstract level containers currently active for this CV and market snapshot.</p>
        </article>
        <article class="card">
          <span class="tag">Exercises</span>
          <h3>{exercise_total}</h3>
          <p>Unified coding and interview exercises linked to the active levels.</p>
        </article>
        <article class="card">
          <span class="tag">History</span>
          <h3>Versioned</h3>
          <p>Current analysis lives under `analysis/current` and prior snapshots under `analysis/history`.</p>
        </article>
      </div>
      <div class="cta-row">
        <a class="button secondary" href="../progress/progress.md">Open Progress</a>
        <a class="button secondary" href="../reports/latest-summary.html">Latest Summary</a>
      </div>
    </section>
    <section class="section-block">
      <h2>Level Order</h2>
      <p class="section-note">Dependency order first, then market priority and CV weakness severity.</p>
      <ul>{sequencing_html}</ul>
    </section>
    <section class="section-block">
      <h2>Active Levels</h2>
      <p class="section-note">Each page explains why the level is active and links its exercise assets.</p>
      <div class="grid">
        {"".join(cards) or '<article class="week-card"><h3>No active levels yet.</h3></article>'}
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_level_page(level: dict, exercises: list[dict]) -> str:
    exercise_cards = []
    for exercise in exercises:
        exercise_cards.append(
            f"""
            <article class="card">
              <span class="tag">{html.escape(exercise.get("mode", "exercise"))}</span>
              <h3>{html.escape(exercise["title"])}</h3>
              <p class="summary">{html.escape(exercise.get("summary", ""))}</p>
              <p class="meta">Type: {html.escape(exercise.get("type", ""))}</p>
              <p class="meta">Support: {html.escape(exercise.get("support_level", ""))}</p>
              <p class="meta">Evaluation: {html.escape(exercise.get("evaluation_method", ""))}</p>
              <p class="meta">Output: {html.escape(exercise.get("expected_output_kind", ""))}</p>
              <p class="meta">Verification: {html.escape(exercise.get("verification", ""))}</p>
              <p class="meta">Fit: {html.escape(exercise.get("fit_rationale", ""))}</p>
              <ul>{render_profile(exercise.get("complexity_profile", {}))}</ul>
              <div class="resource-links">{render_resource_links(exercise)}</div>
            </article>
            """
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(level.get("label", level["id"]))}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">{html.escape(level["id"])}</span>
      <h1>{html.escape(level.get("label", level["id"]))}</h1>
      <p>{html.escape(level.get("why_now", "Pending rationale."))}</p>
      <div class="cta-row">
        <a class="button" href="index.html">Back to Plan</a>
        <a class="button secondary" href="../progress/progress.md">Open Progress</a>
      </div>
    </section>
    <section class="section-block">
      <h2>CV Evidence</h2>
      <ul>{render_list(level.get("cv_evidence", []), "Pending CV evidence.")}</ul>
    </section>
    <section class="section-block">
      <h2>Market Evidence</h2>
      <ul>{render_list(level.get("market_evidence", []), "Pending market evidence.")}</ul>
    </section>
    <section class="section-block">
      <h2>Complexity Profile</h2>
      <ul>{render_profile(level.get("complexity_profile", {}))}</ul>
    </section>
    <section class="section-block">
      <h2>Exercises</h2>
      <div class="exercise-grid">
        {"".join(exercise_cards) or '<article class="card"><h3>No exercises yet.</h3></article>'}
      </div>
    </section>
  </main>
</body>
</html>
"""


def render_latest_summary(plan: dict, levels: dict[str, dict], exercises_by_level: dict[str, list[dict]]) -> str:
    sections = []
    for level_id in plan.get("level_order", []):
        level = levels.get(level_id, {})
        exercises = exercises_by_level.get(level_id, [])
        titles = "".join(f"<li>{html.escape(exercise['title'])}</li>" for exercise in exercises) or "<li>No exercises yet.</li>"
        sections.append(
            f"""
            <section class="section-block">
              <span class="tag">{html.escape(level_id)}</span>
              <h2>{html.escape(level.get("label", level_id))}</h2>
              <p class="section-note">{html.escape(level.get("why_now", "Pending rationale."))}</p>
              <ul>{titles}</ul>
            </section>
            """
        )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(plan.get("title", "Latest Summary"))}</title>
  <link rel="stylesheet" href="../plan/style.css">
</head>
<body>
  <main class="wrap">
    <section class="hero">
      <span class="eyebrow">Latest Summary</span>
      <h1>{html.escape(plan.get("title", "Adaptive Learning Plan"))}</h1>
      <p>{html.escape(plan.get("summary", ""))}</p>
      <div class="cta-row">
        <a class="button" href="../plan/index.html">Open Plan</a>
        <a class="button secondary" href="../progress/progress.md">Open Progress</a>
      </div>
    </section>
    {"".join(sections) or '<section class="section-block"><h2>No active levels yet.</h2></section>'}
  </main>
</body>
</html>
"""


def main() -> int:
    if len(sys.argv) < 5:
        print("Usage: python render_plan_pages.py <learning_plan_json> <exercise_catalog_json> <level_map_json> <plan_dir>")
        return 1

    plan_path = Path(sys.argv[1]).resolve()
    catalog_path = Path(sys.argv[2]).resolve()
    level_map_path = Path(sys.argv[3]).resolve()
    plan_dir = Path(sys.argv[4]).resolve()
    reports_dir = plan_dir.parent / "reports"

    plan_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    style_src = ASSET_DIR / "style.css"
    if style_src.exists():
        shutil.copy2(style_src, plan_dir / "style.css")

    plan = read_json(plan_path)
    catalog = read_json(catalog_path)
    level_map = read_json(level_map_path)
    levels = level_lookup(level_map)
    exercises_by_level = group_exercises_by_level(catalog)

    (plan_dir / "index.html").write_text(render_index(plan, levels, exercises_by_level), encoding="utf-8")
    for level_id in plan.get("level_order", []):
        level = levels.get(level_id)
        if not level or not level.get("active", False):
            continue
        file_name = f"level-{level_id}.html"
        (plan_dir / file_name).write_text(
            render_level_page(level, exercises_by_level.get(level_id, [])),
            encoding="utf-8",
        )

    latest_summary = render_latest_summary(plan, levels, exercises_by_level)
    (reports_dir / "latest-summary.html").write_text(latest_summary, encoding="utf-8")
    snapshot_name = f"snapshot-{Path(plan_path).stat().st_mtime_ns}.html"
    (reports_dir / snapshot_name).write_text(latest_summary, encoding="utf-8")

    print(f"Rendered plan pages into {plan_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
