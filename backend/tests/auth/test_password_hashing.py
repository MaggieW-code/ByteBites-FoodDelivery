import pytest

from backend.app.services.accounts.password_hashing import MalformedPasswordHashError, hash_password, verify_password


def test_hash_is_not_the_password(test_password_hash: str) -> None:
    assert "correct-horse-battery" not in test_password_hash
    assert test_password_hash.startswith("scrypt$")


def test_verify_accepts_right_password_and_rejects_wrong(test_password_hash: str) -> None:
    assert verify_password("correct-horse-battery", test_password_hash) is True
    assert verify_password("Correct-horse-battery", test_password_hash) is False


def test_same_password_gets_a_different_salt_each_time() -> None:
    assert hash_password("same password") != hash_password("same password")


@pytest.mark.parametrize("stored_hash", ["", "bcrypt$abc", "scrypt$16384$8$1$not-base64!$x"])
def test_malformed_hash_raises(stored_hash: str) -> None:
    with pytest.raises(MalformedPasswordHashError):
        verify_password("anything", stored_hash)
