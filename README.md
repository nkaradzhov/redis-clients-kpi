# Redis Clients — Community KPI Dashboard

A daily report on how fast maintainers respond to community issues, pull
requests, and discussions in Redis client repositories. Published as a
GitHub Pages site, rebuilt every day by a GitHub Action.

## How it works

- `collect.py` walks each repository's issues, PRs, and discussions for the
  current fiscal quarter through the GitHub API. Items created by
  maintainers or bots are excluded. It measures time to first maintainer
  response, waiting times, interactions, and the untriaged backlog.
- `render.py` writes a static HTML page plus `data.json` into `site/`.
- `.github/workflows/update.yml` runs daily at 06:00 UTC, on every push to
  `main`, and on demand from the Actions tab. It deploys `site/` to
  GitHub Pages.

The reporting quarter is computed automatically (Redis fiscal year starts
Feb 1: Q1 Feb–Apr, Q2 May–Jul, Q3 Aug–Oct, Q4 Nov–Jan). Pin a fixed period
in `config.yaml` if you need one.

## Change the maintainer lists or repos

Edit [`config.yaml`](config.yaml) and open a pull request. That file holds
the repository list, the maintainer/external-maintainer/docs-team lists,
the optional fixed reporting period, and the slow-response threshold.

## Run locally

```sh
python -m venv .venv && .venv/bin/pip install -r requirements.txt
GITHUB_TOKEN=$(gh auth token) .venv/bin/python run.py
open site/index.html
```

A single repo takes ~25 seconds and ~200 API calls.

## One-time setup after pushing this repo to GitHub

1. Repository **Settings → Pages → Build and deployment → Source**:
   choose **GitHub Actions**.
2. Run the **Update KPI report** workflow once from the Actions tab
   (or just push to `main`).

No secrets are needed: the workflow uses the built-in `GITHUB_TOKEN`
(1,000 API requests/hour). With many large repos on the list you may need
a personal access token instead — set it as a repository secret and point
the workflow's `GITHUB_TOKEN` env entry at it.
