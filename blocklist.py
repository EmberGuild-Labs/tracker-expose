import os
import re
import sys

import requests

LISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lists")

SOURCES = {
    "easyprivacy.txt": "https://easylist.to/easylist/easyprivacy.txt",
    "easylist.txt": "https://easylist.to/easylist/easylist.txt",
}


def update_lists():
    os.makedirs(LISTS_DIR, exist_ok=True)
    for filename, url in SOURCES.items():
        print(f"Downloading {filename}...")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        path = os.path.join(LISTS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(resp.text)
        print(f"  Saved {len(resp.text)} bytes to {path}")


def _parse_domain_from_rule(rule):
    rule = rule.strip()
    if not rule or rule.startswith("!") or rule.startswith("["):
        return None
    if "##" in rule or "#@#" in rule or "#?#" in rule:
        return None
    if rule.startswith("@@"):
        return None

    domain_match = re.match(r"^\|\|([a-z0-9._-]+[a-z])\^?", rule)
    if domain_match:
        return domain_match.group(1)

    return None


_blocked_domains = None


def load_blocklists():
    global _blocked_domains
    if _blocked_domains is not None:
        return _blocked_domains

    _blocked_domains = set()
    for filename in SOURCES:
        path = os.path.join(LISTS_DIR, filename)
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                domain = _parse_domain_from_rule(line)
                if domain:
                    _blocked_domains.add(domain)
    return _blocked_domains


def check_domain(domain, blocked=None):
    if blocked is None:
        blocked = load_blocklists()
    domain = domain.lower()
    parts = domain.split(".")
    for i in range(len(parts)):
        candidate = ".".join(parts[i:])
        if candidate in blocked:
            return True
    return False


def check_domains(domains):
    blocked = load_blocklists()
    return {d for d in domains if check_domain(d, blocked)}


if __name__ == "__main__":
    if "--update" in sys.argv:
        update_lists()
    else:
        print("Usage: python blocklist.py --update")
