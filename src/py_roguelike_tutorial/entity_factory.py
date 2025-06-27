from typing import Final

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import HostileEnemy
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components import consumable
from py_roguelike_tutorial.components.level import Level
from py_roguelike_tutorial.entity import Actor, Item

SCROLL: Final[str] = "~"


class EntityFactory:
    player_prefab = Actor(
        char="@",
        color=Color.WHITE,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=30, defense=2, power=5),
        inventory=Inventory(26),  # 26 bc of English alphabet
        level=Level(level_up_base=2, level_up_factor=10),
    )
    # enemies
    orc_prefab = Actor(
        char="o",
        color=Color.RED_ROBIN,
        name="Orc",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=10, defense=0, power=3),
        inventory=Inventory.none(),
        level=Level(level_up_base=0, xp_given=35),
    )
    troll_prefab = Actor(
        char="T",
        color=Color.GREEN_DEEP_COOL,
        name="Troll",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=16, defense=1, power=4),
        inventory=Inventory.none(),
        level=Level(level_up_base=0, xp_given=35),
    )

    # items
    health_potion_prefab = Item(
        char="!",
        color=Color.VIOLET,
        name="Health Potion",
        consumable=consumable.HealingConsumable(amount=4),
    )
    lightning_scroll_prefab = Item(
        char=SCROLL,
        color=Color.BLUE,
        name="Lightning Scroll",
        consumable=consumable.LightningDamageConsumable(damage=20, max_range=5),
    )
    confusion_scroll_prefab = Item(
        char=SCROLL,
        color=Color.PINK_INSANITY,
        name="Confusion Scroll",
        consumable=consumable.ConfusionConsumable(turns=10),
    )
    fireball_scroll_prefab = Item(
        char=SCROLL,
        color=Color.RED,
        name="Fireball Scroll",
        consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    )
