import tcod

from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity import Entity
from py_roguelike_tutorial.game_map import GameMap
from py_roguelike_tutorial.input_handlers import EventHandler


def main():
    screen_width = 80
    screen_height = 50

    map_width = 80
    map_height = 45

    event_handler = EventHandler()

    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    player = Entity(screen_width // 2, screen_height // 2, "@", (255, 255, 255))
    npc = Entity(screen_width // 2 - 5, screen_height // 2, "N", (255, 255, 0))
    entities = {npc, player}

    game_map = GameMap(map_width, map_height)
    engine = Engine(
        entities=entities, event_handler=event_handler, game_map=game_map, player=player
    )

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Miros Pythyfyl Roguelike",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(root_console, context)
            events = tcod.event.wait()
            engine.handle_events(events)


if __name__ == "__main__":
    main()
