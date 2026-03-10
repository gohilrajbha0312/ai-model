"""
Tool Executor — parses AI intents and triggers cybersecurity tools.
"""

import logging
from typing import Dict, Any, Optional

from modules.port_scanner import PortScanner
from modules.subdomain_enum import SubdomainEnumerator
from modules.whois_lookup import WhoisLookup
from modules.dns_lookup import DnsLookup
from modules.vulnerability_checker import VulnerabilityChecker
from modules.hash_cracker_helper import HashCrackerHelper
from modules.log_analyzer import LogAnalyzer
from modules.cve_lookup import CVELookup
from modules.password_strength_checker import PasswordStrengthChecker

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Manages execution of cybersecurity tools."""

    def __init__(self):
        self.tools = {
            "port_scan": PortScanner(),
            "subdomain_enum": SubdomainEnumerator(),
            "whois": WhoisLookup(),
            "dns": DnsLookup(),
            "vuln_check": VulnerabilityChecker(),
            "hash_crack": HashCrackerHelper(),
            "log_analyze": LogAnalyzer(),
            "cve_lookup": CVELookup(),
            "pass_strength": PasswordStrengthChecker(),
        }

    def execute_tool(self, tool_name: str, target: str, **kwargs) -> str:
        """Execute a specific tool against a target."""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"❌ Unknown tool: {tool_name}"

        try:
            logger.info("Executing %s on target %s", tool_name, target)
            if tool_name == "port_scan" and "start_port" in kwargs and "end_port" in kwargs:
                return tool.run(target, kwargs["start_port"], kwargs["end_port"])
            return tool.run(target)
        except Exception as exc:
            logger.error("Error executing %s: %s", tool_name, exc, exc_info=True)
            return f"❌ Error running {tool_name}: {exc}"
