from unittest.mock import patch
import tcod.event
from py_roguelike_tutorial.main import main


def test_start_game_and_immediately_close():
    # Mock a sequence of KeyDown events
    mock_events = [
        tcod.event.KeyDown(
            scancode=tcod.event.Scancode.ESCAPE,
            sym=tcod.event.KeySym.ESCAPE,
            mod=tcod.event.Modifier.NONE,
            repeat=False,
        ),
    ]

    with patch("tcod.event.get", return_value=mock_events):
        try:
            main(max_iterations=2)
        except SystemExit:
            pass

        assert True
