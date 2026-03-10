"""
Hash Cracker Helper — hash identification and educational dictionary attack.
This module identifies hash types and attempts matching against a small built-in
dictionary for educational purposes only.
"""

import hashlib
import re
import logging

logger = logging.getLogger(__name__)

# Hash type identification patterns
HASH_PATTERNS = [
    (re.compile(r"^[a-fA-F0-9]{32}$"), "MD5", "md5"),
    (re.compile(r"^[a-fA-F0-9]{40}$"), "SHA-1", "sha1"),
    (re.compile(r"^[a-fA-F0-9]{64}$"), "SHA-256", "sha256"),
    (re.compile(r"^[a-fA-F0-9]{128}$"), "SHA-512", "sha512"),
    (re.compile(r"^\$2[aby]?\$.{56}$"), "bcrypt", None),
    (re.compile(r"^\$6\$"), "SHA-512 (crypt)", None),
    (re.compile(r"^\$5\$"), "SHA-256 (crypt)", None),
    (re.compile(r"^\$1\$"), "MD5 (crypt)", None),
    (re.compile(r"^[a-fA-F0-9]{96}$"), "SHA-384", "sha384"),
]

# Small educational dictionary — intentionally limited
EDUCATIONAL_DICTIONARY = [
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine", "ashley",
    "bailey", "shadow", "123123", "654321", "superman",
    "qazwsx", "michael", "football", "password1", "password123",
    "admin", "root", "toor", "test", "guest",
    "changeme", "welcome", "hello", "secret", "pass",
]


class HashCrackerHelper:
    """Identify hash types and attempt educational dictionary matching."""

    def _identify_hash(self, hash_value: str) -> list:
        """Identify the probable hash type(s)."""
        matches = []
        for pattern, name, algo in HASH_PATTERNS:
            if pattern.match(hash_value):
                matches.append((name, algo))
        return matches

    def _try_dictionary(self, hash_value: str, algorithm: str) -> str | None:
        """Try to match the hash against the educational dictionary."""
        hash_lower = hash_value.lower()
        for word in EDUCATIONAL_DICTIONARY:
            try:
                computed = hashlib.new(algorithm, word.encode("utf-8")).hexdigest()
                if computed == hash_lower:
                    return word
            except ValueError:
                break
        return None

    def run(self, hash_value: str) -> str:
        """Identify hash type and attempt dictionary matching."""
        hash_value = hash_value.strip()

        if not hash_value:
            return "❌ Please provide a hash value."

        lines = [f"🔐 **Hash Analysis**", ""]
        lines.append(f"**Input:** `{hash_value[:80]}{'…' if len(hash_value) > 80 else ''}`")
        lines.append(f"**Length:** {len(hash_value)} characters")
        lines.append("")

        # Identify hash type
        matches = self._identify_hash(hash_value)

        if not matches:
            lines.append("**Hash type:** ❓ Unknown format")
            lines.append("\nThe hash does not match any common hash patterns.")
            return "\n".join(lines)

        lines.append("**Possible hash type(s):**")
        for name, algo in matches:
            lines.append(f"  • {name}")
        lines.append("")

        # Try dictionary attack for supported algorithms
        cracked = None
        for name, algo in matches:
            if algo:
                result = self._try_dictionary(hash_value, algo)
                if result:
                    cracked = (result, name)
                    break

        if cracked:
            word, algo_name = cracked
            lines.append(f"⚠️ **Dictionary match found!**")
            lines.append(f"  • Plaintext: `{word}`")
            lines.append(f"  • Algorithm: {algo_name}")
            lines.append("")
            lines.append("🔒 *This password was found in a common wordlist and is extremely weak.*")
            lines.append("*Recommendation: Use a strong, unique password with 12+ characters.*")
        else:
            lines.append("✅ **No match in educational dictionary.**")
            lines.append("*The hash was not found in the basic built-in wordlist.*")
            lines.append("*For thorough hash cracking, use tools like Hashcat or John the Ripper.*")

        return "\n".join(lines)
