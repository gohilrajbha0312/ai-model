"""
Password Strength Checker Module.
"""

import re
import math
import logging

logger = logging.getLogger(__name__)


class PasswordStrengthChecker:
    """Evaluates the strength of a given password."""

    def run(self, password: str) -> str:
        """Calculate password entropy and check policies."""
        if not password:
            return "❌ Empty password provided."

        length = len(password)
        pool = 0

        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digits = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^a-zA-Z\d]', password))

        if has_lower:
            pool += 26
        if has_upper:
            pool += 26
        if has_digits:
            pool += 10
        if has_special:
            pool += 32

        # Calculate entropy: E = L * log2(R)
        entropy = length * math.log2(pool) if pool > 0 else 0

        if entropy < 40:
            rating = "🔴 Weak"
            message = "Can be cracked instantly. Do not use."
        elif entropy < 60:
            rating = "🟠 Moderate"
            message = "Can be cracked. Use a longer password or add special characters."
        elif entropy < 80:
            rating = "🟡 Good"
            message = "Strong for most standard purposes."
        else:
            rating = "🟢 Excellent"
            message = "Very strong against brute-force attacks."

        res = [
            f"🔐 **Password Strength Analysis**",
            f"**Length:** {length} characters",
            f"**Entropy:** ~{int(entropy)} bits",
            f"**Rating:** {rating}",
            "",
            f"*{message}*"
        ]
        return "\n".join(res)
