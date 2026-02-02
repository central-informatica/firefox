import os
import stat
import sys

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

SALT_FILE = "storage/salt.bin"

# NIST SP 800-132 recommends at least 10,000 iterations.
# OWASP 2024 recommends 600,000+ for PBKDF2-SHA256.
PBKDF2_ITERATIONS = 600000


def _set_restrictive_permissions(filepath: str) -> None:
    """
    Set restrictive file permissions (owner read/write only).
    On Windows, this is a no-op as POSIX permissions don't apply.
    """
    if sys.platform != "win32":
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0600


def gerar_chave(password: str = "senha-mestra") -> bytes:
    """
    Generate or load the master key (AES 256 bits).

    Uses PBKDF2-HMAC-SHA256 with 600,000 iterations per NIST/OWASP 2024 guidelines.
    The salt file is protected with restrictive permissions (0600 on Unix).
    """
    os.makedirs("storage", exist_ok=True)

    if not os.path.exists(SALT_FILE):
        salt = os.urandom(16)
        with open(SALT_FILE, "wb") as f:
            f.write(salt)
        # Set restrictive permissions on the salt file
        _set_restrictive_permissions(SALT_FILE)
    else:
        with open(SALT_FILE, "rb") as f:
            salt = f.read()

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    key = kdf.derive(password.encode())
    return key
