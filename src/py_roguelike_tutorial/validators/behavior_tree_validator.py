# pyright: strict, reportIncompatibleVariableOverride=false, reportGeneralTypeIssues=false
from __future__ import annotations

import abc
from typing import Literal, Any

from pydantic import BaseModel, Field

type BtChildren = list[
    BtSelectorData
    | BtSequenceData
    | MaxDistanceToPlayerData
    | MeleeAttackBehaviorData
    | MoveTowardsPlayerBehaviorData
    | WaitBehaviorData
    | ActorAttributeEqualsData
    | BlackboardConditionData
    | WriteToBlackboardData
    | SeesPlayerData
    | InverterData
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


class MaxDistanceToPlayerDataParams(BaseModel):
    max_dist: int


class MaxDistanceToPlayerData(BtBehaviorData):
    type: Literal["MaxDistanceToPlayer"]
    params: MaxDistanceToPlayerDataParams


class ActorAttributeEqualsDataParams(BaseModel):
    attribute_name: str
    value: Any


class ActorAttributeEqualsData(BtBehaviorData):
    type: Literal["ActorAttributeEquals"]
    params: ActorAttributeEqualsDataParams


class BlackboardConditionDataParams(BaseModel):
    comparator: Literal["eq", "has"]
    value: Any
    key: str


class BlackboardConditionData(BtBehaviorData):
    type: Literal["BlackboardCondition"]
    params: BlackboardConditionDataParams


class WriteToBlackboardDataParams(BaseModel):
    value: Any
    key: str


class WriteToBlackboardData(BtBehaviorData):
    type: Literal["WriteToBlackboard"]
    params: WriteToBlackboardDataParams


class MeleeAttackBehaviorData(BtBehaviorData):
    type: Literal["MeleeAttack"]


class MoveTowardsPlayerBehaviorData(BtBehaviorData):
    type: Literal["MoveTowardsPlayer"]


class SeesPlayerData(BtBehaviorData):
    type: Literal["SeesPlayer"]


class WaitBehaviorData(BtBehaviorData):
    type: Literal["Wait"]


class BehaviorTreeData(BaseModel):
    root: BtRootData


class InverterData(BtNodeData):
    type: Literal["Inverter"]
    children: BtChildren = Field(max_length=1, min_length=1)
