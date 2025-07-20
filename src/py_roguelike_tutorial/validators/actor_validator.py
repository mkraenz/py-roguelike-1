from typing import Literal

from pydantic import BaseModel


class VisionData(BaseModel):
    range: int


class BehaviorTreeAIData(BaseModel):
    class_type: Literal["BehaviorTreeAI"]
    behavior_tree_id: str
    vision: VisionData
    interests: list[str]


class HostileEnemyData(BaseModel):
    class_type: Literal["HostileEnemy"]


AiData = BehaviorTreeAIData | HostileEnemyData


class FighterData(BaseModel):
    max_hp: int
    defense: int
    power: int


class RangedData(BaseModel):
    power: int
    range: int


class InventoryData(BaseModel):
    capacity: int = 0
    items: list[str] = []


class LevelData(BaseModel):
    level_up_base: int = 0
    level_up_factor: int = 150
    xp_given: int = 0
    current_level: int = 1
    current_xp: int = 0


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
    ranged: RangedData | None = None
    move_stepsize: int = 1
    tags: list[str]
