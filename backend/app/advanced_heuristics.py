import re
import socket
from urllib.parse import urlparse
import tldextract

TARGET_BRANDS = [
    "google", "paypal", "microsoft", "apple", "amazon", 
    "netflix", "facebook", "instagram", "chase", "wellsfargo", "binance"
]

def check_homograph_and_typosquatting(domain: str) -> dict:
    extracted = tldextract.extract(domain)
    sld = extracted.domain.lower()
    
    # Check for homoglyph / visual impersonation tricks (0 for o, 1/l/I, etc.)
    normalized_sld = (
        sld.replace('0', 'o')
           .replace('1', 'l')
           .replace('vv', 'w')
           .replace('rn', 'm')
    )

    detected_impersonation = None
    similarity_flag = False

    for brand in TARGET_BRANDS:
        # Direct typo impersonation
        if sld != brand and (normalized_sld == brand or (brand in sld and len(sld) <= len(brand) + 4)):
            detected_impersonation = brand
            similarity_flag = True
            break
            
    return {
        "is_impersonation": similarity_flag,
        "impersonated_target": detected_impersonation,
        "extracted_domain": f"{extracted.domain}.{extracted.suffix}"
    }

def analyze_advanced_network_signals(url: str) -> dict:
    signals = []
    penalty_score = 0
    
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    
    # 1. Typosquatting / Brand Squatting Detection
    typo_check = check_homograph_and_typosquatting(hostname)
    if typo_check["is_impersonation"]:
        signals.append(f"Typosquatting/Homograph target detected: spoofing '{typo_check['impersonated_target']}'")
        penalty_score += 35

    # 2. Hex/Unicode/Punycode Obfuscation
    if "xn--" in hostname:
        signals.append("Punycode internationalized domain detected (IDN homograph vulnerability)")
        penalty_score += 25
        
    # 3. Port Obfuscation (non-standard ports)
    if parsed.port and parsed.port not in [80, 443]:
        signals.append(f"Non-standard HTTP service port detected (Port {parsed.port})")
        penalty_score += 20
        
    # 4. Multi-level Subdomain Masking
    subdomain_depth = len(hostname.split(".")) - 2
    if subdomain_depth >= 4:
        signals.append(f"Deep subdomain masking chain detected ({subdomain_depth} levels)")
        penalty_score += 15

    return {
        "penalty_score": penalty_score,
        "signals": signals
    }
