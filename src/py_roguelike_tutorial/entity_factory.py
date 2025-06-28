from typing import Final

from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import HostileEnemy
from py_roguelike_tutorial.components.equipment import Equipment
from py_roguelike_tutorial.components.equippable import Equippable
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components import consumable
from py_roguelike_tutorial.components.level import Level
from py_roguelike_tutorial.entity import Actor, Item
from py_roguelike_tutorial.equipment_types import EquipmentType

SCROLL: Final[str] = "~"


class EntityPrefabs:
    player = Actor(
        char="@",
        color=Color.WHITE,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(max_hp=30, defense=2, power=5),
        inventory=Inventory(26),  # 26 bc of English alphabet
        level=Level(level_up_base=200, level_up_factor=150),
        equipment=Equipment(),
    )
    # enemies
    orc = Actor(
        char="o",
        color=Color.RED_ROBIN,
        name="Orc",
        ai_cls=HostileEnemy,
        fighter=Fighter(max_hp=10, defense=0, power=3),
        inventory=Inventory.none(),
        level=Level(level_up_base=0, xp_given=35),
        equipment=Equipment(),
    )
    troll = Actor(
        char="T",
        color=Color.GREEN_DEEP_COOL,
        name="Troll",
        ai_cls=HostileEnemy,
        fighter=Fighter(max_hp=16, defense=1, power=4),
        inventory=Inventory.none(),
        level=Level(level_up_base=0, xp_given=35),
        equipment=Equipment(),
    )

    # consumable items
    health_potion = Item(
        char="!",
        color=Color.VIOLET,
        name="Health Potion",
        consumable=consumable.HealingConsumable(amount=4),
    )
    lightning_scroll = Item(
        char=SCROLL,
        color=Color.BLUE,
        name="Lightning Scroll",
        consumable=consumable.LightningDamageConsumable(damage=20, max_range=5),
    )
    confusion_scroll = Item(
        char=SCROLL,
        color=Color.PINK_INSANITY,
        name="Confusion Scroll",
        consumable=consumable.ConfusionConsumable(turns=10),
    )
    fireball_scroll = Item(
        char=SCROLL,
        color=Color.RED,
        name="Fireball Scroll",
        consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    )

    # equipment
    dagger = Item(
        char="/",
        color=(0, 191, 255),
        name="Dagger",
        equippable=Equippable(EquipmentType.WEAPON, power=2),
    )
    sword = Item(
        char="/",
        color=(0, 191, 255),
        name="Sword",
        equippable=Equippable(EquipmentType.WEAPON, power=4),
    )
    leather_armor = Item(
        char="[",
        color=(139, 69, 19),
        name="Leather Armor",
        equippable=Equippable(EquipmentType.ARMOR, defense=1),
    )
    chain_mail = Item(
        char="[",
        color=(139, 69, 19),
        name="Chain Mail",
        equippable=Equippable(EquipmentType.ARMOR, defense=3),
    )
