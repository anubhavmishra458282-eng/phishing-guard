import math
import re
from urllib.parse import urlparse
import tldextract

SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "banking", 
    "signin", "wallet", "confirm", "security", "support", "password"
]

def calculate_entropy(text: str) -> float:
    if not text:
        return 0.0
    prob = [float(text.count(c)) / len(text) for c in set(text)]
    return -sum(p * math.log2(p) for p in prob)

def is_ip_address(host: str) -> bool:
    ipv4_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return bool(re.match(ipv4_pattern, host))

def extract_features(raw_url: str) -> dict:
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    ext = tldextract.extract(url)

    hostname = parsed.netloc.split(":")[0]
    path = parsed.path
    query = parsed.query

    subdomain_parts = [s for s in ext.subdomain.split(".") if s]
    num_subdomains = len(subdomain_parts)

    url_length = len(url)
    hostname_length = len(hostname)
    num_dots = url.count(".")
    num_hyphens = url.count("-")
    num_slashes = url.count("/")
    num_digits = sum(c.isdigit() for c in url)
    num_at = url.count("@")
    is_ip = 1 if is_ip_address(hostname) else 0
    entropy = calculate_entropy(hostname)
    has_https = 1 if parsed.scheme == "https" else 0

    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url.lower()]
    has_suspicious_kw = 1 if found_keywords else 0

    vector = [
        url_length,
        hostname_length,
        num_dots,
        num_hyphens,
        num_slashes,
        num_digits,
        num_at,
        is_ip,
        num_subdomains,
        entropy,
        has_https,
        has_suspicious_kw
    ]

    signals = []
    if is_ip:
        signals.append("Direct IP address used instead of domain name")
    if num_subdomains >= 3:
        signals.append(f"Excessive subdomains detected ({num_subdomains} levels)")
    if num_dots >= 4:
        signals.append(f"Abnormal dot count in URL ({num_dots} dots)")
    if num_at > 0:
        signals.append("Authentication symbol '@' present in URL")
    if has_suspicious_kw:
        signals.append(f"Suspicious security keywords found: {', '.join(found_keywords)}")
    if not has_https:
        signals.append("Unencrypted connection (HTTP instead of HTTPS)")
    if entropy > 4.0:
        signals.append("High hostname character entropy (random characters)")

    return {
        "vector": vector,
        "signals": signals,
        "feature_summary": {
            "url_length": url_length,
            "hostname_length": hostname_length,
            "num_dots": num_dots,
            "num_subdomains": num_subdomains,
            "is_ip": bool(is_ip),
            "entropy": round(entropy, 2),
            "has_https": bool(has_https)
        }
    }
