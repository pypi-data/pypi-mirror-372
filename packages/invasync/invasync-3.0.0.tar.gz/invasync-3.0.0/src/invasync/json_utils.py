import json
from pathlib import Path

from .models import User


def load_json(users_json: Path) -> list[User]:
    data = json.loads(users_json.read_text(encoding="utf-8"))
    return [User(**user) for user in data]


def save_json(users_json: Path, users: list[User]) -> None:
    users_json.write_text(
        json.dumps([user.to_dict() for user in users], indent=2),
        encoding="utf-8",
    )
