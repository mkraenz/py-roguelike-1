from __future__ import annotations

import abc
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor


class BtResult(StrEnum):
    Success = "SUCCESS"
    Failure = "FAILURE"
    Running = "RUNNING"


INF = 999999  # for our purposes this is unreachably high


class Blackboard(dict):
    def set(self, key: str, val: Any):
        self[key] = val


class BtNode(abc.ABC):
    def __init__(
        self,
        type: str,
        children: "list[BtNode]",
        blackboard: Blackboard,
        max_children: int = INF,
    ) -> None:
        self.max_children: int = max_children
        self.children: "list[BtNode]" = children
        self.type: str = type
        self.blackboard: dict = blackboard

    @property
    def agent(self) -> Actor:
        return self.blackboard.get("agent")  # type: ignore

    @property
    def player(self) -> Actor:
        return self.blackboard.get("player")  # type: ignore

    @abc.abstractmethod
    def tick(self) -> BtResult:
        pass

    def add_child(self, child: "BtNode") -> None:
        assert (
            len(self.children) + 1 <= self.max_children
        ), f"Too many children added to {self.type} node"
        self.children.append(child)


class BtRoot(BtNode):
    def __init__(self, children: list[BtNode], blackboard: Blackboard):
        super().__init__(type="root", children=children, blackboard=blackboard)

    def tick(self):
        latest_child_res: BtResult
        for child in self.children:
            latest_child_res = child.tick()
            if (
                latest_child_res == BtResult.Failure
                or latest_child_res == BtResult.Running
            ):
                return latest_child_res
        return BtResult.Success


# TODO: consider Reactive Sequence node to add ability for prioritization
class BtSequence(BtNode):
    """Composite node that is basically a logical AND, executing its children serially in order, returning Success if all succeed,
    or stopping execution once the first child fails."""

    def __init__(self, children: list[BtNode], blackboard: Blackboard):
        super().__init__(type="sequence", children=children, blackboard=blackboard)

    def tick(self):
        latest_child_res: BtResult
        for child in self.children:
            latest_child_res = child.tick()
            if (
                latest_child_res == BtResult.Failure
                or latest_child_res == BtResult.Running
            ):
                return latest_child_res
        return BtResult.Success


class BtSelector(BtNode):
    """Aka Fallback. Composite node that executes its children in order, until one returns Success. Otherwise executes the next one.
    This is also the node to implement _explicit success conditions_,
    i.e. before each action check whether the world is already in the desired state,
    for example, before going to a location check whether you are already at that location.
    """

    def __init__(self, children: list[BtNode], blackboard: Blackboard):
        super().__init__(type="selector", children=children, blackboard=blackboard)

    def tick(self):
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Success:
                return BtResult.Success
            # TODO how to handle running?
            # while child_res == BtResult.Running:
            #     yield BtResult.Running

        return BtResult.Failure


class BtParallel(BtNode):
    """Composite node that is basically a logical OR,
    ticking all children and returning Success if any of its children returns success,
    or failure if they all failed."""

    def __init__(self, children: list[BtNode], blackboard: Blackboard):
        super().__init__(type="parallel", children=children, blackboard=blackboard)

    def tick(self):
        res: BtResult = BtResult.Failure
        for child in self.children:
            child_res = child.tick()
            if child_res == BtResult.Success:
                res = BtResult.Success
        return res


class BtAction(BtNode, abc.ABC):
    """Base class to be implemented with the actual actions performed by the AI"""

    def __init__(self, name: str, blackboard: Blackboard):
        """
        Parameters:
            name - display name of this behavior
        """
        super().__init__(
            type="behavior", children=[], max_children=0, blackboard=blackboard
        )
        self.name = name


class BtCondition(BtNode, abc.ABC):
    """Base class to be implemented with condition checks.
    Must not have side-effects, i.e. must not change the world state in any way.
    For conditions, tick() must return either Success or Failure. Running is not allowed!
    """

    def __init__(self, name: str, blackboard: Blackboard):
        """
        Parameters:
            name - display name of this behavior
        """
        super().__init__(
            type="condition", children=[], max_children=0, blackboard=blackboard
        )
        self.name = name


class BtDecorator(BtNode, abc.ABC):
    def __init__(self, type: str, child: BtNode, blackboard: Blackboard):
        super().__init__(
            type=type, children=[child], max_children=1, blackboard=blackboard
        )

    @property
    def child(self) -> BtNode:
        return self.children[0]


class BtInverter(BtDecorator):
    def __init__(self, child: BtNode, blackboard: Blackboard):
        super().__init__(type="inverter", child=child, blackboard=blackboard)

    def tick(self) -> BtResult:
        child_res = self.child.tick()
        if child_res == BtResult.Success:
            return BtResult.Failure
        if child_res == BtResult.Failure:
            return BtResult.Success
        return child_res


class BtForceFailure(BtDecorator):
    def __init__(self, child: BtNode, blackboard: Blackboard):
        super().__init__(type="force-failure", child=child, blackboard=blackboard)

    def tick(self) -> BtResult:
        self.child.tick()
        return BtResult.Failure


class BtSuccessIsFailure(BtDecorator):
    def __init__(self, child: BtNode, blackboard: Blackboard):
        super().__init__(type="success-is-failure", child=child, blackboard=blackboard)

    def tick(self) -> BtResult:
        child_res = self.child.tick()
        if child_res == BtResult.Success:
            return BtResult.Failure
        return child_res
