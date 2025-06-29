import traceback
import random

import tcod
from tcod.event import wait

from py_roguelike_tutorial import exceptions, setup_game
from py_roguelike_tutorial.colors import Theme
from py_roguelike_tutorial.constants import SAVE_FILENAME
from py_roguelike_tutorial.input_handlers import (
    BaseEventHandler,
    EventHandler,
)


def save_game(handler: BaseEventHandler, filename: str):
    if isinstance(handler, EventHandler):
        handler.engine.save_to_file(filename)
        print(f"Game saved to {filename}.")


def main():
    rng_seed = 42
    monitor_width = 1920
    window_width = monitor_width // 2
    window_height = 1080
    screen_width = 80
    screen_height = 50
    window_x = monitor_width // 2 - 10

    random.seed(rng_seed)

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
        title="TSTT's Pythyfyl Roguelike",
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
                        converted_event = context.convert_event(event)
                        handler = handler.handle_events(converted_event)
                except exceptions.QuitWithoutSaving:
                    raise
                except Exception:  # ingame exceptions
                    traceback.print_exc()
                    if isinstance(handler, EventHandler):
                        handler.engine.message_log.add(
                            traceback.format_exc(), fg=Theme.error
                        )
                    raise
        except exceptions.QuitWithoutSaving:
            raise SystemExit()
        except SystemExit:
            save_game(handler, SAVE_FILENAME)
            raise
        except BaseException:  # save on any unexpeceted exception
            save_game(handler, SAVE_FILENAME)
            raise


if __name__ == "__main__":
    main()
