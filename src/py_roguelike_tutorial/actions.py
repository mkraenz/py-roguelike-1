class Action:
    pass


class EscapeAction(Action):
    pass


class MoveAction(Action):
    def __init__(self, dx: int, dy: int) -> None:
        super()
        self.dx = dx
        self.dy = dy
