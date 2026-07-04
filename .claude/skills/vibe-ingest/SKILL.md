---
name: vibe-ingest
description: Ingest and distill Alex Finn's Vibe Coding Academy Skool community (discussions, classroom videos, skills) into the vibe-academy/ knowledge base and its consumption branches. Use when asked to ingest, refresh, or re-sync Vibe Coding Academy / Skool content, or to run the skills synthesis pass.
---

# Vibe Academy ingest runbook

Everything lives under `vibe-academy/` on branch
`claude/vibe-academy-content-ingest-x9uinc` of tmabaker/krewesuite.
Read `vibe-academy/README.md` and `vibe-academy/ingest/README.md` first.

## Preconditions (check in this order)

1. **Network**: `curl -s -o /dev/null -w "%{http_code}" https://www.skool.com/`
   must NOT be a proxy 403/000. If blocked, stop and tell Tammy to apply
   `vibe-academy/NETWORK-SETUP.md` (claude.ai → Settings → Code
   environments → network policy). Do not try to route around the proxy.
2. **Credentials**: AWS Secrets Manager `noit/skool` (see the noit-ops
   skill in kreweconnect for the bootstrap pattern). Never print values —
   the loader in `ingest/secrets_loader.py` handles the shape quirk.

## Run

```bash
cd vibe-academy/ingest
pip install -r requirements.txt
python ingest.py        # ~all posts + classroom; use --max-posts 30 for a smoke test
python distill.py
```

## Synthesis pass (Claude does this, not a script)

Follow "synthesis pass" in `ingest/README.md`: read
`content/skills/_worklist.md` newest-first, write one doc per skill with
the current-best method up top and a "Superseded approaches" changelog;
sanity-check the industry classification and write per-vertical
`PLAYBOOK.md` files (legal, construction, auto-dealership, title-company).

## Publish

Commit on the ingest branch, push, then force-update the consumption
branches `vibe-academy/skills` and `vibe-academy/industries` per
`ingest/README.md`. This content is Tammy's paid membership material —
keep it in this private repo only.
