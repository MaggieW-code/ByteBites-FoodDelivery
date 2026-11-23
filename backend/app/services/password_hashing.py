"""Password hashing with the standard library's scrypt. Swap this one file to move to Argon2."""

import base64
import binascii
import hashlib
import hmac
import secrets

SCRYPT_COST = 2**14
SCRYPT_BLOCK_SIZE = 8
SCRYPT_PARALLELISM = 1
SALT_BYTES = 16
HASH_BYTES = 64


class MalformedPasswordHashError(Exception):
    """A stored hash isn't in the `scrypt$cost$block$parallel$salt$hash` format."""


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    derived = _scrypt(password, salt, SCRYPT_COST, SCRYPT_BLOCK_SIZE, SCRYPT_PARALLELISM)
    return "$".join(
        ["scrypt", str(SCRYPT_COST), str(SCRYPT_BLOCK_SIZE), str(SCRYPT_PARALLELISM), _encode(salt), _encode(derived)]
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, cost, block_size, parallelism, salt, expected = stored_hash.split("$")
        if algorithm != "scrypt":
            raise ValueError(f"unsupported algorithm {algorithm!r}")
        derived = _scrypt(password, _decode(salt), int(cost), int(block_size), int(parallelism))
        expected_bytes = _decode(expected)
    except (ValueError, binascii.Error) as error:
        raise MalformedPasswordHashError("Stored password hash is malformed") from error
    return hmac.compare_digest(derived, expected_bytes)


def _scrypt(password: str, salt: bytes, cost: int, block_size: int, parallelism: int) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=cost, r=block_size, p=parallelism, dklen=HASH_BYTES)


def _encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _decode(text: str) -> bytes:
    return base64.b64decode(text, validate=True)
