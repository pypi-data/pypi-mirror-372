from typing import Annotated
import pandas as pd
from pydantic import Field
from ....common.pandas_utils import interval_to_index
from ....modeling.decorators import update_attrs


@update_attrs(unit='fraction', agg='mean')
def no_losses(
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(0, index=timestamps)


@update_attrs(unit='fraction', agg='mean')
def constant_losses(
    interval: pd.Interval,
    constant_loss_factor: Annotated[float, Field(ge=0, le=1)],
    freq: str,
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(constant_loss_factor, index=timestamps)


@update_attrs(unit='fraction', agg='mean')
def monthwise_losses(
    interval: pd.Interval,
    monthly_loss_factors: Annotated[list[float], Field(min_length=12, max_length=12)],
    freq: str,
) -> pd.Series:
    assert len(monthly_loss_factors) == 12, 'monthly_loss_factors must contain exactly 12 values'
    assert all(0 <= lf <= 1 for lf in monthly_loss_factors), 'All loss factors must be between 0 and 1'
    timestamps = interval_to_index(interval=interval, freq=freq)
    month_indices = timestamps.month - 1  # Convert 1-based month to 0-based index
    loss_factors = [monthly_loss_factors[m] for m in month_indices]
    return pd.Series(loss_factors, index=timestamps)
