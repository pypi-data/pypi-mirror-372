from pydantic import BaseModel


class PuzzleSolution(BaseModel):
    drag_distance: int


class WhirlSolution(BaseModel):
    drag_distance: int
    rotation_angle: float


class SameObjectSolution(BaseModel):
    x1: int
    y1: float
    x2: int
    y2: float
