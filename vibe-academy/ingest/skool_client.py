"""Playwright-based Skool client.

Skool is a Next.js app: every page embeds its full data payload in a
`__NEXT_DATA__` <script> tag, and the SPA also calls api.skool.com. Rather
than depending on any specific (undocumented, changeable) API shape, this
client:

  1. Logs in through the real login form (resilient to API changes).
  2. For each page visited, saves the complete __NEXT_DATA__ JSON.
  3. Captures every api.skool.com XHR/fetch response seen along the way.

Raw captures are the source of truth; distill.py interprets them. If Skool
changes its schema, re-run ingest and fix only the distiller.
"""

import json
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

CHROMIUM_PATH = "/opt/pw-browsers/chromium"  # pre-installed in Claude cloud env
LOGIN_URL = "https://www.skool.com/login"


class SkoolClient:
    def __init__(self, raw_dir, page_delay=1.5):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        (self.raw_dir / "pages").mkdir(exist_ok=True)
        (self.raw_dir / "api").mkdir(exist_ok=True)
        self.page_delay = page_delay
        self._api_counter = 0

    def __enter__(self):
        self._pw = sync_playwright().start()
        launch_kwargs = {"headless": True}
        if Path(CHROMIUM_PATH).exists():
            launch_kwargs["executable_path"] = CHROMIUM_PATH
        self._browser = self._pw.chromium.launch(**launch_kwargs)
        self._ctx = self._browser.new_context(
            viewport={"width": 1400, "height": 2000},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            ),
        )
        self.page = self._ctx.new_page()
        self.page.on("response", self._capture_api_response)
        return self

    def __exit__(self, *exc):
        self._browser.close()
        self._pw.stop()

    # -- auth ---------------------------------------------------------------

    def login(self, email, password):
        self.page.goto(LOGIN_URL, wait_until="networkidle")
        self.page.fill('input[type="email"]', email)
        self.page.fill('input[type="password"]', password)
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state("networkidle")
        cookies = {c["name"] for c in self._ctx.cookies()}
        if "auth_token" not in cookies:
            raise RuntimeError(
                "Login did not produce an auth_token cookie — check the "
                "credential, or the form may have a captcha/2FA step. "
                "Run once with headless=False locally to inspect."
            )
        return True

    # -- capture ------------------------------------------------------------

    def _capture_api_response(self, response):
        try:
            host = urlparse(response.url).netloc
            if "api.skool.com" not in host or response.status != 200:
                return
            body = response.json()
        except Exception:
            return
        self._api_counter += 1
        out = self.raw_dir / "api" / f"{self._api_counter:05d}.json"
        out.write_text(json.dumps({"url": response.url, "body": body}, indent=1))

    def visit(self, url, name):
        """Load a page, wait for it to settle, save its __NEXT_DATA__."""
        self.page.goto(url, wait_until="networkidle")
        time.sleep(self.page_delay)
        data = self.page.evaluate(
            "() => { const el = document.getElementById('__NEXT_DATA__');"
            " return el ? el.textContent : null; }"
        )
        record = {"url": url, "next_data": json.loads(data) if data else None}
        safe = name.replace("/", "_")[:180]
        (self.raw_dir / "pages" / f"{safe}.json").write_text(
            json.dumps(record, indent=1)
        )
        return record["next_data"]

    def scroll_to_bottom(self, max_rounds=30):
        """For infinite-scroll pages: keep scrolling until height stabilizes,
        letting the API-response capture hook collect paginated data."""
        last = 0
        for _ in range(max_rounds):
            height = self.page.evaluate("document.body.scrollHeight")
            if height == last:
                break
            last = height
            self.page.mouse.wheel(0, height)
            time.sleep(self.page_delay)
