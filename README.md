# Tracker Expose

A privacy tool that scans any webpage and exposes every tracker, ad network, and fingerprinting script hiding inside it. Enter a URL, and Tracker Expose fetches the page server-side, analyzes all outbound requests and embedded scripts, then maps them against known tracker blocklists (EasyPrivacy, EasyList) to produce a clear, categorized report.

Companion tool to [Project Oryn](https://github.com/EmberGuild-Labs/oryn) — useful for validating that Oryn's blocking and privacy patches are actually working in the wild.

---

## Features

- Fetches target pages server-side (avoids CORS, hides your IP from the target)
- Parses all `<script>`, `<img>`, `<iframe>`, and `<link>` tags for third-party domains
- Matches outbound domains against EasyPrivacy and EasyList blocklists
- Categorizes findings: ad networks, analytics, fingerprinting scripts, social trackers, CDNs
- Displays a severity-graded report with per-category counts
- Shareable result URLs (query param based)

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3, Flask |
| Page fetching | `requests` + `BeautifulSoup4` |
| Blocklist parsing | Custom parser against EasyPrivacy/EasyList filter lists |
| Frontend | Vanilla JS, HTML/CSS |
| Hosting | proxnode.xyz via ProxDeploy + Cloudflare Tunnel |

---

## Project Structure

```
tracker-expose/
├── app.py               # Flask app — main routes and scan logic
├── blocklist.py         # Blocklist loader and domain matcher
├── parser.py            # HTML parser — extracts all outbound domains
├── categories.py        # Categorization logic (ads, analytics, fingerprint, etc.)
├── lists/
│   ├── easyprivacy.txt  # EasyPrivacy filter list (downloaded at setup)
│   └── easylist.txt     # EasyList filter list (downloaded at setup)
├── static/
│   ├── style.css
│   └── main.js
├── templates/
│   ├── index.html       # URL input page
│   └── results.html     # Scan results page
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites

- Python 3.10+
- pip
- A proxnode.xyz subdomain pointed at this app via ProxDeploy

### Installation

```bash
git clone https://github.com/EmberGuild-Labs/tracker-expose
cd tracker-expose
pip install -r requirements.txt
```

### Download blocklists

```bash
python blocklist.py --update
```

This fetches the latest EasyPrivacy and EasyList filter lists into `lists/`.

### Run locally

```bash
python app.py
```

App runs at `http://localhost:5000` by default.

### Deploy via ProxDeploy

1. Push to your GitHub repo under EmberGuild-Labs
2. Open ProxDeploy at `proxnode.xyz`
3. Enter name: `tracker-expose`, repo: `EmberGuild-Labs/tracker-expose`
4. Set subdomain: `trackers.proxnode.xyz`
5. Deploy

---

## How It Works

1. User submits a URL via the frontend form
2. Flask backend fetches the raw HTML of the target page using `requests` (with a realistic User-Agent)
3. `parser.py` extracts all third-party domain references from script/img/iframe/link tags and inline CSS
4. `blocklist.py` checks each domain against the loaded EasyPrivacy and EasyList rules
5. `categories.py` assigns each hit to a category (ad network, analytics, fingerprinting, social, CDN)
6. Results are rendered in `results.html` with a per-category breakdown and severity rating

---

## Blocklist Sources

| List | Source | Focus |
|---|---|---|
| EasyPrivacy | https://easylist.to/easylist/easyprivacy.txt | Trackers, analytics, fingerprinting |
| EasyList | https://easylist.to/easylist/easylist.txt | Ads and ad networks |

Blocklists should be refreshed periodically. Run `python blocklist.py --update` to pull the latest versions.

---

## Roadmap

- [ ] Live request interception mode (proxy-based, not just static HTML parse)
- [ ] Side-by-side comparison: site with vs. without Oryn active
- [ ] Blocklist auto-update cron job
- [ ] Export results as JSON
- [ ] Browser extension companion that triggers a scan from context menu

---

## Related Projects

- [Project Oryn](https://github.com/EmberGuild-Labs/oryn) — Privacy-focused Chromium fork this tool was built to complement
- [ProxDeploy](https://github.com/EmberGuild-Labs/proxdeploy) — The self-hosted mini-PaaS used to host this app

---

## License

MIT © EmberGuild-Labs
