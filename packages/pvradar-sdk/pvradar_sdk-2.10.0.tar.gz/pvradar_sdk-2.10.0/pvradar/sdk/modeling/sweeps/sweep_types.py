from typing import TypedDict

from ..basics import ModelRecipe


class SweepRange(TypedDict):
    param_name: str
    min: float
    max: float
    step: float


class ModelSweepRecipe(ModelRecipe):
    ranges: list[SweepRange]
