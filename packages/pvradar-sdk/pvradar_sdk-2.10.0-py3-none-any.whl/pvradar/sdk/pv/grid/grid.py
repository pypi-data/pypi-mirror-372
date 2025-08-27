from typing import Annotated
import pandas as pd
import numpy as np

from ...modeling.basics import LambdaArgument
from ..design import PvradarSiteDesign
from ...modeling.decorators import standard_resource_type
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling import R
from ...common.pandas_utils import interval_to_index


@standard_resource_type(R.grid_power, override_unit=True)
def pvradar_simple_grid(
    *,
    ac_power: Annotated[pd.Series, R.ac_power],
    interval: pd.Interval,
    grid_limit: Annotated[
        pd.Series | int | float | None, LambdaArgument(PvradarSiteDesign, lambda design: design.grid.grid_limit)
    ],
) -> pd.Series:
    if grid_limit is None:
        return ac_power

    if isinstance(grid_limit, (int, float)):
        index = interval_to_index(interval=interval, freq='1h')
        grid_limit = pd.Series(float(grid_limit), index=index)

    if not isinstance(grid_limit, pd.Series):
        raise TypeError('`grid_limit` must be None, int, float, or pd.Series')

    return pd.Series(np.minimum(ac_power.to_numpy(), grid_limit.to_numpy()), index=ac_power.index)


@standard_resource_type(R.grid_energy, override_unit=True)
def pvradar_grid_energy_from_power(
    grid_power: Annotated[pd.Series, R.grid_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(grid_power, str(R.grid_energy))
