from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from py_roguelike_tutorial import exceptions
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.exceptions import Impossible
from py_roguelike_tutorial.types import Coord

if TYPE_CHECKING:
    from py_roguelike_tutorial.engine import Engine
    from py_roguelike_tutorial.entity import Entity, Actor, Item


class Action:
    """Command pattern. Named Action to stick with the tutorial notion."""

    def __init__(self, entity: Actor):
        self.entity = entity

    @property
    def engine(self) -> Engine:
        return self.entity.parent.engine

    def perform(self) -> None:
        raise NotImplementedError("subclasses must implement perform")


class WaitAction(Action):
    def perform(self) -> None:
        pass


class EscapeAction(Action):
    def perform(self) -> None:
        sys.exit()


class DirectedAction(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Coord:
        """The destination coordinates."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Entity | None:
        return self.engine.game_map.get_blocking_entity_at(*self.dest_xy)

    @property
    def target_actor(self) -> Actor | None:
        """Returns the target actor at the destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    @property
    def player_is_actor(self) -> bool:
        return self.engine.player == self.entity

    @property
    def player_is_target(self) -> bool:
        return self.engine.player == self.target_actor


class MeleeAction(DirectedAction):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name} hits {target.name}"
        log_color = (
            Theme.player_attacks if self.player_is_actor else Theme.enemy_attacks
        )
        if damage > 0:
            next_hp = target.fighter.hp - damage
            txt = f"{attack_desc} for {damage} HP. {next_hp} HP left."
            self.engine.message_log.add(txt, fg=log_color)
            target.fighter.hp = next_hp
        else:
            txt = f"{attack_desc} but does not damage."
            self.engine.message_log.add(txt, fg=log_color)


class MoveAction(DirectedAction):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy
        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.Impossible("The way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.Impossible("The way is blocked.")
        if self.engine.game_map.get_blocking_entity_at(dest_x, dest_y):
            raise exceptions.Impossible("The way is blocked.")
        self.entity.move(self.dx, self.dy)


class BumpAction(DirectedAction):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        return MoveAction(self.entity, self.dx, self.dy).perform()


class ItemAction(Action):
    def __init__(self, entity: Actor, item: Item, target_xy: Coord | None = None):
        super().__init__(entity)
        self.item = item
        self.target_xy = target_xy if target_xy else (entity.x, entity.y)

    @property
    def target_actor(self) -> Actor | None:
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        self.item.consumable.activate(self)


class PickupAction(Action):
    """Pick up an item and add it to the inventory, if there is enough space."""

    @property
    def target_item(self) -> Item | None:
        return self.engine.game_map.get_item_at_location(*self.entity.pos)

    def perform(self) -> None:
        item = self.target_item
        if not item:
            raise exceptions.Impossible("There is nothing here to pick up.")
        if not self.entity.inventory.has_capacity(1):
            raise exceptions.Impossible("Your backpack is full.")

        self.entity.inventory.add(item)
        self.engine.game_map.entities.remove(item)

        txt = f"You pick up the {item.name}."
        self.engine.message_log.add(txt)


class DropItemAction(ItemAction):
    def perform(self):
        self.entity.inventory.drop(self.item)


class TakeStairsAction(Action):
    def perform(self) -> None:
        """Take the stairs, if any exist at the entity's location."""
        if self.entity.pos != self.engine.game_map.downstairs_location:
            raise Impossible("There are no stairs here.")
        self.engine.game_world.generate_floor()
        self.engine.message_log.add("You descend the staircase.", fg=Theme.descend)
