from py_roguelike_tutorial.components.base_component import BaseComponent


class Faction(BaseComponent):
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        """Display name"""
