from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from py_roguelike_tutorial.handlers.area_ranged_attack_handler import (
    AreaRangedAttackHandler,
)
from py_roguelike_tutorial.handlers.base_event_handler import ActionOrHandler
from py_roguelike_tutorial.handlers.single_ranged_attack_handler import (
    SingleRangedAttackHandler,
)
import py_roguelike_tutorial.validators.item_validator as validators
from py_roguelike_tutorial import tile_types
from py_roguelike_tutorial.actions import Action, ItemAction
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.components.ai import ConfusedEnemy
from py_roguelike_tutorial.components.base_components import BaseComponent
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.exceptions import Impossible

if TYPE_CHECKING:
    from py_roguelike_tutorial.entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item  # type: ignore [reportIncompatibleVariableOverride]
    charges: int = 1

    def get_action(self, consumer: Actor) -> ActionOrHandler | None:
        """Return the action for this item."""
        return ItemAction(consumer, self.parent)

    def activate(self, ctx: Action) -> None:
        """Invoke the item's ability."""
        raise NotImplementedError("Must be implemented by subclass")

    def consume(self) -> None:
        """Reduce the amount of charges.
        If this is the final or only charge, remove the used consumable from its containing inventory.
        """
        self.charges -= 1
        if self.charges <= 0:
            item = self.parent
            inventory = item.parent
            if isinstance(inventory, Inventory):
                inventory.remove(item)


class HealingConsumable(Consumable):
    def __init__(self, data: validators.HealingConsumableConstructorData):
        self.amount = data.amount
        self.charges = data.charges

    def activate(self, ctx: Action) -> None:
        consumer = ctx.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            txt = f"{ctx.entity.name} consumes the {self.parent.name}, and recovers {amount_recovered} HP (-> {consumer.fighter.hp} HP)."
            self.engine.message_log.add(text=txt, fg=Theme.health_recovered)
            self.consume()
        else:
            raise Impossible("You are at full health already.")


class LightningDamageConsumable(Consumable):
    """Lightning attacks automatically pick the closest target within range."""

    def __init__(self, data: validators.LightningDamageConsumableConstructorData):
        self.max_range = data.max_range
        self.damage = data.damage
        self.charges = data.charges

    def activate(self, ctx: ItemAction) -> None:  # type: ignore [reportIncompatibleMethodOverride]
        consumer = ctx.entity
        target = self._closest_enemy_in_range(consumer)

        if not target:
            raise Impossible("No enemy is close enough to strike.")

        txt = f"A lightning bolt stikes the {target.name} with a loud thunder for {self.damage} damage."
        self.engine.message_log.add(txt)
        target.fighter.take_damage(self.damage)
        self.consume()

    def _closest_enemy_in_range(self, consumer: Actor) -> Actor | None:
        target: Actor | None = None
        closest_distance = self.max_range + 1
        for actor in self.engine.game_map.visible_actors:
            if actor is consumer:
                continue
            distance = consumer.dist_euclidean(actor)
            if distance < closest_distance:
                closest_distance = distance
                target = actor
        return target


class ConfusionConsumable(Consumable):
    def __init__(self, data: validators.ConfusionConsumableConstructorData):
        self.turns = data.turns
        self.charges = data.charges

    def get_action(self, consumer: Actor) -> SingleRangedAttackHandler:
        self.engine.message_log.add("Select a target location.", Theme.needs_target)
        return SingleRangedAttackHandler(
            self.engine,
            callback=lambda coord: ItemAction(consumer, self.parent, coord),
        )

    def activate(self, ctx: ItemAction) -> None:  # type: ignore [reportIncompatibleMethodOverride]
        consumer = ctx.entity
        target = ctx.target_actor

        if not self.engine.game_map.visible[ctx.target_xy]:
            self.engine.message_log.add("Cannot select area you cannot see.")
            return
        if not target:
            self.engine.message_log.add("You must select an enemy to target.")
            return
        if target is consumer:
            self.engine.message_log.add("You cannot target yourself.")
            return

        txt = f"{target.name} starts to stumble around aimlessly."
        self.engine.message_log.add(txt, fg=Theme.status_effect_applied)
        target.ai = ConfusedEnemy(previous_ai=target.ai, turns_remaining=self.turns)
        self.consume()


class FireballDamageConsumable(Consumable):
    """AOE Fireball attack. May inflict damage onto the user!"""

    def __init__(self, data: validators.FireballDamageConsumableConstructorData):
        self.damage = data.damage
        self.radius = data.radius
        self.charges = data.charges

    def get_action(self, consumer: Actor) -> AreaRangedAttackHandler | None:
        self.engine.message_log.add("Select a target location.", Theme.needs_target)
        return AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: ItemAction(consumer, self.parent, xy),
        )

    def activate(self, ctx: ItemAction) -> None:  # type: ignore [reportIncompatibleMethodOverride]
        xy = ctx.target_xy

        if not self.engine.game_map.visible[xy]:
            self.log("Cannot target area you cannot see.")
            return

        some_target_hit = False
        # explicitly using actors and not visible_actors because we can target at the corner of the fog of war
        # and the spell may hit enemies hidden inside fog of war
        for actor in self.engine.game_map.actors:
            if actor.dist_chebyshev_pos(*xy) <= self.radius:
                self.log(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {self.damage} damage."
                )
                actor.fighter.take_damage(self.damage)
                some_target_hit = True

        if not some_target_hit:
            raise Impossible("There are no targets in the radius.")
        self.consume()


class TeleportSelfConsumable(Consumable):
    def __init__(self, data: validators.TeleportSelfConsumableConstructorData):
        self.radius = data.radius
        self.charges = data.charges

    def activate(self, ctx: Action) -> None:
        consumer = ctx.entity
        map = self.engine.game_map
        width, height = map.tiles.shape
        # avoid getting negative numbers because that would iterate from the end of the array
        offset_x = max(consumer.x - self.radius, 0)
        offset_y = max(consumer.y - self.radius, 0)
        tiles_in_range = map.tiles[
            offset_x : min(consumer.x + self.radius, width),
            offset_y : min(consumer.y + self.radius, height),
        ]
        floor_tile_indexes = np.argwhere(tiles_in_range == tile_types.floor)
        rand_index = self.engine.np_rng.choice(floor_tile_indexes)
        new_pos = rand_index + (offset_x, offset_y)

        consumer.pos = new_pos
        self.log(
            f"The {self.parent.name} crumbles to pieces."
            f"Suddenly, the air flutters about as the {consumer.name} vanishes and reappears nearby."
        )

        self.consume()
