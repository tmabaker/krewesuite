# Vibe Coding Academy — Knowledge Base

Personal reference mirror of [Alex Finn's Vibe Coding Academy](https://www.skool.com/vibe-coding-academy)
Skool community (discussions, classroom/videos, and skills), ingested and
distilled for use while building.

**This content is for Tammy's personal use as a paying member.** Do not
redistribute, publish, or expose it outside this private repo.

## Branch map

| Branch | Purpose |
|---|---|
| `claude/vibe-academy-content-ingest-x9uinc` | Integration branch: pipeline + full raw + organized content |
| `vibe-academy/skills` | **Distilled skills Alex covers** — conglomerated to the most recent, effective versions (older/superseded approaches noted in a changelog, not mixed in) |
| `vibe-academy/industries` | **Community-shared content by vertical** — legal, construction, auto dealerships, title companies, plus general MSP/end-customer material |

## Directory layout

```
vibe-academy/
  ingest/        Pipeline: login, harvest, distill (see ingest/README.md)
  raw/           Untouched JSON captures per page/post/lesson (source of truth)
  content/
    skills/      Alex's skills, one doc per skill, recency-first
    discussions/ Community threads as markdown (post + comment tree)
    videos/      Video index: title, URL, platform, transcript when available
    industries/  Classified community shares: legal/, construction/,
                 auto-dealership/, title-company/, general/
```

## How ingest works (short version)

1. Credentials come from AWS Secrets Manager `noit/skool` at runtime — never
   stored in this repo.
2. `ingest/ingest.py` logs into Skool with Playwright, walks the community
   feed, post detail pages, and the classroom, and dumps every page's
   embedded `__NEXT_DATA__` JSON plus captured `api.skool.com` responses
   into `raw/`.
3. `ingest/distill.py` converts raw captures into markdown under `content/`,
   classifies community posts by industry keywords, and builds worklists for
   the synthesis pass (a Claude session reads the worklists and writes the
   conglomerated skill docs — recency wins, superseded methods go to a
   changelog section).
4. The distilled `content/skills/` and `content/industries/` trees are then
   synced to their consumption branches.

## Prerequisite: network allowlist

The Claude cloud environment must be able to reach Skool. See
[`NETWORK-SETUP.md`](NETWORK-SETUP.md) — until those domains are added, the
pipeline cannot run from a cloud session.

## Re-running / updating

The community changes over time; re-ingest is idempotent (raw captures are
keyed by URL slug and overwritten). From a Claude session in this repo:
"run the vibe-ingest skill" — see `.claude/skills/vibe-ingest/SKILL.md`.
