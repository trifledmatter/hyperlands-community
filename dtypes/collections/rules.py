from typing import TypedDict, List

from database import MongoDB
from config import get_config_or_throw
from datetime import datetime


# instantiate the database
db = MongoDB(get_config_or_throw("database"), "community")


class Rules(TypedDict):
    name: str
    title: str
    author: str
    description: str
    tags: List[str]
    timestamp: datetime


def save(data: Rules):
    db.insert_one(
        "rules",
        {
            "name": data.get("name"),
            "title": data.get("title"),
            "author": data.get("author"),
            "description": data.get("description"),
            "tags": data.get("tags"),
            "timestamp": datetime.now(),
        },
    )


def find_rule_by_name(name: str):
    return db.find_one("rules", {"name": name.strip().lower()})


def remove_rule_by_name(name: str):
    rule = find_rule_by_name(name.strip().lower())
    db.delete_one("rules", {"name": name.strip().lower()})

    return rule


def get_rules() -> List[Rules]:
    return db.get_all("rules")
