from typing import TypedDict, Callable, Awaitable

class CommandFormat(TypedDict):
    name: str
    description: str
    predicate: Callable[..., Awaitable]