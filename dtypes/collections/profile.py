from typing import TypedDict, Any
from datetime import datetime

from database import MongoDB
from config import get_config_or_throw

db = MongoDB(get_config_or_throw("database"), "community")


class CommunityProfile(TypedDict):
    name: str
    user_id: str

    level: int

    nickname: str
    color: str

    timestamp: datetime

    last_edited_message: str = None
    last_deleted_message: str = None


def save(data: CommunityProfile):
    db.insert_one(
        "profiles",
        {
            "name": data.get("name"),
            "user_id": data.get("user_id"),
            "level": data.get("level"),
            "nickname": data.get("nickname"),
            "color": data.get("color"),
            "timestamp": datetime.now(),
            "last_edited_message": data.get("last_edited_message") or "none",
            "last_deleted_message": data.get("last_deleted_message") or "none",
        },
    )


def find_profile_by_id(id: str):
    return db.find_one("profiles", {"user_id": id})

def update_profile_by_id(profile_id: str, k: str, v: Any):
    profile = db.update_one("profiles", {"user_id": f"{profile_id}"}, {k: v})

    print(profile)
    return profile
