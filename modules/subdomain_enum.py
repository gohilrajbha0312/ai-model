"""
Subdomain Enumerator — DNS brute-force with a built-in wordlist.
Educational tool for understanding subdomain discovery.
"""

import socket
import logging
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Built-in common subdomain wordlist
DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "smtp", "pop", "imap", "webmail",
    "admin", "portal", "blog", "dev", "staging", "test",
    "api", "app", "m", "mobile", "cdn", "static", "assets",
    "ns1", "ns2", "dns", "dns1", "dns2",
    "vpn", "remote", "gateway", "proxy",
    "db", "database", "mysql", "postgres", "redis", "mongo",
    "git", "gitlab", "github", "bitbucket", "jenkins", "ci",
    "docs", "wiki", "help", "support", "status", "monitor",
    "shop", "store", "checkout", "pay", "billing",
    "auth", "login", "sso", "oauth", "id", "accounts",
    "cloud", "aws", "azure", "gcp",
    "beta", "alpha", "demo", "sandbox", "uat",
    "intranet", "internal", "corp", "office",
    "backup", "old", "new", "legacy", "archive",
    "media", "img", "images", "video", "upload",
    "grafana", "kibana", "elastic", "prometheus", "nagios",
    "jira", "confluence", "slack", "teams",
]


class SubdomainEnumerator:
    """DNS brute-force subdomain enumerator."""

    def __init__(self, timeout: float = 2.0, max_workers: int = 20):
        self.timeout = timeout
        self.max_workers = max_workers

    def _check_subdomain(self, subdomain: str, domain: str) -> Tuple[str, str | None]:
        """Try to resolve subdomain.domain. Returns (fqdn, ip_or_None)."""
        fqdn = f"{subdomain}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            return fqdn, ip
        except socket.gaierror:
            return fqdn, None

    def run(self, domain: str, wordlist: List[str] | None = None) -> str:
        """
        Enumerate subdomains for the given domain.
        """
        words = wordlist or DEFAULT_WORDLIST
        logger.info("Enumerating subdomains for %s — %d candidates", domain, len(words))

        found: List[Tuple[str, str]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._check_subdomain, word, domain): word
                for word in words
            }
            for future in as_completed(futures):
                fqdn, ip = future.result()
                if ip:
                    found.append((fqdn, ip))

        found.sort()

        lines = [f"🌐 **Subdomain Enumeration for {domain}**", ""]
        if found:
            lines.append(f"Found **{len(found)}** subdomain(s):\n")
            lines.append("| Subdomain | IP Address |")
            lines.append("|-----------|------------|")
            for fqdn, ip in found:
                lines.append(f"| {fqdn} | {ip} |")
        else:
            lines.append("No subdomains found from the wordlist.")

        lines.append(f"\nTested {len(words)} subdomain candidates.")
        return "\n".join(lines)
