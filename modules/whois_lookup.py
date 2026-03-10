"""
WHOIS Lookup — domain registration information.
Uses the python-whois library.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WhoisLookup:
    """Perform WHOIS lookups on domain names."""

    def run(self, target: str) -> str:
        """Look up WHOIS information for the given domain."""
        try:
            import whois  # python-whois

            w: Any = whois.whois(target)

            lines = [f"📋 **WHOIS Lookup for {target}**", ""]

            fields = [
                ("Domain Name", w.domain_name),
                ("Registrar", w.registrar),
                ("Creation Date", w.creation_date),
                ("Expiration Date", w.expiration_date),
                ("Updated Date", w.updated_date),
                ("Name Servers", w.name_servers),
                ("Status", w.status),
                ("DNSSEC", w.dnssec),
                ("Registrant", w.get("org") or w.get("registrant_name")),
                ("Country", w.get("country")),
                ("State", w.get("state")),
            ]

            for label, value in fields:
                if value:
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)
                    lines.append(f"**{label}:** {value}")

            return "\n".join(lines)

        except Exception as exc:
            error_msg = f"❌ WHOIS lookup failed for {target}: {exc}"
            logger.error(error_msg)
            return error_msg
