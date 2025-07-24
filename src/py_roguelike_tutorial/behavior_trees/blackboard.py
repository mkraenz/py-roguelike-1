from enum import StrEnum
from typing import Any

__all__ = [
    "BlackboardSpecialKey",
    "Blackboard",
]


class BlackboardSpecialKey(StrEnum):
    Engine = "__engine__"
    Agent = "__agent__"
    Player = "__player__"
    SpawnLocation = "__spawn_location__"
    Vision = "vision:"


to_vision_tag = lambda tag: f"{BlackboardSpecialKey.Vision.value}{tag}"


class Blackboard(dict[str, Any]):
    def set(self, key: str, val: Any) -> None:
        self[key] = val

    def set_from_version(self, key: str, val: Any):
        self.set(to_vision_tag(key), val)

    def has(self, key: str) -> bool:
        return key in self or to_vision_tag(key) in self

    def remove(self, key: str) -> None:
        if key in self:
            del self[key]

    def clear_vision(self):
        for key in list(self.keys()):
            if key.startswith(BlackboardSpecialKey.Vision.value):
                del self[key]

    def get(self, key: str, default: Any | None = None, /) -> Any:
        """
        Retrieve a value from the blackboard using the specified key. If the key is not found,
        attempt to retrieve a value using a special vision-prefixed key.

        Args:
            key (str): The key to look up in the blackboard.
            default (Any): The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key, or the value associated with the vision-prefixed key,
            or the default value if neither is found.
        """
        val = super().get(key)
        if val is not None:
            return val
        val2 = super().get(f"{BlackboardSpecialKey.Vision.value}{key}", default)
        return val2
