import uuid


def temporary_key() -> str:
    return f"RedisCooker:Temporary:{uuid.uuid4()}"
