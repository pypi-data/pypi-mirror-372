from typing import Annotated
import pandas as pd

from ...modeling.decorators import resource_type, synchronize_freq
from ...modeling import R
from ...common.pandas_utils import interval_to_index


@resource_type(R.revenue(set_unit='USD'))
@synchronize_freq('lowest')
def pvradar_simple_revenue(
    grid_power: Annotated[pd.Series, R.grid_power],
    electricity_sales_price: Annotated[pd.Series, R.energy_sales_price],
) -> pd.Series:
    # FIXME: this function uses power as energy which is ok as power is hourly frequency (same values).
    # Better first convert to energy before multiplying with electricity sales prices to allow any frequency input.
    return grid_power * electricity_sales_price / 1e6  # price in USD per MWh!


@resource_type(R.energy_sales_price(set_unit='USD/MWh'))
def pvradar_simple_ppa(
    ppa_price: float,
    interval: pd.Interval,
) -> pd.Series:
    index = interval_to_index(interval, freq='h')
    return pd.Series(ppa_price, index=index)
