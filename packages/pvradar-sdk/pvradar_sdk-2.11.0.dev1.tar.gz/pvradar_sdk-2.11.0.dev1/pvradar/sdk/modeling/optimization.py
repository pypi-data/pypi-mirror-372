from typing import Annotated, Any, Callable, override
import numpy as np
import pandas as pd
from pydantic import Field
from abc import ABC, abstractmethod

from .utils import to_series


def series_rmse(
    true_values: Annotated[pd.Series | list[float], Field(description='true values')],
    predicted_values: Annotated[pd.Series | list[float], Field(description='predicted values')],
) -> float:
    return np.sqrt(series_mse(true_values, predicted_values))


def series_mse(
    true_values: Annotated[pd.Series | list[float], Field(description='true values')],
    predicted_values: Annotated[pd.Series | list[float], Field(description='predicted values')],
) -> float:
    pd_true_values = to_series(true_values)
    pd_predicted_values = to_series(predicted_values)
    return float(np.mean((pd_true_values - pd_predicted_values) ** 2))


def series_huber_loss(
    true_values: Annotated[pd.Series | list[float], Field(description='true values')],
    predicted_values: Annotated[pd.Series | list[float], Field(description='predicted values')],
    delta: float = 0.05,
):
    pd_true_values = to_series(true_values)
    pd_predicted_values = to_series(predicted_values)
    residual = pd_true_values - pd_predicted_values
    return np.where(np.abs(residual) <= delta, 0.5 * residual**2, delta * (np.abs(residual) - 0.5 * delta)).mean()


class OptimizationTarget(ABC):
    @abstractmethod
    def deviation(self, predicted: Any) -> float: ...

    @abstractmethod
    def get_overlap_ratio(self, predicted: pd.Series) -> float: ...


class OptimizationSeriesTarget(OptimizationTarget):
    def __init__(
        self,
        true_values: Annotated[pd.Series | list[float], Field(description='target values')],
        deviation_callback: Callable = series_rmse,
        **kwargs,
    ) -> None:
        self.true_values = to_series(true_values)
        self.deviation_callback = deviation_callback
        self.data = kwargs

    @override
    def deviation(self, predicted: pd.Series | list[float]) -> float:
        return self.deviation_callback(self.true_values, predicted)

    @override
    def get_overlap_ratio(self, predicted: pd.Series) -> float:
        true_series = to_series(self.true_values)
        overlapping_index = predicted.index.intersection(true_series.index)  # pyright: ignore[reportArgumentType]
        overlapping_ratio = len(overlapping_index) / len(true_series.index)
        return overlapping_ratio
