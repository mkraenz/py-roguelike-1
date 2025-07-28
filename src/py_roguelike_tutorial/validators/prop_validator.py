from typing import Literal

from pydantic import BaseModel

from py_roguelike_tutorial.validators.actor_validator import HealthData, InventoryData


class InteractableData(BaseModel):
    class_type: Literal["Chest"]


class PropData(BaseModel):
    char: str
    color: str
    name: str
    health: HealthData
    interactable: InteractableData
    inventory: InventoryData
    tags: list[str]
