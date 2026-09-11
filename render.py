"""Render collected KPI data as a static HTML page."""

import html
import json
import os
from datetime import datetime, timezone

import pandas as pd
from jinja2 import Environment, FileSystemLoader

HOUR_COLUMNS = ["Unanswered for", "Time to first response", "Time to close"]


def table(df, drop=()):
    """DataFrame -> safe HTML table with a clickable link column."""
    if df is None or not len(df):
        return None

    df = df.drop(columns=list(drop), errors="ignore").copy()

    for col in df.columns:
        if col in HOUR_COLUMNS:
            df[col] = df[col].map(lambda v: f"{v:.1f}" if pd.notna(v) else "—")
        elif col == "Created At":
            df[col] = df[col].map(lambda v: v.strftime("%Y-%m-%d") if pd.notna(v) else "—")
        elif df[col].dtype == object:
            df[col] = df[col].map(lambda v: html.escape(str(v)) if v is not None else "—")

    if "Link" in df.columns:
        number_col = next((c for c in df.columns if c.endswith("Number")), None)
        if number_col:
            df[number_col] = [
                f'<a href="{link}">#{num}</a>' for num, link in zip(df[number_col], df["Link"])
            ]
            df = df.drop(columns=["Link"])
        else:
            df["Link"] = df["Link"].map(lambda v: f'<a href="{v}">{v}</a>')

    return df.to_html(index=False, escape=False, border=0, classes="stats")


def render(cfg, repos, out_dir="site"):
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")),
        autoescape=False,
    )
    template = env.get_template("index.html.j2")

    sections = []
    for r in repos:
        opened = r["opened"]
        prs = opened["prs"]
        det = r["detractors"]
        sections.append({
            "name": r["name"],
            "summary": {k: ("—" if v is None else v) for k, v in r["summary"].items() if k != "Repository"},
            "counters": dict(opened["counters"]),
            "closed_counters": dict(r["closed"]["counters"]),
            "detractors": {
                "issues_unanswered": table(det["issues_unanswered"]),
                "issues_slow": table(det["issues_slow"].head(10)),
                "prs_unanswered": table(det["prs_unanswered"], drop=["Closed", "Time to close"]),
                "prs_slow": table(det["prs_slow"].head(10), drop=["Closed", "Time to close"]),
            },
            "issues": table(r["issues"]),
            "backlog": table(r["backlog"]),
            "open_prs": table(prs, drop=["Closed"]),
            "closed_prs": table(r["closed"]["prs"], drop=["Closed"]),
            "discussions": table(r["discussions"]),
            "docs_open": table(opened["docs_open"]),
            "docs_merged": opened["docs_merged"],
        })

    page = template.render(
        quarter=cfg["quarter_label"],
        start=cfg["start_date"].strftime("%b %d, %Y"),
        end=cfg["end_date"].strftime("%b %d, %Y"),
        generated=datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC"),
        threshold=cfg.get("slow_threshold_hours", 48),
        summary_table=table(pd.DataFrame([r["summary"] for r in repos])),
        repos=sections,
    )

    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(page)

    # machine-readable copy, for future consumers
    data = {
        "quarter": cfg["quarter_label"],
        "generated": datetime.now(timezone.utc).isoformat(),
        "summaries": [r["summary"] for r in repos],
    }
    with open(os.path.join(out_dir, "data.json"), "w") as f:
        json.dump(data, f, indent=2, default=str)
