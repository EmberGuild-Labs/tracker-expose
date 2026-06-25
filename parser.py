import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


def extract_domains(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(base_url).netloc.lower()
    domains = set()

    def _add_url(url):
        if not url:
            return
        url = url.strip()
        if url.startswith("//"):
            url = "https:" + url
        if not url.startswith(("http://", "https://")):
            return
        try:
            netloc = urlparse(url).netloc.lower()
        except Exception:
            return
        if not netloc or netloc == base_domain:
            return
        netloc = netloc.split(":")[0]
        if netloc:
            domains.add(netloc)

    for tag in soup.find_all("script", src=True):
        _add_url(tag["src"])

    for tag in soup.find_all("img", src=True):
        _add_url(tag["src"])

    for tag in soup.find_all("iframe", src=True):
        _add_url(tag["src"])

    for tag in soup.find_all("link", href=True):
        _add_url(tag["href"])

    for tag in soup.find_all("script"):
        if tag.string:
            urls = re.findall(r'https?://[^\s"\'<>]+', tag.string)
            for url in urls:
                _add_url(url)

    for tag in soup.find_all(style=True):
        urls = re.findall(r'url\(["\']?(https?://[^"\')\s]+)', tag["style"])
        for url in urls:
            _add_url(url)

    for style_tag in soup.find_all("style"):
        if style_tag.string:
            urls = re.findall(r'url\(["\']?(https?://[^"\')\s]+)', style_tag.string)
            for url in urls:
                _add_url(url)

    return sorted(domains)
