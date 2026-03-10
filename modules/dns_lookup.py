"""
DNS Lookup — query various DNS record types using dnspython.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]


class DnsLookup:
    """Perform DNS lookups for various record types."""

    def run(self, target: str, record_types: List[str] | None = None) -> str:
        """Look up DNS records for the given domain."""
        try:
            import dns.resolver  # dnspython

            types = record_types or RECORD_TYPES
            lines = [f"🔎 **DNS Lookup for {target}**", ""]

            for rtype in types:
                try:
                    answers = dns.resolver.resolve(target, rtype)
                    lines.append(f"**{rtype} Records:**")
                    for rdata in answers:
                        if rtype == "MX":
                            lines.append(f"  • Priority {rdata.preference}: {rdata.exchange}")
                        elif rtype == "SOA":
                            lines.append(
                                f"  • Primary NS: {rdata.mname}, "
                                f"Email: {rdata.rname}, "
                                f"Serial: {rdata.serial}"
                            )
                        else:
                            lines.append(f"  • {rdata.to_text()}")
                    lines.append("")
                except dns.resolver.NoAnswer:
                    continue
                except dns.resolver.NXDOMAIN:
                    return f"❌ Domain does not exist: {target}"
                except dns.resolver.NoNameservers:
                    lines.append(f"**{rtype}:** No nameservers available")
                    lines.append("")
                except Exception:
                    continue

            if len(lines) <= 2:
                lines.append("No DNS records found.")

            return "\n".join(lines)

        except ImportError:
            return "❌ dnspython library not installed. Run: pip install dnspython"
        except Exception as exc:
            error_msg = f"❌ DNS lookup failed for {target}: {exc}"
            logger.error(error_msg)
            return error_msg
