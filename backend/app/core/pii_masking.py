import re
from typing import Dict, Any

# Regex patterns for sensitive data
CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')
CVV_PATTERN = re.compile(r'\b(?:cvv|cvc|security code|cvv2)[\s:]*([0-9]{3,4})\b', re.IGNORECASE)
CNIC_PATTERN = re.compile(r'\b\d{5}-\d{7}-\d{1}\b')
EMAIL_PATTERN = re.compile(r'\b([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b')
PHONE_PATTERN = re.compile(r'\b(?:\+?92|0)?3\d{2}[ -]?\d{7}\b')

def mask_credit_card(text: str) -> str:
    """
    Masks payment card numbers, keeping only the last 4 digits.
    Example: '4532 1234 5678 9012' -> '****-****-****-9012'
    """
    def replace_card(match):
        raw = match.group(0)
        digits = re.sub(r'\D', '', raw)
        # Verify plausible card length (Luhn check or 13-19 digits)
        if len(digits) >= 13 and len(digits) <= 19:
            last4 = digits[-4:]
            return f"****-****-****-{last4}"
        return raw

    # Replace CVVs
    masked = CVV_PATTERN.sub(r'CVV: ***', text)
    # Replace Cards
    masked = CARD_PATTERN.sub(replace_card, masked)
    return masked

def mask_cnic(text: str) -> str:
    """Masks National ID/CNIC numbers."""
    return CNIC_PATTERN.sub(lambda m: f"{m.group(0)[:5]}-*******-{m.group(0)[-1]}", text)

def mask_pii_for_prompts(text: str) -> str:
    """
    Sanitizes customer text before feeding into AI prompts or logs.
    Masks payment cards, CVVs, and CNIC/National IDs.
    """
    if not text:
        return ""
    text = mask_credit_card(text)
    text = mask_cnic(text)
    return text

def sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively scrub sensitive fields from arbitrary dictionary payloads."""
    cleaned = {}
    sensitive_keys = {"password", "secret", "cvv", "cvc", "card_number", "token"}
    for k, v in payload.items():
        if any(s in k.lower() for s in sensitive_keys):
            cleaned[k] = "[REDACTED]"
        elif isinstance(v, dict):
            cleaned[k] = sanitize_payload(v)
        elif isinstance(v, str):
            cleaned[k] = mask_pii_for_prompts(v)
        else:
            cleaned[k] = v
    return cleaned
