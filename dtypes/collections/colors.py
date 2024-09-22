from typing import TypedDict, List

from database import MongoDB
from config import get_config_or_throw
from datetime import datetime


# instantiate the database
db = MongoDB(get_config_or_throw("database"), "community")


class ProfileColors(TypedDict):
    name: str
    value: str
    author: str


def save(data: ProfileColors):
    db.insert_one(
        "colors",
        {
            "name": data.get("name"),
            "value": data.get("value"),
            "author": data.get("author"),
        },
    )


def find_color_by_name(name: str):
    return db.find_one("colors", {"name": name.strip().lower()})


def remove_color_by_name(name: str):
    rule = find_color_by_name(name.strip().lower())
    db.delete_one("colors", {"name": name.strip().lower()})

    return rule


def get_colors() -> List[ProfileColors]:
    return db.get_all("colors")
