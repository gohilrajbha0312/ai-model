"""
Encryption Manager — Fernet-based encrypt / decrypt with auto-generated key.
"""

import os
import logging
from cryptography.fernet import Fernet

import config

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Encrypt and decrypt strings using Fernet symmetric encryption."""

    def __init__(self, key_path: str | None = None):
        self.key_path = key_path or config.ENCRYPTION_KEY_PATH
        self._fernet = Fernet(self._load_or_create_key())

    # ── key management ───────────────────────────────────────────────────
    def _load_or_create_key(self) -> bytes:
        """Load the Fernet key from disk, or generate + persist one."""
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        if os.path.isfile(self.key_path):
            with open(self.key_path, "rb") as fh:
                key = fh.read().strip()
                logger.debug("Encryption key loaded from %s", self.key_path)
                return key

        key = Fernet.generate_key()
        with open(self.key_path, "wb") as fh:
            fh.write(key)
        # Restrict permissions on the key file
        os.chmod(self.key_path, 0o600)
        logger.info("New encryption key generated and saved to %s", self.key_path)
        return key

    # ── public API ───────────────────────────────────────────────────────
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a UTF-8 string and return the base64-encoded ciphertext."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext and return the original string."""
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
