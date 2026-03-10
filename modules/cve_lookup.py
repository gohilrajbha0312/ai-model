"""
CVE Lookup Module — fetches information about Common Vulnerabilities and Exposures.
"""

import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CVELookup:
    """Looks up CVE details via the NIST NVD or an external API."""

    def run(self, cve_id: str) -> str:
        """Fetch CVE details."""
        cve_id = cve_id.strip().upper()
        if not cve_id.startswith("CVE-"):
            return "❌ Invalid CVE ID format. Must start with 'CVE-' (e.g. CVE-2021-44228)."

        # Using the CIRCL CVE API as it doesn't require an API key for basic lookups
        url = f"https://cve.circl.lu/api/cve/{cve_id}"

        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 404:
                return f"❌ CVE '{cve_id}' not found in database."
            resp.raise_for_status()

            data = resp.json()
            if not data:
                return f"❌ No data returned for '{cve_id}'."

            summary = data.get("summary", "No description available.")
            cvss = data.get("cvss", "N/A")
            published = data.get("Published", "N/A")

            res = [
                f"🛡️ **CVE Lookup: {cve_id}**",
                f"**CVSS Score:** {cvss}",
                f"**Published:** {published[:10] if published else 'N/A'}",
                "",
                f"**Description:**",
                summary
            ]
            return "\n".join(res)

        except requests.Timeout:
            return f"❌ Timeout while fetching data for {cve_id}."
        except requests.RequestException as e:
            return f"❌ Error connecting to CVE database: {e}"
        except Exception as e:
            logger.error("CVE lookup failed: %s", e)
            return f"❌ Internal error looking up CVE: {e}"
