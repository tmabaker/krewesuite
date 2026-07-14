# Krewe Suite

**Enterprise Tools. Louisiana Soul.**

Purpose-built business tools for MSPs and the businesses they serve. By [NO & SE IT Group](https://noitgroup.com).

## Products

| Product | Description | Status | Landing page | App |
|---------|-------------|--------|--------------|-----|
| **KreweConnect** | Modern employee directory — multi-tenant, secure, powered by Microsoft Entra ID | Live | `/kreweconnect/` | `/app/kreweconnect/` |
| **KreweReview** | Contract lifecycle management — track, approve, and renew with confidence | Live | `/krewereview/` | `/app/kreweconnect/contracts` |
| **KreweCatch** | AI-powered threat analysis for suspicious links, files, domains, and emails | New | `/krewecatch/` | [krewecatch.ai](https://krewecatch.ai) (standalone) |
| **KreweGovernance** | Policy template engine with variable wizard, assembly, and acknowledgment tracking | Coming soon | `/krewegovernance/` | — |

The app launcher hub at `/app/` links to every module.

## Folder Structure

```
krewesuite/
├── index.html                  # Krewe Suite overview page
├── css/styles.css              # Suite overview styles
├── js/main.js                  # Suite overview scripts
├── staticwebapp.config.json    # Azure Static Web App routing & security headers
├── README.md                   # This file
├── app/
│   ├── index.html              # App launcher hub (/app/) — links to all modules
│   └── kreweconnect/           # Built KreweConnect SPA (deployed fresh from the
│                               #   tmabaker/kreweconnect repo by its SWA workflow)
├── kreweconnect/               # KreweConnect landing page
│   ├── index.html
│   ├── css/styles.css
│   └── js/main.js
├── krewereview/                # KreweReview landing page
│   ├── index.html
│   ├── css/styles.css
│   └── js/main.js
├── krewecatch/                 # KreweCatch landing page (app is standalone at krewecatch.ai)
│   ├── index.html
│   ├── css/styles.css
│   └── js/main.js
└── krewegovernance/            # KreweGovernance landing page (coming soon)
    ├── index.html
    ├── css/styles.css
    └── js/main.js
```

## Deployment

### Azure Static Web Apps

This project is designed for Azure Static Web Apps. The `staticwebapp.config.json` handles:

- **Routing:** `/kreweconnect/*`, `/krewereview/*`, `/krewecatch/*`, and `/krewegovernance/*` serve from their respective directories; root serves the suite overview
- **Security headers:** CSP, X-Frame-Options (DENY), X-Content-Type-Options, XSS Protection, Referrer-Policy, Permissions-Policy
- **Trailing slash redirects:** each module path redirects to its trailing-slash form (e.g. `/kreweconnect` → `/kreweconnect/`)

### Deploy Steps

1. Push to your GitHub repository
2. Connect the repo to Azure Static Web Apps via Azure Portal or CLI
3. Set the app location to `/` (root of this directory)
4. No build step required — static HTML/CSS/JS

### Custom Domain

Configure `krewesuite.noitgroup.com` as a custom domain in Azure Static Web Apps settings.

### Local Preview

```bash
# From the krewesuite directory
npx serve .
# Or use any static file server
python3 -m http.server 8080
```

## Design System

All pages share the same Mardi Gras dark theme:

- **Background:** `#0A0E17` (dark navy)
- **Purple:** `#5B2D8E` (primary accent)
- **Gold:** `#D4A843` (CTAs, highlights)
- **Green:** `#1B6B3A` (success, secondary)
- **Font:** Segoe UI / system-ui stack
- **Animations:** Floating particles, scroll-reveal, gradient pulses
- **Accessibility:** Reduced motion support, focus-visible styles, semantic HTML

## Contact Form

Contact forms store submissions to `localStorage` (key: `krewesuite_submissions` for KreweReview, `kreweconnect_submissions` for KreweConnect). Backend integration can be added later to POST to an API endpoint.

---

© 2026 NO & SE IT Group. All rights reserved.
