from tcod.event import KeySym as Key


_MOVE_KEYS = {
    # numpad
    Key.KP_1: (-1, 1),
    Key.KP_2: (0, 1),
    Key.KP_3: (1, 1),
    Key.KP_4: (-1, 0),
    Key.KP_6: (1, 0),
    Key.KP_7: (-1, -1),
    Key.KP_8: (0, -1),
    Key.KP_9: (1, -1),
    # wasd
    Key.Z: (-1, 1),
    Key.S: (0, 1),
    Key.X: (1, 1),
    Key.A: (-1, 0),
    Key.D: (1, 0),
    Key.Q: (-1, -1),
    Key.W: (0, -1),
    Key.E: (1, -1),
}

_WAIT_KEYS = {Key.KP_5, Key.PERIOD, Key.SPACE}

_CURSOR_Y_KEYS = {
    Key.UP: -1,
    Key.DOWN: 1,
    Key.PAGEUP: -10,
    Key.PAGEDOWN: 10,
}


_CONFIRM_KEYS = {
    Key.RETURN,
    Key.KP_ENTER,
}

_MODIFIER_KEYS = {
    Key.LSHIFT,
    Key.RSHIFT,
    Key.LCTRL,
    Key.RCTRL,
    Key.LALT,
    Key.RALT,
}
