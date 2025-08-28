from enum import Enum


class Side(Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    NONE = ""


class Coordinate:
    x_pos: int
    y_pos: int
    side: Side
    connected: bool

    def __init__(self):
        self.x_pos = 0
        self.y_pos = 0
        self.side = Side.NONE
        self.connected = False

    def __repr__(self) -> str:
        return f"pos: ({self.x_pos},{self.y_pos}), side: {self.side}, connected: {self.connected}"

    def get_xy(self) -> (int, int):
        return (self.x_pos, self.y_pos)
