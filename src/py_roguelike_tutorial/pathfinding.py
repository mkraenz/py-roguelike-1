from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import tcod

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.types import Coord


def find_path(from_: Coord, to: Coord, engine: Engine) -> list[Coord]:
    """Returns the list of coordinates to the destination, or an empty list if there is no such path."""
    cost = np.array(engine.game_map.tiles["walkable"], dtype=np.int8)

    for entity in engine.game_map.entities:
        if entity.blocks_movement and cost[entity.x, entity.y]:
            # we add to the cost of a blocked position. A lower number means more enemies will crowd behind
            # each other in hallways. Higher number means they will take longer paths towards the destination.
            cost[entity.x, entity.y] += 10
    graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
    pathfinder = tcod.path.Pathfinder(graph)
    pathfinder.add_root(from_)
    # path_to includes the start and ending points. we strip away the start point
    path: list[list[int]] = pathfinder.path_to(to)[1:].tolist()
    return [(index[0], index[1]) for index in path]
