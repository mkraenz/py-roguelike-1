import sys

import tcod

from py_roguelike_tutorial.actions import EscapeAction, MoveAction
from py_roguelike_tutorial.input_handers import InputMap


def main():
    screen_width = 80
    screen_height = 50

    player_x: int = screen_width // 2
    player_y: int = screen_height // 2

    event_handler = InputMap()

    tileset = tcod.tileset.load_tilesheet(
        "assets/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
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
            ## game loop start
            root_console.print(player_x, player_y, "@")
            context.present(
                root_console
            )  ## present = draw = redraw = commit and apply changes

            root_console.clear()

            for event in tcod.event.wait():
                action = event_handler.dispatch(event)
                if action is None:
                    continue

                match action:
                    case MoveAction():
                        player_x += action.dx
                        player_y += action.dy
                    case EscapeAction():
                        sys.exit()
                    case _:
                        pass

                root_console.clear()


if __name__ == "__main__":
    main()
