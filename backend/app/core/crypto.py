from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Crypto NÃO importa security, NUNCA
ph = PasswordHasher(
    time_cost=3,
    memory_cost=64 * 1024,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_argon2(raw: str) -> str:
    return ph.hash(raw)


def verify_argon2(raw: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, raw)
    except VerifyMismatchError:
        return False
    except Exception:
        return False
