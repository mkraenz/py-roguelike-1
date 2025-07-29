from py_roguelike_tutorial.components.base_component import BaseComponent
from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.entity import Actor, Prop


class Health(BaseComponent):

    parent: Actor | Prop

    def __init__(self, max_hp: int, hp: int | None = None):
        self.max_hp = max_hp
        self._hp = hp if hp else max_hp

    @property
    def hp_percent(self) -> float:
        return float(self.hp) / self.max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, val: int) -> None:
        self._hp = max(0, min(self.max_hp, val))
        if self._hp <= 0:
            self.die()

    def die(self) -> None:
        death_msg, log_color = self.dying_message()
        self.parent.die()
        self.engine.message_log.add(death_msg, fg=log_color)
        if hasattr(self.parent, "level"):
            self.engine.player.level.add_xp(getattr(self.parent, "level").xp_given)

    def dying_message(self):
        player_died = self.engine.player is self.parent
        is_prop = isinstance(self.parent, Prop)
        if is_prop:
            return f"The {self.parent.name} opened.", Theme.log_message
        if player_died:
            return "You died!", Theme.player_dies
        return f"{self.parent.name} has died!", Theme.enemy_dies

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def increase_max_hp(self, amount: int) -> None:
        self.max_hp += amount
        self.hp += amount

    def heal(self, amount: int) -> int:
        """Heals by the given amount and returns the amount recovered."""
        theoretical_new_hp = self.hp + amount
        new_hp_value = (
            theoretical_new_hp if theoretical_new_hp <= self.max_hp else self.max_hp
        )
        amount_recovered = new_hp_value - self.hp
        self.hp = new_hp_value
        return amount_recovered
