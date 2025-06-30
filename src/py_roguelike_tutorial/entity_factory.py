from typing import Final

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import HostileEnemy
from py_roguelike_tutorial.components.equipment import Equipment
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components.level import Level
from py_roguelike_tutorial.entity import Actor, Item

SCROLL: Final[str] = "~"


class EntityPrefabs:
    player = Actor(
        char="@",
        color=Color.WHITE,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(max_hp=30, defense=2, power=5),
        inventory=Inventory(26),  # 26 bc of English alphabet
        level=Level(level_up_base=30, level_up_factor=10),
        equipment=Equipment(),
    )
    npcs: dict[str, Actor] = {
        "orc": Actor(
            char="o",
            color=Color.GREEN_ORC,
            name="Orc",
            ai_cls=HostileEnemy,
            fighter=Fighter(max_hp=10, defense=0, power=3),
            inventory=Inventory.none(),
            level=Level(level_up_base=0, xp_given=15),
            equipment=Equipment(),
        ),
        "troll": Actor(
            char="T",
            color=Color.GREEN_DEEP_COOL,
            name="Troll",
            ai_cls=HostileEnemy,
            fighter=Fighter(max_hp=16, defense=1, power=4),
            inventory=Inventory.none(),
            level=Level(level_up_base=0, xp_given=35),
            equipment=Equipment(),
        ),
    }
    items: dict[str, Item] = {}
