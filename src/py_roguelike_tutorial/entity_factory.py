from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import HostileEnemy
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.components.inventory import Inventory
from py_roguelike_tutorial.components import consumable
from py_roguelike_tutorial.entity import Actor, Item


class EntityFactory:
    player_prefab = Actor(
        char="@",
        color=Color.WHITE,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=30, defense=2, power=5),
        inventory=Inventory(26),  # 26 bc of English alphabet
    )
    # enemies
    orc_prefab = Actor(
        char="o",
        color=Color.RED_ROBIN,
        name="Orc",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=10, defense=0, power=3),
        inventory=Inventory.none(),
    )
    troll_prefab = Actor(
        char="T",
        color=Color.GREEN_DEEP_COOL,
        name="Troll",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=16, defense=1, power=4),
        inventory=Inventory.none(),
    )

    # items
    health_potion_prefab = Item(
        char="!",
        color=Color.VIOLET,
        name="Health Potion",
        consumable=consumable.HealingConsumable(amount=4),
    )
    lightning_scroll_prefab = Item(
        char="~",
        color=Color.BLUE,
        name="Lightning Scroll",
        consumable=consumable.LightningDamageConsumable(damage=20, max_range=5),
    )
    confusion_scroll_prefab = Item(
        char="~",
        color=Color.PINK_INSANITY,
        name="Confusion Scroll",
        consumable=consumable.ConfusionConsumable(turns=10),
    )
