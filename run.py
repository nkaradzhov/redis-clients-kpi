"""Entry point: read config.yaml, collect stats, write the site/ directory."""

import os
import time

from collect import collect, load_config
from render import render

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    cfg = load_config(os.path.join(HERE, "config.yaml"))
    print(f"Reporting period: {cfg['quarter_label']} "
          f"({cfg['start_date']:%Y-%m-%d} to {cfg['end_date']:%Y-%m-%d})")

    t0 = time.perf_counter()
    repos = collect(cfg)
    print(f"Collected {len(repos)} repo(s) in {time.perf_counter() - t0:.1f}s")

    render(cfg, repos, out_dir=os.path.join(HERE, "site"), data_dir=os.path.join(HERE, "data"))
    print("Wrote site/index.html, site/data.json, and data/latest.json")


if __name__ == "__main__":
    main()
