import pvlib
from typing import Annotated
import pandas as pd
from pydantic import Field
from ....modeling.decorators import standard_resource_type, synchronize_freq
from ....modeling import R
from ....common.pandas_utils import interval_to_index


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def no_soiling_losses(
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(0, index=timestamps)


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
@synchronize_freq('default')
def pvlib_soiling_hsu(
    *,
    pm2_5: Annotated[pd.Series, R.pm2_5_volume_concentration(to_unit='g/m^3')],
    pm10: Annotated[pd.Series, R.pm10_volume_concentration(to_unit='g/m^3')],
    rainfall: Annotated[pd.Series, R.rainfall(to_unit='mm')],
    surface_tilt_angle: Annotated[pd.Series, R.surface_tilt_angle],
    rain_cleaning_threshold: Annotated[float, Field(gt=0, lt=10)] = 1,
    pm2_5_depo_veloc: Annotated[float, Field(gt=0)] = 0.0009,
    pm10_depo_veloc: Annotated[float, Field(gt=0)] = 0.004,
    rain_accum_period=pd.Timedelta('1d'),
) -> pd.Series:
    depo_veloc = {'2_5': pm2_5_depo_veloc, '10': pm10_depo_veloc}

    soiling_ratio = pvlib.soiling.hsu(
        rainfall=rainfall,
        cleaning_threshold=rain_cleaning_threshold,
        surface_tilt=surface_tilt_angle,
        pm2_5=pm2_5.values,
        pm10=pm10.values,
        depo_veloc=depo_veloc,
        rain_accum_period=rain_accum_period,
    )
    return 1 - soiling_ratio


@standard_resource_type(R.soiling_loss_factor, override_unit=True)
def pvlib_soiling_kimber(
    *,
    rainfall: Annotated[pd.Series, R.rainfall(to_unit='mm', to_freq='D')],
    rain_cleaning_threshold: Annotated[float, Field(gt=0)] = 6,
    soiling_rate_value: Annotated[float, Field(gt=0)] = 0.0015,
    grace_period: Annotated[int, Field(ge=0)] = 14,
    max_soiling_value: Annotated[float, Field(gt=0)] = 0.3,
    initial_soiling: Annotated[float, Field(ge=0)] = 0,
    rain_accum_period=pd.Timedelta('1d'),
) -> pd.Series:
    soiling_loss_factor = pvlib.soiling.kimber(
        rainfall=rainfall,
        cleaning_threshold=rain_cleaning_threshold,  # type: ignore
        soiling_loss_rate=soiling_rate_value,
        grace_period=grace_period,
        max_soiling=max_soiling_value,
        initial_soiling=initial_soiling,  # type: ignore
        rain_accum_period=int(rain_accum_period.total_seconds() / 3600),
    )

    return soiling_loss_factor
