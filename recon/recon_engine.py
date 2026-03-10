"""
Recon Engine — automated reconnaissance pipeline.
"""

import logging
from typing import Dict, Any

from tools.tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


class ReconEngine:
    """Automated reconnaissance workflow."""

    def __init__(self):
        self.executor = ToolExecutor()

    def run_recon(self, domain: str) -> str:
        """Run a full reconnaissance pipeline on a domain."""
        logger.info("Starting automated recon on %s", domain)
        results = [f"🔍 **Automated Reconnaissance Report for {domain}**\n"]

        # 1. DNS Lookup
        results.append("### 1. DNS Records")
        results.append(self.executor.execute_tool("dns", domain))

        # 2. WHOIS
        results.append("\n### 2. WHOIS Information")
        results.append(self.executor.execute_tool("whois", domain))

        # 3. Subdomains
        results.append("\n### 3. Subdomain Enumeration")
        results.append(self.executor.execute_tool("subdomain_enum", domain))

        # 4. Vuln/Headers Check
        results.append("\n### 4. Basic Vulnerability Check")
        results.append(self.executor.execute_tool("vuln_check", domain))

        return "\n".join(results)
