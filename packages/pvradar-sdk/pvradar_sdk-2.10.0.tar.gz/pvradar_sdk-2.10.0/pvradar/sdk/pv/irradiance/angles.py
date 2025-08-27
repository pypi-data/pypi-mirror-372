from typing import Annotated
import pandas as pd
import numpy as np
from pvlib import shading, irradiance, tracking
from pvlib.location import Location
from pvlib.tools import cosd

from ..design import ArrayDesign, FixedStructureDesign, TrackerStructureDesign as TD
from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R
from ...common.pandas_utils import interval_to_index
from ...modeling.model_context import ModelContext
from ...modeling.basics import LambdaArgument as LA


### -------------------------- SOLAR POSITION -------------------------- ###


def _pure_calculate_solar_position_table(
    location: Location,
    interval: pd.Interval,
    freq: str,
):
    solar_position_table = location.get_solarposition(
        times=interval_to_index(interval, freq),
        pressure=None,  # TODO: use actual pressure series
        temperature=12,  # TODO: use actual ambient temperature series
    )
    assert isinstance(solar_position_table, pd.DataFrame)
    solar_position_table.attrs['location'] = location
    solar_position_table.attrs['interval'] = interval
    solar_position_table.attrs['freq'] = freq
    return solar_position_table


def _solar_position_table(
    location: Location,
    interval: pd.Interval,
    freq: str,
    context: ModelContext,
):
    """
    Calculates solar position and stores result in context for reuse
    This stored value is reused only if the same location and interval is requested
    """
    if '_solar_position_table' in context:
        result = context['_solar_position_table']
        assert isinstance(result, pd.DataFrame)
        if result.attrs['location'] is location and result.attrs['interval'] is interval and result.attrs['freq'] == freq:
            return result
    result = _pure_calculate_solar_position_table(location, interval, freq)
    context['_solar_position_table'] = result
    return result


@standard_resource_type(R.solar_azimuth_angle, override_unit=True)
def pvlib_solar_azimuth_angle(context: ModelContext) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table, **context.all_kwargs)
    return solar_pos_table['azimuth']


@standard_resource_type(R.solar_elevation_angle, override_unit=True)
def pvlib_solar_elevation_angle(
    context: ModelContext,
    apparent: bool = True,
) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table, **context.all_kwargs)
    if apparent:
        return solar_pos_table['apparent_elevation']
    else:
        return solar_pos_table['elevation']


@standard_resource_type(R.solar_zenith_angle, override_unit=True)
def pvlib_solar_zenith_angle(
    context: ModelContext,
    apparent: bool = True,
) -> pd.Series:
    solar_pos_table = context.run(_solar_position_table, **context.all_kwargs)
    if apparent:
        return solar_pos_table['apparent_zenith']
    else:
        return solar_pos_table['zenith']


### -------------------------- ANGLE OF INCIDENCE -------------------------- ###


@standard_resource_type(R.tracker_rotation_angle, override_unit=True)
@synchronize_freq('default')
def pvlib_tracking_single_axis(
    apparent_zenith: Annotated[pd.Series, R.solar_zenith_angle(apparent=True)],
    apparent_azimuth: Annotated[pd.Series, R.solar_azimuth_angle],
    slope_azimuth: Annotated[float, LA(ArrayDesign, lambda d: d.slope_azimuth)],
    slope_tilt: Annotated[float, LA(ArrayDesign, lambda d: d.slope_tilt)],
    axis_tilt: Annotated[float, LA(TD, lambda d: d.axis_tilt)],
    axis_azimuth: Annotated[float, LA(TD, lambda d: d.axis_azimuth)],
    max_angle: Annotated[float, LA(TD, lambda d: d.max_tracking_angle)],
    backtrack: Annotated[bool, LA(TD, lambda d: d.backtracking)],
    night_stow_angle: Annotated[float, LA(TD, lambda d: d.night_stow_angle)],
    gcr: Annotated[float, LA(ArrayDesign, lambda d: d.ground_cover_ratio)],
) -> pd.Series:
    """
    Determine the rotation angle of a single-axis tracker when given particular
    solar zenith and azimuth angles.

    Based on pvlib.tracking.singleaxis, but ...
    https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.tracking.singleaxis.html
    """
    # calculate cross axis tilt
    cross_axis_tilt = tracking.calc_cross_axis_tilt(
        slope_azimuth=slope_azimuth,
        slope_tilt=slope_tilt,
        axis_azimuth=axis_azimuth,
        axis_tilt=axis_tilt,
    )

    # The ideal tracking angle, omega_ideal, is the rotation to place the sun
    # position vector (xp, yp, zp) in the (x, z) plane, which is normal to
    # the panel and contains the axis of rotation. omega_ideal=0 indicates
    # that the panel is horizontal. Here, our convention is that a clockwise
    # rotation is positive, to view rotation angles in the same frame of
    # reference as azimuth. For example, for a system with tracking
    # axis oriented south, a rotation toward the east is negative, and a
    # rotation to the west is positive. This is a right-handed rotation
    # around the tracker y-axis.
    omega_ideal = shading.projected_solar_zenith_angle(
        axis_tilt=axis_tilt,
        axis_azimuth=axis_azimuth,
        solar_zenith=apparent_zenith,
        solar_azimuth=apparent_azimuth,
    )

    # filter for sun above panel horizon
    zen_gt_90 = apparent_zenith > 90
    omega_ideal[zen_gt_90] = np.nan

    # Account for backtracking
    if backtrack:
        # distance between rows in terms of rack lengths relative to cross-axis
        # tilt
        axes_distance = 1 / (gcr * cosd(cross_axis_tilt))

        # NOTE: account for rare angles below array, see GH 824
        temp = np.abs(axes_distance * cosd(omega_ideal - cross_axis_tilt))

        # backtrack angle using [1], Eq. 14
        with np.errstate(invalid='ignore'):
            omega_correction = np.degrees(-np.sign(omega_ideal) * np.arccos(temp))

        # NOTE: in the middle of the day, arccos(temp) is out of range because
        # there's no row-to-row shade to avoid, & backtracking is unnecessary
        # [1], Eqs. 15-16
        with np.errstate(invalid='ignore'):
            tracker_theta = omega_ideal + np.where(temp < 1, omega_correction, 0)
    else:
        tracker_theta = omega_ideal

    # Clip tracker_theta between the minimum and maximum angles.
    min_angle = -max_angle
    tracker_theta = np.clip(tracker_theta, min_angle, max_angle)  # type: ignore

    # replace missing values with night stow angle
    tracker_theta: pd.Series
    tracker_theta.fillna(night_stow_angle * (-1), inplace=True)
    # NOTE: multiplying with -1 to make tracker face east at night (random choice)
    # TODO: replace night stow tilt angle with night stow rotation angle (theta) to allow users
    # to define orientation towards west as well

    return tracker_theta


def _tracker_orientation_table(
    tracker_rotation_angle: Annotated[pd.Series, R.tracker_rotation_angle],
    axis_tilt: Annotated[float, LA(TD, lambda d: d.axis_tilt)],
    axis_azimuth: Annotated[float, LA(TD, lambda d: d.axis_azimuth)],
) -> pd.DataFrame:
    """
    wrapper for pvlib function pvlib.tracking.calc_surface_orientation
    only for trackers

    Two columns:
    - surface_tilt
    - surface_azimuth
    """

    tracker_orientation_table: pd.DataFrame = tracking.calc_surface_orientation(
        tracker_theta=tracker_rotation_angle,
        axis_tilt=axis_tilt,  # type: ignore
        axis_azimuth=axis_azimuth,  # type: ignore
    )

    return tracker_orientation_table  # type: ignore


def _fixed_orientation_table(
    tilt: Annotated[float, LA(FixedStructureDesign, lambda d: d.tilt)],
    azimuth: Annotated[float, LA(FixedStructureDesign, lambda d: d.azimuth)],
    interval: pd.Interval,
) -> pd.DataFrame:
    fixed_structure_orientation_table = pd.DataFrame(
        {'surface_tilt': tilt, 'surface_azimuth': azimuth}, index=interval_to_index(interval)
    )
    return fixed_structure_orientation_table


@standard_resource_type(R.surface_tilt_angle, override_unit=True)
def pvlib_surface_tilt_angle(
    context: ModelContext,
    array: ArrayDesign,
):
    if isinstance(array.structure, TD):
        orientation_table = context.run(_tracker_orientation_table, **context.all_kwargs)
        result = orientation_table['surface_tilt']
    else:
        orientation_table = context.run(_fixed_orientation_table, **context.all_kwargs)
        result = orientation_table['surface_tilt']
    return context.with_dependencies(result, orientation_table)


@standard_resource_type(R.surface_azimuth_angle, override_unit=True)
def pvlib_surface_azimuth_angle(
    context: ModelContext,
    array: ArrayDesign,
):
    if isinstance(array.structure, TD):
        orientation_table = context.run(_tracker_orientation_table, **context.all_kwargs)
        result = orientation_table['surface_azimuth']

    else:
        orientation_table = context.run(_fixed_orientation_table, **context.all_kwargs)
        result = orientation_table['surface_azimuth']
    return context.with_dependencies(result, orientation_table)


@standard_resource_type(R.angle_of_incidence, override_unit=True)
@synchronize_freq('default')
def pvlib_angle_of_incidence(
    surface_tilt: Annotated[pd.Series, R.surface_tilt_angle],
    surface_azimuth: Annotated[pd.Series, R.surface_azimuth_angle],
    apparent_solar_zenith: Annotated[pd.Series, R.solar_zenith_angle(apparent=True)],
    solar_azimuth: Annotated[pd.Series, R.solar_azimuth_angle],
):
    """
    Wrapper around irradiance.aoi
    """
    aoi = irradiance.aoi(
        surface_tilt=surface_tilt,
        surface_azimuth=surface_azimuth,
        solar_zenith=apparent_solar_zenith,
        solar_azimuth=solar_azimuth,
    )
    return aoi
