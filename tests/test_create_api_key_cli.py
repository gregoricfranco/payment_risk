import hashlib

from app.cli.create_api_key import generate_api_key


def test_generate_api_key_returns_matching_hash() -> None:
    generated = generate_api_key()

    assert generated.raw_key.startswith("prk_")
    assert generated.prefix == generated.raw_key[:32]
    assert generated.key_hash == hashlib.sha256(generated.raw_key.encode("utf-8")).hexdigest()
    assert len(generated.key_hash) == 64
