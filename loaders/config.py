import json
from dtypes.config import Config
from typing import TypedDict, List, Optional

class ConfigLoader:
    def __init__(self, path: str = "./config.json"):
        self.path = path
        self.data: Optional[List[Config]] = None
        self.has_error: bool = False

    def load(self) -> None:
        """Loads and parses the JSON file at the specified path."""
        try:
            with open(self.path, 'r') as f:
                raw = json.load(f)
                self.data = self._parse(raw)
        except FileNotFoundError:
            if not self.has_error:
                print(f"error - {self.path} not found!")

            self.has_error = True
        except json.JSONDecodeError:
            if not self.has_error:
                print(f"error - {self.path} is malformed!")

            self.has_error = True

    def get(self) -> Optional[List[Config]]:
        """Returns the parsed data, or None if not loaded."""
        return self.data

    def validate(self, path: Optional[str] = None, items_to_validate: List[str] = []) -> bool:
        """
        Validates that the config contains certain values. Optionally reloads the config
        from a different path if validation fails initially.
        Specifying certain values will override default functionality
        """
        # override default functionality if items provided
        if len(items_to_validate) > 0:
            values = []
            for item in items_to_validate:
                if path: 
                    self.path = path
                    self.load()

                values.append(self._has_value(item))
            
            if False in values:
                return False
            
            return True

        # validate currently loaded data
        if self._has_value("token"):
            return True

        # validation failed, try reloading the data.
        if path:
            self.path = path
            self.load()

        return self._has_value("token")

    def _has_value(self, value: str = "token") -> bool:
        """Checks if any loaded config contains a value."""
        if not self.data:
            return False

        return any(value in entry for entry in self.data)

    def _parse(self, raw) -> List[Config]:
        """Parses raw JSON data into a list of Config."""
        
        if isinstance(raw, dict):
            raw = [raw]
        
        return [Config(token=entry.get("token", ""), guild_id=entry.get("guild_id", ""), database=entry.get("database", "")) for entry in raw]
