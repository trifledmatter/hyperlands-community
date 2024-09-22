from enum import Enum, auto

class Role(Enum):
    FOUNDER = 1284871184198008894
    ADMINISTRATORS = 1284866415748321321

    @staticmethod
    def from_string(role_str: str) -> 'Role':
        try:
            return Role[role_str.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role_str}")

    def to_int(self) -> int:
        return self.value