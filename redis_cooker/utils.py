import uuid


def temporary_key() -> str:
    return f"RedisCooker:TemporaryKey:{uuid.uuid4()}"
