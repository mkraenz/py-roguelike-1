import copy

import tcod

from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity_factory import EntityFactory
from py_roguelike_tutorial.procgen import generate_dungeon


def main():
    monitor_width = 1920
    window_width = monitor_width // 2
    window_height = 1080
    screen_width = 80
    screen_height = 50
    window_x = monitor_width // 2 - 10

    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 2

    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    player = copy.deepcopy(EntityFactory.player_prefab)
    engine = Engine(player=player)
    engine.game_map = generate_dungeon(
        map_width=map_width,
        map_height=map_height,
        max_rooms=max_rooms,
        room_max_size=room_max_size,
        room_min_size=room_min_size,
        max_monsters_per_room=max_monsters_per_room,
        engine=engine,
    )
    engine.update_fov()
    engine.message_log.add(text="Welcome, adventurer.", fg=Theme.welcome_text)

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Miros Pythyfyl Roguelike",
        vsync=True,
        width=window_width,
        height=window_height,
        x=window_x,
        y=0,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            engine.render(root_console, context)
            engine.event_handler.handle_events()


if __name__ == "__main__":
    main()
