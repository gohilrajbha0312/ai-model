"""
Input Validation — sanitise and validate all user-supplied data.
"""

import re
import logging
from typing import Tuple

import config

logger = logging.getLogger(__name__)

# Characters that could enable shell / SQL injection
_DANGEROUS_CHARS = re.compile(r"[;|&`$(){}!\[\]<>\\]")

# Patterns indicating requests for illegal activity
_ILLEGAL_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"hack\s+into",
        r"break\s+into",
        r"steal\s+(data|credentials|password)",
        r"ddos\s+attack",
        r"launch\s+(an?\s+)?attack\s+on",
        r"ransomware",
        r"create\s+(a\s+)?virus",
        r"phishing\s+campaign",
        r"illegal\s+access",
        r"unauthorized\s+access\s+to\s+(?!your)",
        r"exploit\s+(a\s+)?live\s+(system|server|target)",
    ]
]

# Simple IPv4 pattern
_IPV4 = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$"
)

# Domain name pattern (simple)
_DOMAIN = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,}$"
)


def sanitize_input(text: str) -> str:
    """
    Strip dangerous shell metacharacters and enforce length limit.
    Returns the cleaned string.
    """
    if len(text) > config.MAX_INPUT_LENGTH:
        text = text[: config.MAX_INPUT_LENGTH]
        logger.warning("Input truncated to %d characters.", config.MAX_INPUT_LENGTH)

    cleaned = _DANGEROUS_CHARS.sub("", text).strip()
    if cleaned != text.strip():
        logger.warning("Dangerous characters removed from input.")
    return cleaned


def validate_ip(ip: str) -> Tuple[bool, str]:
    """Validate an IPv4 address string."""
    ip = ip.strip()
    if _IPV4.match(ip):
        return True, ip
    return False, f"Invalid IPv4 address: {ip}"


def validate_domain(domain: str) -> Tuple[bool, str]:
    """Validate a domain name string."""
    domain = domain.strip().lower()
    if _DOMAIN.match(domain):
        return True, domain
    # Also accept localhost
    if domain == "localhost":
        return True, domain
    return False, f"Invalid domain: {domain}"


def validate_target(target: str) -> Tuple[bool, str]:
    """Validate that target is a valid IP or domain."""
    target = target.strip()
    ok, _ = validate_ip(target)
    if ok:
        return True, target
    ok, _ = validate_domain(target)
    if ok:
        return True, target.lower()
    return False, f"Invalid target (must be an IP or domain): {target}"


def validate_port(port: str | int) -> Tuple[bool, int]:
    """Validate a single port number."""
    try:
        p = int(port)
        if 1 <= p <= config.ALLOWED_SCAN_PORTS_MAX:
            return True, p
        return False, 0
    except (ValueError, TypeError):
        return False, 0


def validate_port_range(start: str | int, end: str | int) -> Tuple[bool, Tuple[int, int]]:
    """Validate a port range."""
    ok1, s = validate_port(start)
    ok2, e = validate_port(end)
    if ok1 and ok2 and s <= e:
        return True, (s, e)
    return False, (0, 0)


def is_safe_query(text: str) -> Tuple[bool, str]:
    """
    Check if a user query is requesting illegal activity.
    Returns (is_safe, reason).
    """
    for pattern in _ILLEGAL_PATTERNS:
        if pattern.search(text):
            reason = (
                "⚠️  I cannot assist with illegal activities. "
                "This assistant is for educational and authorised testing only."
            )
            logger.warning("Unsafe query blocked: %s", text[:80])
            return False, reason
    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate a username (alphanumeric + underscore, 3-32 chars)."""
    if not re.match(r"^[a-zA-Z0-9_]{3,32}$", username):
        return False, "Username must be 3-32 alphanumeric characters or underscores."
    return True, username


def validate_password(password: str) -> Tuple[bool, str]:
    """Ensure password meets minimum complexity."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, password
