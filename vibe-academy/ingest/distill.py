"""Distill raw/ Skool captures into organized markdown under content/.

Three outputs:
  1. content/discussions/  — one markdown file per community post
                             (title, author, date, body, comment tree).
  2. content/videos/index.md — every video URL found anywhere, with the
                             page it came from and its platform.
  3. content/industries/<vertical>/ — posts whose text matches that
                             vertical's keywords (config.json), copied in.
  4. content/skills/_worklist.md — posts/lessons authored by Alex (or
                             pinned/classroom material), sorted newest-first,
                             for the synthesis pass that writes the final
                             conglomerated skill docs.

This script is deliberately schema-tolerant: it walks the captured JSON
generically looking for post-shaped objects (dicts with name/title +
content/body + created_at-ish fields) instead of assuming Skool's exact
schema. After the first real ingest, tighten the extractors against what
raw/ actually contains.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
CFG = json.loads((HERE / "config.json").read_text())
RAW = (HERE / CFG["raw_dir"]).resolve()
CONTENT = (HERE / CFG["content_dir"]).resolve()

VIDEO_PAT = re.compile(
    r"https?://(?:www\.)?(youtube\.com/watch[^\s\"']+|youtu\.be/[^\s\"']+|"
    r"loom\.com/share/[^\s\"']+|vimeo\.com/[^\s\"']+|"
    r"[a-z0-9.-]*wistia\.(?:com|net)/[^\s\"']+|"
    r"video\.skool\.com/[^\s\"']+|stream\.mux\.com/[^\s\"']+)"
)

TEXT_KEYS = {"content", "body", "text", "post_content", "description"}
TITLE_KEYS = {"title", "name", "post_title"}
DATE_KEYS = {"created_at", "createdAt", "updated_at", "updatedAt"}


def walk(obj):
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def looks_like_post(d):
    if not isinstance(d, dict):
        return False
    keys = set(d.keys())
    return bool(keys & TITLE_KEYS) and bool(keys & TEXT_KEYS)


def get_first(d, keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:80] or "untitled"


def main():
    posts = {}   # slug -> {title, text, date, source, author}
    videos = {}  # url -> source page

    for f in sorted((RAW / "pages").glob("*.json")) + \
             sorted((RAW / "api").glob("*.json")):
        record = json.loads(f.read_text())
        payload = record.get("next_data") or record.get("body")
        if payload is None:
            continue
        blob = json.dumps(payload)
        for m in VIDEO_PAT.finditer(blob):
            videos.setdefault(m.group(0).rstrip("\\"), record.get("url", f.name))
        for node in walk(payload):
            if not looks_like_post(node):
                continue
            title = get_first(node, TITLE_KEYS)
            text = get_first(node, TEXT_KEYS)
            if len(text) < 40:  # skip nav items / stubs
                continue
            key = slugify(title)
            date = get_first(node, DATE_KEYS)
            author = ""
            for u in walk(node):
                if isinstance(u, dict) and {"first_name", "last_name"} <= set(u):
                    author = f"{u['first_name']} {u['last_name']}".strip()
                    break
            prev = posts.get(key)
            if not prev or len(text) > len(prev["text"]):
                posts[key] = {"title": title, "text": text, "date": date,
                              "author": author, "source": record.get("url", "")}

    # 1. discussions
    disc = CONTENT / "discussions"
    disc.mkdir(parents=True, exist_ok=True)
    for key, p in posts.items():
        md = (f"# {p['title']}\n\n"
              f"- **Author:** {p['author'] or 'unknown'}\n"
              f"- **Date:** {p['date'] or 'unknown'}\n"
              f"- **Source:** {p['source']}\n\n---\n\n{p['text']}\n")
        (disc / f"{key}.md").write_text(md)

    # 2. video index
    vid_dir = CONTENT / "videos"
    vid_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Video index\n"]
    for url, src in sorted(videos.items()):
        lines.append(f"- <{url}>  \n  found on: {src}")
    (vid_dir / "index.md").write_text("\n".join(lines) + "\n")

    # 3. industry classification
    for vertical, words in CFG["industry_keywords"].items():
        out = CONTENT / "industries" / vertical
        out.mkdir(parents=True, exist_ok=True)
        pat = re.compile("|".join(re.escape(w) for w in words), re.I)
        hits = {k: p for k, p in posts.items()
                if pat.search(p["title"] + " " + p["text"])}
        for key, p in hits.items():
            (out / f"{key}.md").write_text((disc / f"{key}.md").read_text())
        idx = [f"# {vertical} — {len(hits)} matched posts\n"]
        idx += [f"- [{p['title']}]({k}.md)" for k, p in sorted(hits.items())]
        (out / "_index.md").write_text("\n".join(idx) + "\n")

    # 4. skills worklist (Alex-authored + classroom, newest first)
    owner = CFG["owner"]["name"].lower()
    skill_items = [
        (k, p) for k, p in posts.items()
        if owner in p["author"].lower() or "classroom" in p["source"]
    ]
    skill_items.sort(key=lambda kp: kp[1]["date"], reverse=True)
    skills = CONTENT / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    wl = ["# Skills synthesis worklist",
          "",
          "Alex-authored posts and classroom lessons, newest first. The",
          "synthesis pass reads these top-down and writes one doc per skill",
          "into this directory. Rule: **the newest treatment of a topic",
          "wins**; when an older post contradicts it, record the change in",
          "the doc's 'Superseded approaches' section instead of blending.",
          ""]
    for k, p in skill_items:
        wl.append(f"- [ ] `{k}` — {p['title']} ({p['date'] or 'undated'})")
    (skills / "_worklist.md").write_text("\n".join(wl) + "\n")

    stamp = datetime.now(timezone.utc).isoformat()
    print(f"[{stamp}] distilled: {len(posts)} posts, {len(videos)} videos, "
          f"worklist of {len(skill_items)} Alex/classroom items")


if __name__ == "__main__":
    main()
