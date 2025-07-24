from __future__ import annotations

import abc
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar

from py_roguelike_tutorial.behavior_trees.blackboard import (
    Blackboard,
    BlackboardSpecialKey,
)

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Actor

__all__ = [
    "BtResult",
    "Blackboard",
    "BtConstructorArgs",
    "BtNode",
    "BtRoot",
    "BtSequence",
    "BtSelector",
    "BtParallel",
    "BtAction",
    "BtCondition",
    "BtInverter",
    "BtDecorator",
    "BtForceFailure",
    "BtForceSuccess",
    "BtSuccessIsFailure",
]


class BtResult(StrEnum):
    Success = "SUCCESS"
    Failure = "FAILURE"
    Running = "RUNNING"


INF = 999999  # for our purposes this is unreachably high


T = TypeVar("T")


class BtConstructorArgs(Generic[T], NamedTuple):
    children: list[BtNode]
    params: T


class BtNode(abc.ABC):
    # we are injecting blackboard after creating the tree, and propagate it to all children.
    # The alternative of having blackboard in every single node constructor was too boilerplatey
    _blackboard: Blackboard

    def __init__(
        self,
        children: "list[BtNode]",
        max_children: int = INF,
    ) -> None:
        self.max_children: int = max_children
        self.children: "list[BtNode]" = children
        if len(self.children) > self.max_children:
            raise ValueError(
                f"Too many children provided. behavior tree node type: {self.class_name},"
                f" num children: {len(self.children)}, max children: {self.max_children}"
            )

    @property
    def class_name(self):
        return type(self).__name__

    @property
    def blackboard(self) -> Blackboard:
        return self._blackboard

    @blackboard.setter
    def blackboard(self, val: Blackboard) -> None:
        self._blackboard = val
        for child in self.children:
            child.blackboard = self._blackboard

    @property
    def agent(self) -> Actor:
        key = BlackboardSpecialKey.Agent
        return self.blackboard.get(key)  # type: ignore[reportReturnType]

    @property
    def player(self) -> Actor:
        key = BlackboardSpecialKey.Player
        return self.blackboard.get(key)  # type: ignore[reportReturnType]

    @property
    def engine(self) -> Engine:
        key = BlackboardSpecialKey.Engine
        return self.blackboard.get(key)  # type: ignore[reportReturnType]

    @abc.abstractmethod
    def tick(self) -> BtResult:
        pass

    def maybe_read_blackboard(self, input: Any) -> tuple[Any, bool]:
        if isinstance(input, str) and input.startswith("$"):
            return self.blackboard.get(input[1:]), True
        return input, False

    def remove_from_blackboard(self, input: Any) -> None:
        self.blackboard.remove(input[1:])


class BtRoot(BtNode):
    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=args.children)

    def tick(self):
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Failure or child_res == BtResult.Running:
                return child_res
        return BtResult.Success


class BtSequence(BtNode):
    """Composite node that is basically a logical AND, executing its children serially in order, returning Success if all succeed,
    or stopping execution once the first child fails."""

    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=args.children)

    def tick(self):
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Failure or child_res == BtResult.Running:
                return child_res
        return BtResult.Success


class BtSelector(BtNode):
    """Aka Fallback. Composite node that executes its children in order, until one returns Success. Otherwise executes the next one.
    This is also the node to implement _explicit success conditions_,
    i.e. before each action check whether the world is already in the desired state,
    for example, before going to a location check whether you are already at that location.
    """

    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=args.children)

    def tick(self):
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Success:
                return BtResult.Success
        return BtResult.Failure


class BtParallel(BtNode):
    """Composite node that is basically a logical OR,
    ticking all children and returning Success if any of its children returns success,
    or failure if they all failed."""

    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=args.children)

    def tick(self):
        res: BtResult = BtResult.Failure
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Success:
                res = BtResult.Success
        return res


class BtAction(BtNode, abc.ABC):
    """Base class to be implemented with the actual actions performed by the AI"""

    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=[], max_children=0)


class BtCondition(BtNode, abc.ABC):
    """Base class to be implemented with condition checks.
    Must not have side-effects, i.e. must not change the world state in any way.
    For conditions, tick() must return either Success or Failure. Running is not allowed!
    """

    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=[], max_children=0)

    def success_else_fail(self, successful: bool) -> BtResult:
        return BtResult.Success if successful else BtResult.Failure


class BtDecorator(BtNode, abc.ABC):
    def __init__(self, args: BtConstructorArgs):
        super().__init__(children=args.children, max_children=1)

    @property
    def child(self) -> BtNode:
        return self.children[0]


class BtInverter(BtDecorator):
    def tick(self) -> BtResult:
        child_res = self.child.tick()
        if child_res == BtResult.Success:
            return BtResult.Failure
        if child_res == BtResult.Failure:
            return BtResult.Success
        return child_res


class BtForceFailure(BtDecorator):
    def tick(self) -> BtResult:
        self.child.tick()
        return BtResult.Failure


class BtForceSuccess(BtDecorator):
    def tick(self) -> BtResult:
        self.child.tick()
        return BtResult.Success


class BtSuccessIsFailure(BtDecorator):
    def tick(self) -> BtResult:
        child_res = self.child.tick()
        if child_res == BtResult.Success:
            return BtResult.Failure
        return child_res
