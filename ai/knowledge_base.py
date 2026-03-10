"""
Knowledge Base — load and search the cybersecurity knowledge files.
Improved with synonym expansion and fuzzy matching.
"""

import os
import json
import logging
import re
from typing import Dict, List, Tuple, Any

import config

logger = logging.getLogger(__name__)

# ── Synonym map for better matching ──────────────────────────────────────
SYNONYMS: Dict[str, List[str]] = {
    "xss": ["cross site scripting", "cross-site scripting", "script injection"],
    "sqli": ["sql injection", "sql inject", "database injection"],
    "sql injection": ["sqli", "sql inject", "database injection"],
    "rce": ["remote code execution", "code execution"],
    "lfi": ["local file inclusion", "file inclusion"],
    "rfi": ["remote file inclusion"],
    "ssrf": ["server side request forgery", "server-side request forgery"],
    "csrf": ["cross site request forgery", "cross-site request forgery"],
    "idor": ["insecure direct object reference", "direct object reference"],
    "dos": ["denial of service", "ddos", "distributed denial of service"],
    "mitm": ["man in the middle", "man-in-the-middle", "adversary in the middle"],
    "apt": ["advanced persistent threat"],
    "cve": ["common vulnerabilities and exposures", "vulnerability database"],
    "ad": ["active directory"],
    "pentest": ["penetration testing", "pen test", "pentesting"],
    "recon": ["reconnaissance", "information gathering", "enumeration"],
    "privesc": ["privilege escalation", "priv esc"],
    "reverse shell": ["revshell", "rev shell", "callback shell"],
    "payload": ["shellcode", "exploit code"],
    "c2": ["command and control", "c&c", "command control"],
    "rat": ["remote access trojan", "remote access tool"],
    "firewall": ["fw", "packet filter", "iptables", "nftables"],
    "ids": ["intrusion detection system", "intrusion detection"],
    "ips": ["intrusion prevention system", "intrusion prevention"],
    "siem": ["security information event management", "security information and event management"],
    "waf": ["web application firewall"],
    "vpn": ["virtual private network"],
    "phishing": ["social engineering", "spear phishing"],
    "malware": ["virus", "trojan", "worm", "ransomware", "spyware"],
    "hash": ["hashing", "md5", "sha1", "sha256", "sha-1", "sha-256"],
    "encryption": ["encrypt", "aes", "rsa", "cipher", "cryptography"],
    "nmap": ["network mapper", "port scan", "port scanner"],
    "burp": ["burp suite", "burpsuite"],
    "metasploit": ["msf", "msfconsole"],
    "hydra": ["brute force", "bruteforce", "password cracking"],
    "john": ["john the ripper", "password cracking"],
    "hashcat": ["hash cracking", "password cracking"],
    "wireshark": ["packet capture", "packet analysis", "pcap"],
    "tcp": ["transmission control protocol"],
    "udp": ["user datagram protocol"],
    "http": ["hypertext transfer protocol"],
    "https": ["http secure", "tls", "ssl"],
    "dns": ["domain name system", "name resolution"],
    "dhcp": ["dynamic host configuration protocol"],
    "arp": ["address resolution protocol"],
    "osint": ["open source intelligence", "open-source intelligence"],
    "ctf": ["capture the flag"],
    "owasp": ["open web application security project"],
    "mitre": ["mitre att&ck", "mitre attack", "att&ck"],
    "zero day": ["0day", "zero-day", "0-day"],
    "exploit": ["exploitation", "exploiting"],
    "vulnerability": ["vuln", "vulnerabilities", "weakness", "flaw"],
    "authentication": ["auth", "login", "sign in", "credentials"],
    "authorization": ["access control", "permissions", "rbac"],
    "kernel": ["kernel exploit", "kernel vulnerability"],
    "buffer overflow": ["bof", "stack overflow", "heap overflow"],
    "rootkit": ["root kit"],
    "backdoor": ["back door", "persistence mechanism"],
    "sandbox": ["sandboxing", "isolation"],
    "forensics": ["digital forensics", "computer forensics", "incident response"],
    "network": ["networking", "network security"],
    "linux": ["unix", "bash", "terminal", "kali"],
    "windows": ["win", "powershell", "cmd", "active directory"],
}

# Stop words to filter out from queries
STOP_WORDS = {
    "what", "is", "a", "an", "the", "how", "do", "does", "can", "i", "you",
    "me", "my", "we", "to", "in", "on", "of", "for", "and", "or", "it",
    "this", "that", "about", "explain", "tell", "describe", "define",
    "please", "could", "would", "should", "give", "show", "list",
    "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "with", "from", "by", "at", "as", "into", "through", "during",
    "before", "after", "between", "out", "up", "down", "some", "any",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "your", "their", "its", "our", "these", "those",
    "mean", "means", "meaning", "work", "works", "working",
    "use", "used", "using", "different", "between", "types",
}


class KnowledgeBase:
    """Loads JSON knowledge files and provides intelligent search with synonyms."""

    def __init__(self, knowledge_dir: str | None = None):
        self.knowledge_dir = knowledge_dir or config.KNOWLEDGE_DIR
        self.topics: Dict[str, Dict[str, Any]] = {}
        self._load_all()

    # ── loading ──────────────────────────────────────────────────────────
    def _load_all(self) -> None:
        """Load every .json file in the knowledge directory."""
        if not os.path.isdir(self.knowledge_dir):
            logger.warning("Knowledge directory not found: %s", self.knowledge_dir)
            return

        for filename in sorted(os.listdir(self.knowledge_dir)):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(self.knowledge_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                for key, value in data.items():
                    self.topics[key] = value
                logger.info("Loaded knowledge file: %s", filename)
            except (json.JSONDecodeError, IOError) as exc:
                logger.error("Failed to load %s: %s", filename, exc)

        logger.info("Knowledge base loaded: %d topics.", len(self.topics))

    # ── query expansion ──────────────────────────────────────────────────
    @staticmethod
    def _expand_query(query: str) -> set:
        """Expand query with synonyms and filter stop words."""
        words = set(re.findall(r'[a-z0-9&]+(?:[-][a-z0-9]+)*', query.lower()))
        # Remove stop words but keep meaningful short words
        meaningful = {w for w in words if w not in STOP_WORDS or len(w) <= 2}
        if not meaningful:
            meaningful = words  # fallback if everything was a stop word

        expanded = set(meaningful)

        # Add synonyms
        full_query = query.lower()
        for key, syns in SYNONYMS.items():
            # Check if the key appears in the query
            if key in full_query:
                expanded.update(key.split())
                for syn in syns:
                    expanded.update(syn.split())
            # Check if any synonym appears in the query
            for syn in syns:
                if syn in full_query:
                    expanded.update(key.split())
                    for s in syns:
                        expanded.update(s.split())

        # Remove stop words from expanded set too
        expanded = {w for w in expanded if w not in STOP_WORDS or len(w) <= 2}
        return expanded if expanded else words

    # ── search ───────────────────────────────────────────────────────────
    def search(self, query: str, top_n: int = 3) -> List[Tuple[str, str, float]]:
        """
        Search the knowledge base with synonym expansion and fuzzy matching.
        Returns a list of (topic_key, matched_content, relevance_score) tuples.
        """
        query_lower = query.lower().strip()
        expanded_words = self._expand_query(query)
        results: List[Tuple[str, str, float]] = []

        for topic_key, topic_data in self.topics.items():
            score = 0.0

            # Check title
            title = topic_data.get("title", "").lower()
            if query_lower in title or title in query_lower:
                score += 15.0
            else:
                title_words = set(re.findall(r'[a-z0-9]+', title))
                overlap = expanded_words & title_words
                score += len(overlap) * 4.0

            # Check keywords
            keywords = [kw.lower() for kw in topic_data.get("keywords", [])]
            for kw in keywords:
                if kw in query_lower or query_lower in kw:
                    score += 8.0
                elif any(w in kw for w in expanded_words if len(w) >= 3):
                    score += 3.0

            # Check content (items / topics / phases / categories / tactics)
            content_dict = self._get_content_dict(topic_data)
            best_section = ""
            best_section_score = 0.0

            for section_name, section_text in content_dict.items():
                section_score = 0.0
                combined = f"{section_name} {section_text}".lower()

                # Exact phrase match in content
                if query_lower in combined:
                    section_score += 12.0
                else:
                    # Word-level matching with expanded terms
                    matched_words = 0
                    for word in expanded_words:
                        if len(word) >= 2 and word in combined:
                            section_score += 2.5
                            matched_words += 1
                    # Bonus for matching multiple words
                    if matched_words >= 2:
                        section_score += matched_words * 1.5

                if section_score > best_section_score:
                    best_section_score = section_score
                    best_section = f"**{section_name}**\n{section_text}"

            score += best_section_score

            if score > 0:
                content = best_section if best_section else topic_data.get("description", "")
                results.append((topic_key, content, score))

        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_n]

    def get_topic_summary(self, topic_key: str) -> str:
        """Return a full summary of a given topic."""
        topic = self.topics.get(topic_key)
        if not topic:
            return f"Topic '{topic_key}' not found."

        lines = [f"# {topic.get('title', topic_key)}", "", topic.get("description", ""), ""]
        content_dict = self._get_content_dict(topic)
        for section, text in content_dict.items():
            lines.append(f"## {section}")
            lines.append(text)
            lines.append("")
        return "\n".join(lines)

    def list_topics(self) -> List[Dict[str, str]]:
        """Return a list of all available topic titles and keys."""
        return [
            {"key": k, "title": v.get("title", k)}
            for k, v in self.topics.items()
        ]

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _get_content_dict(topic_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract the content dictionary from topic data (varies by file structure)."""
        for field in ("items", "topics", "phases", "categories", "tactics"):
            if field in topic_data and isinstance(topic_data[field], dict):
                return topic_data[field]
        return {}
