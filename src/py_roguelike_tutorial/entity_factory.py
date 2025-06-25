from py_roguelike_tutorial.colors import Color
from py_roguelike_tutorial.components.ai import HostileEnemy
from py_roguelike_tutorial.components.fighter import Fighter
from py_roguelike_tutorial.entity import Actor


class EntityFactory:
    player_prefab = Actor(
        char="@",
        color=Color.WHITE,
        name="Player",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=30, defense=2, power=5),
    )
    orc_prefab = Actor(
        char="o",
        color=Color.RED_ROBIN,
        name="Orc",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=10, defense=0, power=3),
    )
    troll_prefab = Actor(
        char="T",
        color=Color.DEEP_COOL_GREEN,
        name="Troll",
        ai_cls=HostileEnemy,
        fighter=Fighter(hp=16, defense=1, power=4),
    )
