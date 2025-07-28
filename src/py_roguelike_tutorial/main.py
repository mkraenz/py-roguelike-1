import random
import time
import traceback

import tcod

from py_roguelike_tutorial import exceptions, setup_game
from py_roguelike_tutorial.constants import Theme
from py_roguelike_tutorial.procgen.procgen_config import (
    ProcgenConfig,
)
from py_roguelike_tutorial.constants import AUTOSAVE_FILENAME, RNG_SEED
from py_roguelike_tutorial.entity_factory import EntityPrefabs
from py_roguelike_tutorial.handlers.base_event_handler import BaseEventHandler
from py_roguelike_tutorial.handlers.ingame_event_handler import IngameEventHandler
import py_roguelike_tutorial.loader as loader
from py_roguelike_tutorial.screen_stack import ScreenStack
from py_roguelike_tutorial.utils import assets_filepath


def save_game(handler: BaseEventHandler, filename: str):
    if isinstance(handler, IngameEventHandler):
        handler.engine.save_to_file(filename)
        print(f"Game saved to {filename}.")


def load_data_files():
    EntityPrefabs.items = loader.load_item_entities()
    EntityPrefabs.factions = loader.load_factions()
    loader.load_behavior_trees(EntityPrefabs.behavior_trees)
    EntityPrefabs.player = loader.load_player_entity(EntityPrefabs.items)
    EntityPrefabs.npcs = loader.load_npcs_entities(EntityPrefabs.items)
    EntityPrefabs.props = loader.load_props_entities(EntityPrefabs.items)
    ProcgenConfig.item_chances = loader.load_item_drops_rates(EntityPrefabs.items)
    ProcgenConfig.enemy_chances = loader.load_enemy_spawn_rates(EntityPrefabs.npcs)


def main(*, max_iterations: int | None = None):
    monitor_width = 1920
    window_width = monitor_width // 2
    window_height = 1080
    screen_width = 80
    screen_height = 50
    window_x = monitor_width // 2 - 10
    max_frame_time: float = 1 / 60  # 60 FPS

    random.seed(RNG_SEED)

    filename = assets_filepath("assets/dejavu10x10_gs_tc.png")
    tileset = tcod.tileset.load_tilesheet(
        filename,
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    load_data_files()
    stack = ScreenStack()
    stack.push(setup_game.MainMenu(stack))
    handler = stack.peek()

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

        previous_timestamp: float = time.time()
        iterations = 0
        try:
            while True and (
                iterations < max_iterations if max_iterations is not None else True
            ):
                if max_iterations is not None:
                    iterations += 1

                root_console.clear()

                current_timestamp = time.time()
                delta = current_timestamp - previous_timestamp
                previous_timestamp = current_timestamp

                handler = stack.peek()
                handler.on_render(console=root_console, delta_time=delta)
                context.present(root_console)
                try:
                    for event in tcod.event.wait(max_frame_time):
                        converted_event = context.convert_event(event)
                        next_handler = handler.handle_events(converted_event)
                        if next_handler is not handler:
                            stack.push(next_handler)
                except exceptions.QuitWithoutSaving:
                    raise
                except Exception:  # ingame exceptions
                    traceback.print_exc()
                    if isinstance(handler, IngameEventHandler):
                        handler.engine.message_log.add(
                            traceback.format_exc(), fg=Theme.error
                        )
                    raise
        except exceptions.QuitWithoutSaving:
            raise SystemExit()
        except SystemExit:
            save_game(handler, AUTOSAVE_FILENAME)
            raise
        except BaseException:  # save on any unexpeceted exception
            save_game(handler, AUTOSAVE_FILENAME)
            raise
