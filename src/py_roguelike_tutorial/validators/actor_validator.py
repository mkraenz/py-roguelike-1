from typing import Literal

from pydantic import BaseModel


class AiData(BaseModel):
    class_type: Literal["HostileEnemy"]


class FighterData(BaseModel):
    max_hp: int
    defense: int
    power: int


class InventoryData(BaseModel):
    capacity: int | None = None
    items: list[str] | None = None


class LevelData(BaseModel):
    level_up_base: int | None = None
    level_up_factor: int | None = None
    xp_given: int | None = None
    current_level: int | None = None
    current_xp: int | None = None


class EquipmentData(BaseModel):
    weapon: str | None = None
    armor: str | None = None


class ActorData(BaseModel):
    char: str
    color: str
    name: str
    ai: AiData
    fighter: FighterData
    inventory: InventoryData
    level: LevelData
    equipment: EquipmentData
