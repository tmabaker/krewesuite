# Ingest pipeline

## Run order

```bash
cd vibe-academy/ingest
pip install -r requirements.txt   # playwright/chromium is pre-installed in the cloud env
python ingest.py                  # login -> feed -> posts -> classroom -> raw/
python distill.py                 # raw/ -> content/ markdown + worklists
```

Then the **synthesis pass** (done by a Claude session, not a script):

1. Read `content/skills/_worklist.md` (Alex/classroom items, newest first).
2. Group items by skill/topic (e.g. "Claude Code setup", "OpenClaw agents",
   "PRD writing", "shipping/deploying", "app templates").
3. Write one doc per skill into `content/skills/` — the **most recent
   effective method as the main body**, with a short *Superseded
   approaches* section listing what changed over time and why.
4. Review `content/industries/*/_index.md` — the keyword classifier is a
   first cut; move misfiled posts, and pull the best per-vertical posts
   into a `PLAYBOOK.md` for each vertical.
5. Sync distilled trees to the consumption branches:

```bash
# from repo root, after committing on the ingest branch
git branch -f vibe-academy/skills HEAD
git branch -f vibe-academy/industries HEAD
git push -f origin vibe-academy/skills vibe-academy/industries
```

(Consumption branches track the ingest branch; they exist so a build
session can check out just the reference material by name.)

## Design notes

- **Playwright over raw API calls**: Skool's API is undocumented and
  changes; the login form + `__NEXT_DATA__` payloads are stable surfaces.
  Every `api.skool.com` response seen during browsing is captured anyway
  (`raw/api/`) as a bonus source.
- **Schema-tolerant distiller**: `distill.py` pattern-matches post-shaped
  objects rather than assuming exact field names. After the first real
  run, tighten the extractors against actual captures.
- **Videos**: URLs + source page are indexed in `content/videos/index.md`.
  Binaries are never committed. Transcript pulls (YouTube/Loom) are a
  follow-up once those domains are allowlisted — see `../NETWORK-SETUP.md`.
- **raw/ size**: raw captures are committed so the distiller can be
  iterated without re-scraping. If raw/ exceeds ~50 MB after a full
  ingest, prune `raw/api/` from git and keep only `raw/pages/`.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| curl/browser gets proxy 403 CONNECT | skool.com not in the environment network allowlist — see `../NETWORK-SETUP.md` |
| Login fails, no `auth_token` cookie | Password rotated (check `noit/skool`), or Skool added a captcha — run headed locally to inspect |
| Feed loop stops early | Skool changed pagination — rely on `scroll_to_bottom()` captures in `raw/api/` |
| Empty distill output | Schema drift — inspect a `raw/pages/post_*.json` and update `TEXT_KEYS`/`TITLE_KEYS` in distill.py |
