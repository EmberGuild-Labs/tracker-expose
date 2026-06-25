AD_NETWORKS = {
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "adnxs.com", "adsrvr.org", "criteo.com", "criteo.net",
    "moatads.com", "amazon-adsystem.com", "media.net",
    "pubmatic.com", "rubiconproject.com", "openx.net",
    "casalemedia.com", "indexww.com", "taboola.com", "outbrain.com",
    "revcontent.com", "mgid.com", "adroll.com", "bidswitch.net",
    "smartadserver.com", "33across.com", "sharethrough.com",
    "yieldmo.com", "triplelift.com", "sovrn.com", "lijit.com",
}

ANALYTICS = {
    "google-analytics.com", "googletagmanager.com", "analytics.google.com",
    "hotjar.com", "mixpanel.com", "segment.com", "segment.io",
    "amplitude.com", "heap.io", "heapanalytics.com",
    "fullstory.com", "mouseflow.com", "crazyegg.com",
    "optimizely.com", "clicktale.com", "newrelic.com",
    "nr-data.net", "chartbeat.com", "parsely.com", "parse.ly",
    "quantserve.com", "scorecardresearch.com", "comscore.com",
    "matomo.cloud", "plausible.io", "umami.is",
}

FINGERPRINTING = {
    "fingerprintjs.com", "fpjs.io", "fpjs.pro",
    "iovation.com", "threatmetrix.com",
    "permutive.com", "id5-sync.com", "liveintent.com",
    "tapad.com", "liveramp.com", "rlcdn.com",
    "crwdcntrl.net", "bluekai.com", "exelator.com",
    "eyeota.net", "semasio.net", "lotame.com",
}

SOCIAL_TRACKERS = {
    "facebook.net", "facebook.com", "fbcdn.net",
    "connect.facebook.net", "platform.twitter.com",
    "platform.linkedin.com", "snap.licdn.com",
    "tiktok.com", "analytics.tiktok.com",
    "pinterest.com", "assets.pinterest.com",
    "reddit.com", "redditstatic.com",
    "snapchat.com", "sc-static.net",
}

CDN_SERVICES = {
    "cloudflare.com", "cdnjs.cloudflare.com",
    "jsdelivr.net", "unpkg.com",
    "bootstrapcdn.com", "googleapis.com",
    "gstatic.com", "ajax.googleapis.com",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "stackpath.bootstrapcdn.com", "cdn.jsdelivr.net",
    "fastly.net", "akamaized.net", "akamai.net",
    "cloudfront.net",
}

CATEGORY_MAP = {
    "Ad Networks": AD_NETWORKS,
    "Analytics": ANALYTICS,
    "Fingerprinting": FINGERPRINTING,
    "Social Trackers": SOCIAL_TRACKERS,
    "CDNs": CDN_SERVICES,
}

SEVERITY = {
    "Fingerprinting": "high",
    "Ad Networks": "high",
    "Social Trackers": "medium",
    "Analytics": "medium",
    "CDNs": "low",
    "Unknown": "low",
}


def categorize_domain(domain):
    domain_lower = domain.lower()
    for category, domains in CATEGORY_MAP.items():
        for known in domains:
            if domain_lower == known or domain_lower.endswith("." + known):
                return category
    return "Unknown"


def categorize_results(domains, blocklist_hits):
    results = {}
    for domain in domains:
        is_blocked = domain in blocklist_hits
        category = categorize_domain(domain)
        if is_blocked and category == "Unknown":
            category = "Analytics"
        if category not in results:
            results[category] = []
        results[category].append({
            "domain": domain,
            "blocked": is_blocked,
            "severity": SEVERITY.get(category, "low"),
        })
    for entries in results.values():
        entries.sort(key=lambda x: (not x["blocked"], x["domain"]))
    return results


def compute_score(categorized):
    total_trackers = 0
    severity_weights = {"high": 3, "medium": 2, "low": 1}
    for category, entries in categorized.items():
        if category == "CDNs":
            continue
        for entry in entries:
            if entry["blocked"]:
                total_trackers += severity_weights.get(entry["severity"], 1)
    if total_trackers == 0:
        return {"grade": "A", "label": "Clean", "color": "#22c55e"}
    elif total_trackers <= 5:
        return {"grade": "B", "label": "Minor tracking", "color": "#84cc16"}
    elif total_trackers <= 15:
        return {"grade": "C", "label": "Moderate tracking", "color": "#eab308"}
    elif total_trackers <= 30:
        return {"grade": "D", "label": "Heavy tracking", "color": "#f97316"}
    else:
        return {"grade": "F", "label": "Severe tracking", "color": "#ef4444"}
