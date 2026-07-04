"""Ingest the Vibe Coding Academy Skool community into raw/ captures.

Walks, in order:
  1. Community feed (all pages / infinite scroll) — collects post slugs.
  2. Every post detail page — full post body + comment tree.
  3. Classroom — every course, module, and lesson page (video links live
     in lesson __NEXT_DATA__).
  4. The about + members pages (light metadata).

Usage (from vibe-academy/ingest/):
    pip install -r requirements.txt
    python ingest.py [--max-posts N]

Requires: network access to skool.com (see ../NETWORK-SETUP.md) and AWS
credentials able to read the noit/skool secret.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from secrets_loader import get_skool_credentials
from skool_client import SkoolClient

HERE = Path(__file__).parent
CFG = json.loads((HERE / "config.json").read_text())
RAW = (HERE / CFG["raw_dir"]).resolve()


def find_strings(obj, pattern, out):
    """Recursively collect strings matching pattern from nested JSON."""
    if isinstance(obj, str):
        if re.search(pattern, obj):
            out.add(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            find_strings(v, pattern, out)
    elif isinstance(obj, list):
        for v in obj:
            find_strings(v, pattern, out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-posts", type=int, default=None,
                    help="cap post detail fetches (default: all)")
    args = ap.parse_args()

    slug = CFG["community_slug"]
    base = f"https://www.skool.com/{slug}"
    email, password = get_skool_credentials()

    with SkoolClient(RAW, page_delay=CFG["page_delay_seconds"]) as sk:
        print("logging in ...")
        sk.login(email, password)

        print("about page ...")
        sk.visit(f"{base}/about", "about")

        # 1. Feed: numbered pages first (Skool paginates with ?p=N), then a
        # scroll pass to trigger any API-driven pagination we can capture.
        post_slugs = set()
        for p in range(1, CFG["feed_max_pages"] + 1):
            url = base if p == 1 else f"{base}?p={p}"
            data = sk.visit(url, f"feed_p{p:03d}")
            found = set()
            # Post URLs look like /{slug}/{post-slug}; harvest every
            # community-relative path that isn't a known section.
            if data:
                find_strings(data, rf"^/{re.escape(slug)}/[a-z0-9][a-z0-9-]*$",
                             found)
            before = len(post_slugs)
            sections = {"about", "classroom", "calendar", "members",
                        "leaderboards", "settings"}
            for path in found:
                tail = path.rsplit("/", 1)[-1]
                if tail not in sections:
                    post_slugs.add(tail)
            print(f"  feed page {p}: {len(post_slugs)} post slugs total")
            if len(post_slugs) == before and p > 1:
                break  # no new posts on this page -> past the end
        sk.scroll_to_bottom()

        # 2. Post detail pages (post body + full comment tree in __NEXT_DATA__)
        slugs = sorted(post_slugs)
        if args.max_posts:
            slugs = slugs[: args.max_posts]
        print(f"fetching {len(slugs)} post pages ...")
        for i, s in enumerate(slugs, 1):
            sk.visit(f"{base}/{s}", f"post_{s}")
            if i % 25 == 0:
                print(f"  {i}/{len(slugs)}")

        # 3. Classroom: course list, then every course/module/lesson URL
        # discoverable from each page's payload.
        print("classroom ...")
        data = sk.visit(f"{base}/classroom", "classroom_index")
        course_paths = set()
        if data:
            find_strings(data, rf"^/{re.escape(slug)}/classroom/[a-z0-9-]+",
                         course_paths)
        seen = set()
        queue = sorted(course_paths)
        while queue:
            path = queue.pop(0)
            if path in seen:
                continue
            seen.add(path)
            name = "classroom_" + path.split("/classroom/", 1)[-1]
            data = sk.visit(f"https://www.skool.com{path}", name)
            more = set()
            if data:
                find_strings(data,
                             rf"^/{re.escape(slug)}/classroom/[a-z0-9-]+",
                             more)
                # lesson deep links use ?md= module ids
                find_strings(data, r"md=[a-f0-9]+", more)
            for m in sorted(more):
                if m.startswith("/") and m not in seen:
                    queue.append(m)
            print(f"  {path} (+{len(more)} refs, {len(queue)} queued)")

        print("members page (first pages only) ...")
        for p in range(1, 4):
            sk.visit(f"{base}/members" + ("" if p == 1 else f"?p={p}"),
                     f"members_p{p}")

    n_pages = len(list((RAW / "pages").glob("*.json")))
    n_api = len(list((RAW / "api").glob("*.json")))
    print(f"done: {n_pages} page captures, {n_api} api captures in {RAW}")
    print("next: python distill.py")


if __name__ == "__main__":
    sys.exit(main())
