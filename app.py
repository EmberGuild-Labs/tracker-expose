import os

import requests
from flask import Flask, render_template, request, jsonify

from parser import extract_domains
from blocklist import check_domains, load_blocklists
from categories import categorize_results, compute_score

app = Flask(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan():
    url = request.form.get("url", "").strip()
    if not url:
        return render_template("index.html", error="Please enter a URL.")

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        return render_template("index.html", error=f"Could not fetch URL: {e}")

    html = resp.text
    domains = extract_domains(html, url)
    blocklist_hits = check_domains(domains)
    categorized = categorize_results(domains, blocklist_hits)
    score = compute_score(categorized)

    total_domains = len(domains)
    total_trackers = sum(
        1 for entries in categorized.values()
        for e in entries if e["blocked"]
    )

    return render_template(
        "results.html",
        url=url,
        categorized=categorized,
        score=score,
        total_domains=total_domains,
        total_trackers=total_trackers,
    )


@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing url"}), 400

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 502

    html = resp.text
    domains = extract_domains(html, url)
    blocklist_hits = check_domains(domains)
    categorized = categorize_results(domains, blocklist_hits)
    score = compute_score(categorized)

    return jsonify({
        "url": url,
        "score": score,
        "total_domains": len(domains),
        "total_trackers": sum(
            1 for entries in categorized.values()
            for e in entries if e["blocked"]
        ),
        "categories": categorized,
    })


if __name__ == "__main__":
    load_blocklists()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
