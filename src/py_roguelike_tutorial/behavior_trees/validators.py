# pyright: strict, reportIncompatibleVariableOverride=false, reportGeneralTypeIssues=false
from __future__ import annotations

import abc
from typing import Literal, Any

from pydantic import BaseModel, Field

type BtChildren = list[
    BtSelectorData
    | BtSequenceData
    | DistanceToPlayerData
    | SimpleBehaviorData
    | ActorAttributeEqualsData
    | BlackboardConditionData
    | WriteToBlackboardData
    | InverterData
    | HasItemData
    | UseItemData
    | HealthConditionData
    | SubtreeData
    | WriteItemPosInVicinityData
    | MoveToEntityData
    | PickUpItemData
    | EquipItemData
]


class BtNodeData(BaseModel, abc.ABC):
    children: BtChildren | None = None
    type: str
    params: object | None = None
    comment: str | None = None
    """Freetext comment to help make the subtrees more readable at runtime."""


class BtRootData(BtNodeData):
    type: Literal["Root"]
    children: BtChildren = Field(min_length=1)


class BtSelectorData(BtNodeData):
    type: Literal["Selector"]
    children: BtChildren = Field(min_length=1)


class BtSequenceData(BtNodeData):
    type: Literal["Sequence"]
    children: BtChildren = Field(min_length=1)


class BtBehaviorData(BtNodeData):
    children: None = None


class SimpleBehaviorData(BtBehaviorData):
    type: Literal[
        "MeleeAttack",
        "RangedAttack",
        "MoveTowardsPlayer",
        "SeesPlayer",
        "Wait",
        "RandomMove",
        "HasItemAtPosition",
    ]


class DistanceToPlayerDataParamsA(BaseModel):
    max_dist: int
    min_dist: int = 0


class DistanceToPlayerDataParamsB(BaseModel):
    max_dist: int = 999999999  # de facto infinite
    min_dist: int


DistanceToPlayerDataParams = DistanceToPlayerDataParamsA | DistanceToPlayerDataParamsB


class DistanceToPlayerData(BtBehaviorData):
    type: Literal["DistanceToPlayer"]
    params: DistanceToPlayerDataParamsA | DistanceToPlayerDataParamsB
    """WORKAROUND: At least one of the params max_dist or min_dist must be provided. 
    Unfortunately, there is no perfect way to do that in pydantic."""


class ActorAttributeEqualsDataParams(BaseModel):
    attribute_name: str
    value: Any


class ActorAttributeEqualsData(BtBehaviorData):
    type: Literal["ActorAttributeEquals"]
    params: ActorAttributeEqualsDataParams


class BlackboardConditionDataParams(BaseModel):
    comparator: Literal["eq", "has"]
    """The comparison operator: 
      - eq = equals
      - has = whether the key exists
    """
    value: Any
    """The value that blackboard[key] is being compared to."""
    key: str
    """The key in the blackboard to access"""


class HasItemDataParams(BaseModel):
    item_kind: str


class HasItemData(BtBehaviorData):
    type: Literal["HasItem"]
    params: HasItemDataParams


class UseItemDataParams(BaseModel):
    item_kind: str


class UseItemData(BtBehaviorData):
    type: Literal["UseItem"]
    params: UseItemDataParams


class PickUpItemDataParams(BaseModel):
    key: str


class PickUpItemData(BtBehaviorData):
    type: Literal["PickUpItem"]
    params: PickUpItemDataParams


class EquipItemDataParams(BaseModel):
    id: str


class EquipItemData(BtBehaviorData):
    type: Literal["EquipItem"]
    params: EquipItemDataParams


class BlackboardConditionData(BtBehaviorData):
    type: Literal["BlackboardCondition"]
    params: BlackboardConditionDataParams


class WriteToBlackboardDataParams(BaseModel):
    value: Any
    key: str


class WriteToBlackboardData(BtBehaviorData):
    type: Literal["WriteToBlackboard"]
    params: WriteToBlackboardDataParams


class HealthConditionDataParams(BaseModel):
    value_percent: float = Field(ge=0, le=100)
    comparator: Literal["leq"]


class HealthConditionData(BtBehaviorData):
    type: Literal["HealthCondition"]
    params: HealthConditionDataParams


class SubtreeDataParams(BaseModel):
    id: str


class SubtreeData(BtNodeData):
    type: Literal["Subtree"]
    params: SubtreeDataParams


class InverterData(BtNodeData):
    type: Literal["Inverter"]
    children: BtChildren = Field(max_length=1, min_length=1)


class WriteItemPosInVicinityDataParams(BaseModel):
    write_to_blackboard_key: str
    look_for_kind: str
    radius: int


class WriteItemPosInVicinityData(BtBehaviorData):
    type: Literal["WriteItemPosInVicinity"]
    params: WriteItemPosInVicinityDataParams


class MoveToEntityDataParams(BaseModel):
    to: str


class MoveToEntityData(BtBehaviorData):
    type: Literal["MoveToEntity"]
    params: MoveToEntityDataParams


class BehaviorTreeData(BaseModel):
    root: BtRootData
