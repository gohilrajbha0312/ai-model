"""
Log Analyzer — parse system log files for suspicious patterns.
Educational tool for understanding log analysis in security operations.
"""

import os
import re
import logging
from typing import List, Dict
from collections import Counter

logger = logging.getLogger(__name__)

# Suspicious patterns to look for
SUSPICIOUS_PATTERNS = {
    "Failed Login Attempts": [
        re.compile(r"Failed password", re.I),
        re.compile(r"authentication fail", re.I),
        re.compile(r"failed login", re.I),
        re.compile(r"invalid user", re.I),
        re.compile(r"FAILED LOGIN", re.I),
    ],
    "Privilege Escalation": [
        re.compile(r"sudo:.*COMMAND", re.I),
        re.compile(r"su:.*session opened", re.I),
        re.compile(r"pkexec", re.I),
        re.compile(r"privilege escalat", re.I),
    ],
    "SSH Activity": [
        re.compile(r"sshd\[", re.I),
        re.compile(r"Accepted publickey", re.I),
        re.compile(r"Accepted password", re.I),
        re.compile(r"Connection closed by", re.I),
    ],
    "Suspicious Commands": [
        re.compile(r"wget\s+http", re.I),
        re.compile(r"curl\s+.*\|\s*(?:ba)?sh", re.I),
        re.compile(r"chmod\s+\+s", re.I),
        re.compile(r"nc\s+-[elp]", re.I),
        re.compile(r"ncat\s+", re.I),
        re.compile(r"/etc/shadow", re.I),
        re.compile(r"reverse.shell", re.I),
    ],
    "Service Changes": [
        re.compile(r"systemctl\s+(start|stop|enable|disable)", re.I),
        re.compile(r"service\s+\w+\s+(start|stop)", re.I),
        re.compile(r"iptables\s+-[ADIRF]", re.I),
    ],
}

# Default log files to check
DEFAULT_LOG_PATHS = [
    "/var/log/auth.log",
    "/var/log/syslog",
    "/var/log/secure",
    "/var/log/messages",
]


class LogAnalyzer:
    """Analyse system log files for suspicious activity."""

    def __init__(self, max_lines: int = 10000):
        self.max_lines = max_lines

    def _analyze_file(self, filepath: str) -> Dict[str, List[str]]:
        """Analyse a single log file and return categorised findings."""
        findings: Dict[str, List[str]] = {cat: [] for cat in SUSPICIOUS_PATTERNS}

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh):
                    if i >= self.max_lines:
                        break
                    line = line.strip()
                    for category, patterns in SUSPICIOUS_PATTERNS.items():
                        for pattern in patterns:
                            if pattern.search(line):
                                findings[category].append(line[:200])
                                break  # one match per category per line
        except PermissionError:
            findings["Errors"] = [f"Permission denied: {filepath}"]
        except FileNotFoundError:
            findings["Errors"] = [f"File not found: {filepath}"]
        except Exception as exc:
            findings["Errors"] = [f"Error reading {filepath}: {exc}"]

        return findings

    def run(self, log_path: str | None = None) -> str:
        """
        Analyse log files for suspicious patterns.
        If log_path is None, scan default system log locations.
        """
        paths: List[str] = []

        if log_path and os.path.isfile(log_path):
            paths = [log_path]
        elif log_path and os.path.isdir(log_path):
            paths = [
                os.path.join(log_path, f)
                for f in os.listdir(log_path)
                if f.endswith(".log") or f in ("auth.log", "syslog", "secure", "messages")
            ]
        else:
            paths = [p for p in DEFAULT_LOG_PATHS if os.path.isfile(p)]

        if not paths:
            return (
                "📄 **Log Analyzer**\n\n"
                "No log files found to analyse.\n"
                "Try: 'analyze logs /var/log/auth.log' or 'analyze logs /path/to/logfile'"
            )

        lines = ["📄 **Log Analysis Report**", ""]
        total_findings = 0

        for filepath in paths:
            lines.append(f"### 📁 {filepath}")
            findings = self._analyze_file(filepath)

            file_findings = 0
            for category, matches in findings.items():
                if matches:
                    lines.append(f"\n**{category}** ({len(matches)} occurrence{'s' if len(matches) != 1 else ''}):")
                    # Show up to 5 samples
                    for match in matches[:5]:
                        lines.append(f"  • `{match}`")
                    if len(matches) > 5:
                        lines.append(f"  • *(… and {len(matches) - 5} more)*")
                    file_findings += len(matches)

            if file_findings == 0:
                lines.append("  ✅ No suspicious patterns detected.")
            total_findings += file_findings
            lines.append("")

        # Summary
        lines.append("---")
        lines.append(f"**Total suspicious entries: {total_findings}**")
        if total_findings > 50:
            lines.append("⚠️ *High number of suspicious entries. Investigate immediately.*")
        elif total_findings > 0:
            lines.append("⚠️ *Review flagged entries for potential security incidents.*")
        else:
            lines.append("✅ *No suspicious activity detected in scanned logs.*")

        return "\n".join(lines)
