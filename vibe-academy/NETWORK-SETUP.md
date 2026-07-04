# One-time setup: network allowlist for Skool ingest

The Claude cloud environment's network policy currently **blocks skool.com**
(the proxy gateway answers `403` to CONNECT — verified 2026-07-04). The
ingest pipeline cannot run until these domains are allowed.

## Where to change it

claude.ai → **Settings → Code environments** → select the environment used
for these sessions → **Network policy** → add allowed domains.

## Domains required

| Domain | Why |
|---|---|
| `www.skool.com` | Login + all community/classroom pages |
| `api.skool.com` | Skool's API (login, feed, comments) |
| `assets.skool.com` | Avatars/images referenced by pages (optional but avoids errors) |
| `video.skool.com` | Skool-native hosted video metadata |
| `*.mux.com` | Skool-native video streams (transcript/caption fetch) |

## Optional — embedded video transcripts

Alex's lessons and community posts often embed video from third-party hosts.
Allow these only if you want the pipeline to pull transcripts/captions:

| Domain | Why |
|---|---|
| `www.youtube.com`, `youtubei.googleapis.com` | YouTube embeds + caption tracks |
| `www.loom.com` | Loom embeds |
| `player.vimeo.com`, `vimeo.com` | Vimeo embeds |
| `fast.wistia.net`, `fast.wistia.com` | Wistia embeds |

Without these, the pipeline still records every video's title + URL in
`content/videos/` — you just won't get transcripts for third-party embeds.

## Credentials (already in place)

- AWS Secrets Manager secret **`noit/skool`** holds the Skool login
  (email + password). The pipeline reads it at runtime via the session's
  AWS credentials; nothing is stored in the repo.
- ⚠️ **Rotation recommended**: the secret is stored with the credential
  values as JSON *keys* (console key/value entry quirk), which caused the
  password to surface in a session transcript on 2026-07-04. Change the
  Skool password and re-store the secret as
  `{"email": "...", "password": "..."}`.
