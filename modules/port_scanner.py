"""
Port Scanner — TCP connect scan using Python sockets.
Educational tool for understanding port scanning concepts.
"""

import socket
import logging
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Well-known ports to scan by default
DEFAULT_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
    993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017,
]

PORT_SERVICES = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPCbind", 135: "MSRPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
}


class PortScanner:
    """Educational TCP connect scanner."""

    def __init__(self, timeout: float = 1.5, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers

    def _scan_port(self, host: str, port: int) -> Tuple[int, bool, str]:
        """Attempt a TCP connect to host:port. Returns (port, is_open, service)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                is_open = result == 0
                service = PORT_SERVICES.get(port, "unknown")
                return port, is_open, service
        except socket.error:
            return port, False, ""

    def run(self, target: str, start_port: int = 0, end_port: int = 0) -> str:
        """
        Scan ports on the target host.
        If start/end are 0, scan DEFAULT_PORTS.
        """
        # Resolve hostname
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            return f"❌ Could not resolve host: {target}"

        if start_port and end_port:
            ports = list(range(start_port, end_port + 1))
        else:
            ports = DEFAULT_PORTS

        logger.info("Scanning %s (%s) — %d ports", target, ip, len(ports))

        open_ports: List[Tuple[int, str]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._scan_port, ip, port): port
                for port in ports
            }
            for future in as_completed(futures):
                port, is_open, service = future.result()
                if is_open:
                    open_ports.append((port, service))

        open_ports.sort()

        # Format results
        lines = [f"🔍 **Port Scan Results for {target} ({ip})**", ""]
        if open_ports:
            lines.append(f"Found **{len(open_ports)}** open port(s):\n")
            lines.append("| Port  | Service     | State |")
            lines.append("|-------|-------------|-------|")
            for port, service in open_ports:
                lines.append(f"| {port:<5} | {service:<11} | OPEN  |")
        else:
            lines.append("No open ports found in the scanned range.")

        lines.append(f"\nScanned {len(ports)} port(s) total.")
        return "\n".join(lines)
