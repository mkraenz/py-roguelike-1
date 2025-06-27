import copy
import traceback

import tcod
from tcod.event import wait

from py_roguelike_tutorial import exceptions, setup_game
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.engine import Engine
from py_roguelike_tutorial.entity_factory import EntityFactory
from py_roguelike_tutorial.input_handlers import (
    BaseEventHandler,
    MainGameEventHandler,
    EventHandler,
)
from py_roguelike_tutorial.procgen import generate_dungeon


def main():
    monitor_width = 1920
    window_width = monitor_width // 2
    window_height = 1080
    screen_width = 80
    screen_height = 50
    window_x = monitor_width // 2 - 10


    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )


    handler: BaseEventHandler = setup_game.MainMenu()

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
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)
                try:
                    for event in wait():
                        # TODO i guess i should use the converted event and pass that to the event handler
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # ingame exceptions
                    traceback.print_exc()
                    if isinstance(handler, EventHandler):
                        handler.engine.message_log.add(
                            traceback.format_exc(), fg=Theme.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:
            # TODO: add save functionality here
            raise
        except BaseException:  # save on any unexpeceted exception
            # TODO: add save functionality here
            raise


if __name__ == "__main__":
    main()
