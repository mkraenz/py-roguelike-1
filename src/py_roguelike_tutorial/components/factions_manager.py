from typing import NamedTuple

from py_roguelike_tutorial.components.faction import Faction


class FactionPair(NamedTuple):
    faction_id1: str
    faction_id2: str


type FactionRelationships = dict[FactionPair, float]


class FactionsManager:
    def __init__(self, factions: dict[str, Faction]):
        self.factions: dict[str, Faction] = factions
        self._relations: FactionRelationships = {}

        """How much do the factions like eachother. 
        Relations are asymmetric! In other words, A can be friends with B, but B can simultaneously hate A.
        Each entry `{(A,B): X}` reads A likes B by amount X where X is between -100.0 and +100.0. 
        Higher values of X means "likes more".
        """

        for faction1 in self.factions:
            for faction2 in self.factions:
                pair = FactionPair(faction1, faction2)
                self._relations[pair] = 0.0 if faction1 != faction2 else 100.0

    def get_relation(self, faction1: str, faction2: str) -> float:
        return self._relations[FactionPair(faction1, faction2)]

    def get_faction(self, id: str) -> Faction:
        return self.factions[id]


if __name__ == "__main__":
    factions = {"a": Faction("a", "A"), "b": Faction("b", "B"), "c": Faction("c", "C")}
    mng = FactionsManager(factions)

    print(
        mng.get_relation("a", "a"),
        mng.get_relation("a", "b"),
        mng.get_relation("a", "c"),
        mng.get_relation("b", "b"),
    )
