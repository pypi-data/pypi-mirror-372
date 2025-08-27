import pvlib
from typing import Annotated
import pandas as pd
import numpy as np
from pydantic import Field

from ....modeling.decorators import standard_resource_type, synchronize_freq
from ....modeling import R, resample_series
from ....common.pandas_utils import interval_to_index
from ...design import ArrayDesign, FixedStructureDesign, ModuleOrientation, ModuleDesign
from ....modeling.basics import LambdaArgument


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def no_snow_losses(
    interval: pd.Interval,
    freq: str,
) -> pd.Series:
    timestamps = interval_to_index(interval=interval, freq=freq)
    return pd.Series(0, index=timestamps)


@standard_resource_type(R.snow_coverage, override_unit=True)
@synchronize_freq('h')
def pvlib_snow_coverage_marion(
    snowfall: Annotated[pd.Series, R.snowfall(to_unit='cm')],
    poa_irradiance: Annotated[pd.Series, R.global_poa_on_front(to_unit='W/m^2')],
    air_temperature: Annotated[pd.Series, R.air_temperature(to_unit='degC')],
    array: ArrayDesign,
    snowfall_threshold: Annotated[float, Field(ge=0)] = 1,
    can_slide_coef: Annotated[float, Field(le=0)] = -80.0,
    slide_amount_coef: Annotated[float, Field(ge=0)] = 0.197,
    initial_snow_coverage: Annotated[float, Field(ge=0, le=1)] = 0,
) -> pd.Series:
    # Calculate coverage factor
    snow_coverage = pvlib.snow.coverage_nrel(
        snowfall=snowfall,
        poa_irradiance=poa_irradiance,
        temp_air=air_temperature,
        surface_tilt=_get_max_tilt_angle(array.structure),
        initial_coverage=initial_snow_coverage,  # type: ignore
        threshold_snowfall=snowfall_threshold,
        can_slide_coefficient=can_slide_coef,
        slide_amount_coefficient=slide_amount_coef,
    )

    # inherit freq, so that there is no guessing in the downstream
    if poa_irradiance.attrs.get('freq'):
        snow_coverage.attrs['freq'] = poa_irradiance.attrs['freq']

    return snow_coverage


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def pvlib_snow_loss_marion(
    snow_coverage: Annotated[pd.Series, R.snow_coverage],
    module_orientation: Annotated[ModuleOrientation, LambdaArgument(ArrayDesign, lambda d: d.module_orientation)],
    num_mod_cross_section: Annotated[int, LambdaArgument(ArrayDesign, lambda d: d.number_modules_cross_section)],
    cell_string_count: Annotated[int, LambdaArgument(ModuleDesign, lambda d: d.cell_string_count)],
    is_half_cell: Annotated[bool, LambdaArgument(ModuleDesign, lambda d: d.half_cell)],
) -> pd.Series:
    if module_orientation == 'horizontal':
        num_cell_strings = cell_string_count * num_mod_cross_section
    else:
        if is_half_cell:
            # half cell: module separated in two parts along long side
            num_cell_strings = num_mod_cross_section * 2
        else:
            num_cell_strings = num_mod_cross_section

    snow_loss_factor = np.ceil(snow_coverage * num_cell_strings) / num_cell_strings

    # let's keep type checking happy
    assert isinstance(snow_loss_factor, pd.Series)

    if snow_coverage.attrs.get('freq'):
        snow_loss_factor.attrs['freq'] = snow_coverage.attrs['freq']

    return snow_loss_factor


@standard_resource_type(R.snow_loss_factor, override_unit=True)
def pvlib_snow_loss_townsend(
    snowfall: Annotated[pd.Series, R.snowfall(to_freq='D', to_unit='cm'), Field()],
    poa_irradiance_hourly: Annotated[pd.Series, R.global_poa_on_front(to_freq='h', to_unit='W/m^2'), Field()],
    air_temperature: Annotated[pd.Series, R.air_temperature(to_freq='MS', to_unit='degC'), Field()],
    relative_humidity: Annotated[pd.Series, R.relative_humidity(to_freq='MS', to_unit='%'), Field()],
    array: ArrayDesign,
    angle_of_repose: Annotated[float, Field(ge=0, le=90)] = 40,  # in deg
    snow_event_threshold: Annotated[float, Field(ge=0)] = 1.27,  # 0.5 in/day in cm/day
    string_factor: Annotated[float, Field(ge=0)] = 0.75,
    # should be 0.75 if more than one module in cross-section, and 1.0 otherwise
) -> pd.Series:
    # counting how often the snow threshold was surpassed = snow event
    snow_events = snowfall > snow_event_threshold
    snow_events_monthly = snow_events.resample('MS').sum()
    snowfall_monthly = snowfall.resample('MS').sum()

    # integrate irradiance to irradiation
    monthly_irradiation = resample_series(poa_irradiance_hourly, freq='MS', agg='sum')

    # running pvlib model
    dc_loss_townsend = pvlib.snow.loss_townsend(
        snow_total=snowfall_monthly,
        snow_events=snow_events_monthly,
        surface_tilt=_get_max_tilt_angle(array.structure),
        relative_humidity=relative_humidity,
        temp_air=air_temperature,
        poa_global=monthly_irradiation,
        slant_height=array.collector_width,
        lower_edge_height=array.module_clearance,
        string_factor=string_factor,
        angle_of_repose=angle_of_repose,  # type: ignore
    )

    return dc_loss_townsend


def _get_max_tilt_angle(structure) -> float:
    """The maximum tilt angle of the structure / module."""
    if isinstance(structure, FixedStructureDesign):
        return structure.tilt
    else:
        return structure.max_tracking_angle
