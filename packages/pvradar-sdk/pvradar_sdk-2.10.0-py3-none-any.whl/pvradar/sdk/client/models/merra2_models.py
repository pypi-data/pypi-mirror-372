from typing import Any, Annotated as A, TypeVar
import pandas as pd
import numpy as np
from pydantic import Field as F

from ...common.exceptions import DataUnavailableError
from ..api_query import Query
from ..client import PvradarClient
from pvlib.location import Location
from ...modeling.decorators import (
    datasource,
    realign_and_shift_timestamps,
    standard_resource_type,
    resource_type,
    synchronize_freq,
)
from ...modeling import R
from ...modeling.utils import auto_attr_table, convert_series_unit, rate_to_cumulative, ureg
from ..pvradar_resources import PvradarResourceType, SeriesConfigAttrs as S


# annotations redefined to account for non-standard 3h frequency
merra2_resource_annotations: dict[PvradarResourceType, Any] = {
    'air_density': A[float, F(ge=0), S(unit='kg/m^3', freq='3h')],
    'particle_mixing_ratio': A[pd.Series, F(ge=0), S(unit='kg/kg', param_names=['particle_name'], freq='3h')],
    'relative_humidity': A[float, S(resource_type='relative_humidity', unit='dimensionless', freq='3h')],
}

merra2_series_name_mapping: dict[str, PvradarResourceType | A[Any, Any]] = {
    # ----------------------------------------------------
    # MERRA2 - M2I3NVAER, merra2_aerosol_mixing_table
    #
    'AIRDENS': 'air_density',
    'RH': 'relative_humidity',
    'BCPHILIC': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='BC',
            min_radius_um=0.35,
            max_radius_um=0.35,
            density=1800,
        ),
    ],
    'BCPHOBIC': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='BC',
            min_radius_um=0.35,
            max_radius_um=0.35,
            density=1800,
        ),
    ],
    'DU001': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='DU',
            min_radius_um=0.1,
            max_radius_um=1.0,
            density=2500,
        ),
    ],
    'DU002': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='DU',
            min_radius_um=1.0,
            max_radius_um=1.8,
            density=2650,
        ),
    ],
    'DU003': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='DU',
            min_radius_um=1.8,
            max_radius_um=3,
            density=2650,
        ),
    ],
    'DU004': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='DU',
            min_radius_um=3,
            max_radius_um=6,
            density=2500,
        ),
    ],
    'OCPHILIC': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='OC',
            min_radius_um=0.35,
            max_radius_um=0.35,
            density=1800,
        ),
    ],
    'OCPHOBIC': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='OC',
            min_radius_um=0.35,
            max_radius_um=0.35,
            density=1800,
        ),
    ],
    'SO4': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='SO4',
            min_radius_um=0.35,
            max_radius_um=0.35,
            density=1700,
            mass_weight=132.14 / 96.06,  # = 1.375
        ),
    ],
    'SS001': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='SS',
            min_radius_um=0.03,
            max_radius_um=0.1,
            density=2200,
        ),
    ],
    'SS002': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='SS',
            min_radius_um=0.1,
            max_radius_um=0.5,
            density=2200,
        ),
    ],
    'SS003': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='SS',
            min_radius_um=0.5,
            max_radius_um=1.5,
            density=2200,
        ),
    ],
    'SS004': A[
        pd.Series,
        dict(
            resource_type='particle_mixing_ratio',
            species='SS',
            min_radius_um=1.5,
            max_radius_um=5.0,
            density=2200,
        ),
    ],
    # ----------------------------------------------------
    # MERRA2 - M2T1NXFLX, merra2_surface_flux_table
    #
    'PRECSNO': A[pd.Series, S(resource_type='snowfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    'PRECTOT': A[pd.Series, S(resource_type='rainfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    'PRECTOTCORR': A[pd.Series, S(resource_type='rainfall_mass_rate', unit='kg/m^2/s', agg='mean', freq='h')],
    # ----------------------------------------------------
    # MERRA2 - M2I1NXASM, merra2_meteo_table
    'T2M': A[pd.Series, S(resource_type='air_temperature', unit='degK', freq='h')],
    'U2M': A[pd.Series, S(resource_type='wind_speed', unit='m/s', agg='mean', freq='h')],
    'V2M': A[pd.Series, S(resource_type='wind_speed', unit='m/s', agg='mean', freq='h')],
    # ----------------------------------------------------
    # MERRA2 - M2T1NXLND, merra2_land_surface_table
    'SNODP': A[pd.Series, S(resource_type='snow_depth', unit='m', freq='h')],
    # ----------------------------------------------------
    # MERRA2 - M2T1NXAER, merra2_aerosol_diagnostics_table
    # Total Aerosol Angstrom parameter [470-870 nm]
    'TOTANGSTR': A[pd.Series, S(resource_type=str(R.aerosol_angstrom_exponent), unit='dimensionless', freq='h')],
    # Total Aerosol Extinction AOT [550 nm]
    'TOTEXTTAU': A[pd.Series, S(resource_type=str(R.aerosol_extinction_optical_thickness), unit='dimensionless', freq='h')],
    # Total Aerosol Scattering AOT [550 nm]
    'TOTSCATAU': A[pd.Series, S(resource_type=str(R.aerosol_scattering_optical_thickness), unit='dimensionless', freq='h')],
    # Black Carbon Surface Mass Concentration
    'BCSMASS': A[pd.Series, S(resource_type=str(R.particle_mass_concentration), unit='kg/m^3', freq='h')],
    # Dust Surface Mass Concentration - PM 2.5
    'DUSMASS25': A[pd.Series, S(resource_type=str(R.particle_mass_concentration), unit='kg/m^3', freq='h')],
    # Organic Carbon Surface Mass Concentration __ENSEMBLE__
    'OCSMASS': A[pd.Series, S(resource_type=str(R.particle_mass_concentration), unit='kg/m^3', freq='h')],
    # SO4 Surface Mass Concentration __ENSEMBLE__
    'SO4SMASS': A[pd.Series, S(resource_type=str(R.particle_mass_concentration), unit='kg/m^3', freq='h')],
    # Sea Salt Surface Mass Concentration - PM 2.5
    'SSSMASS25': A[pd.Series, S(resource_type=str(R.particle_mass_concentration), unit='kg/m^3', freq='h')],
    # ----------------------------------------------------
}


def _auto_attr_table(df: pd.DataFrame) -> None:
    if df is None:
        return
    auto_attr_table(
        df,
        series_name_mapping=merra2_series_name_mapping,
        resource_annotations=merra2_resource_annotations,
    )
    for name in df:
        df[name].attrs['datasource'] = 'merra2'


# when requesting data from DB, we add 59min some tolerance to include data with minutes
# originally MERRA2 has data as 00:30, 01:30 ...
def _add_minute_tolerance(interval: pd.Interval) -> pd.Interval:
    minute = interval.right.minute
    result = pd.Interval(interval.left, interval.right + pd.Timedelta(minutes=59 - minute), closed=interval.closed)
    return result


# ----------------------------------------------------
# MERRA2 tables


def get_merra2_table(
    location: Location,
    interval: pd.Interval,
    dataset: str,
) -> pd.DataFrame:
    interval = _add_minute_tolerance(interval)
    query = Query.from_site_environment(location=location, interval=interval)
    query.set_path(f'datasources/merra2/raw/{dataset}/csv')
    result = PvradarClient.instance().get_df(query, crop_interval=interval)
    if not len(result):
        raise DataUnavailableError(interval=interval, where=f'MERRA2 {dataset} dataset')
    _auto_attr_table(result)
    return result


@realign_and_shift_timestamps()
@standard_resource_type(R.merra2_surface_flux_table)
@datasource('merra2')
def merra2_surface_flux_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from MERRA2 M2T1NXFLX dataset
    https://disc.gsfc.nasa.gov/datasets/M2T1NXFLX_5.12.4/summary
    """
    return get_merra2_table(location, interval, 'M2T1NXFLX')


@realign_and_shift_timestamps()
@standard_resource_type(R.merra2_aerosol_mixing_table)
@datasource('merra2')
def merra2_aerosol_mixing_table_raw(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from MERRA2 M2I3NVAER dataset
    https://disc.gsfc.nasa.gov/datasets/M2I3NVAER_5.12.4/summary
    """
    return get_merra2_table(location, interval, 'M2I3NVAER')


@realign_and_shift_timestamps()
@resource_type('aerosol_mixing_ratio_table')
@datasource('merra2')
def merra2_aerosol_mixing_ratio_table(
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
) -> pd.DataFrame:
    data_for_df = {}
    attrs_map = {}
    for name in merra2_aerosol_mixing_table.columns:
        if merra2_aerosol_mixing_table[name].attrs.get('resource_type') == 'particle_mixing_ratio':
            data_for_df[name] = merra2_aerosol_mixing_table[name]
            attrs_map[name] = merra2_aerosol_mixing_table[name].attrs.copy()
    result = pd.DataFrame(data_for_df)
    for name, attrs in attrs_map.items():
        result[name].attrs = attrs
    return result


@realign_and_shift_timestamps()
@standard_resource_type(R.merra2_meteo_table)
@datasource('merra2')
def merra2_meteo_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from M2I1NXASM dataset
    https://disc.gsfc.nasa.gov/datasets/M2I1NXASM_5.12.4/summary
    """
    return get_merra2_table(location, interval, 'M2I1NXASM')


@realign_and_shift_timestamps()
@standard_resource_type(R.merra2_land_surface_table)
@datasource('merra2')
def merra2_land_surface_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from M2T1NXLND dataset
    https://disc.gsfc.nasa.gov/datasets/M2T1NXLND_5.12.4/summary
    """
    return get_merra2_table(location, interval, 'M2T1NXLND')


@realign_and_shift_timestamps()
@standard_resource_type(R.merra2_aerosol_diagnostics_table)
@datasource('merra2')
def merra2_aerosol_diagnostics_table(
    location: Location,
    interval: pd.Interval,
) -> pd.DataFrame:
    """
    Data extracted from M2T1NXAER dataset
    https://disc.gsfc.nasa.gov/datasets/M2T1NXAER_5.12.4/summary
    """
    return get_merra2_table(location, interval, 'M2T1NXAER')


# ----------------------------------------------------
# MERRA2 series (alphabetical order)

SeriesOrDf = TypeVar('T', pd.DataFrame, pd.Series)  # type: ignore


def _merra2_3h_to_1h(df: SeriesOrDf, interval: pd.Interval) -> SeriesOrDf:
    start_datetime = interval.left
    end_datetime = interval.right
    assert isinstance(start_datetime, pd.Timestamp)
    new_index = pd.date_range(start=start_datetime, end=end_datetime, freq='1h')
    df = df.reindex(new_index).interpolate().bfill()
    df.attrs['freq'] = '1h'
    return df


@standard_resource_type(R.air_density, use_default_freq=True)
@datasource('merra2')
def merra2_air_density(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
) -> pd.Series:
    return merra2_aerosol_mixing_table['AIRDENS']


@standard_resource_type(R.air_temperature, use_default_freq=True)
@datasource('merra2')
def merra2_air_temperature(
    *,
    merra2_meteo_table: A[pd.DataFrame, R.merra2_meteo_table],
) -> pd.Series:
    return convert_series_unit(merra2_meteo_table['T2M'], to_unit='degC')


@standard_resource_type(R.particle_mixing_ratio, use_default_freq=True)
@datasource('merra2')
def merra2_particle_mixing_ratio(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    particle_name: str,
) -> pd.Series:
    if particle_name not in merra2_aerosol_mixing_table:
        raise ValueError(f'Particle {particle_name} not found in aerosol mixing table')
    return merra2_aerosol_mixing_table[particle_name]


@standard_resource_type('pm10_volume_concentration', rename=False, use_default_freq=True)
@datasource('merra2')
def merra2_pm10_volume_concentration(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    df = merra2_aerosol_mixing_table
    result = (
        1.375 * df['SO4']
        + df['BCPHOBIC']
        + df['BCPHILIC']
        + df['OCPHOBIC']
        + df['OCPHILIC']
        + df['DU001']
        + df['DU002']
        + df['DU003']
        + 0.74 * df['DU004']
        + df['SS001']
        + df['SS002']
        + df['SS003']
        + df['SS004']
    ) * df['AIRDENS']
    result = _merra2_3h_to_1h(result, interval)
    result.attrs['resource_type'] = 'pm10_volume_concentration'
    result.attrs['unit'] = 'kg/m^3'
    if 'particle_name' in result.attrs:
        del result.attrs['particle_name']
    result.name = 'pm10'
    return result


@standard_resource_type('pm2_5_volume_concentration', rename=False, use_default_freq=True)
@datasource('merra2')
def merra2_pm2_5_volume_concentration(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    df = merra2_aerosol_mixing_table
    result = (
        1.375 * df['SO4']
        + df['BCPHOBIC']
        + df['BCPHILIC']
        + df['OCPHOBIC']
        + df['OCPHILIC']
        + df['DU001']
        + df['DU002']
        + 0.58 * df['DU003']
        + df['SS001']
        + df['SS002']
    ) * df['AIRDENS']
    result = _merra2_3h_to_1h(result, interval)
    result.attrs['resource_type'] = 'pm2_5_volume_concentration'
    result.attrs['unit'] = 'kg/m^3'
    if 'particle_name' in result.attrs:
        del result.attrs['particle_name']
    result.name = 'pm2_5'
    return result


@standard_resource_type(R.total_precipitation_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_total_precipitation_mass_rate(
    merra2_surface_flux_table: A[pd.DataFrame, R.merra2_surface_flux_table],
) -> pd.Series:
    return merra2_surface_flux_table['PRECTOTCORR'].copy()


@standard_resource_type(R.total_precipitation, use_default_freq=True)
@datasource('merra2')
def merra2_total_precipitation(
    merra2_total_precipitation_mass_rate: A[
        pd.Series,
        R.total_precipitation_mass_rate(datasource='merra2', to_unit='kg/m^2/h'),
    ],
) -> pd.Series:
    # given that 1 kg/m^2 == 1mm of water, no need to convert units
    result = merra2_total_precipitation_mass_rate.copy()
    result.attrs['unit'] = 'mm'
    result.attrs['resource_type'] = 'total_precipitation'
    result.attrs['agg'] = 'sum'
    return result


@standard_resource_type(R.rainfall_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall_mass(
    merra2_total_precipitation_mass_rate: A[pd.Series, R.total_precipitation_mass_rate(datasource='merra2')],
) -> pd.Series:
    return merra2_total_precipitation_mass_rate


@standard_resource_type(R.rainfall_rate, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall_rate(
    rainfall_mass_rate: A[pd.Series, R.rainfall_mass_rate(datasource='merra2')],
) -> pd.Series:
    result = rainfall_mass_rate.copy()

    # given that 1 kg/m^2 == 1mm of water,
    # we only need to change the unit
    unit_object = ureg(rainfall_mass_rate.attrs['unit']) / ureg('kg/m^2') * ureg('mm')
    result.attrs['unit'] = str(unit_object)
    result.attrs['resource_type'] = 'rainfall_rate'
    return result


@standard_resource_type(R.rainfall, use_default_freq=True)
@datasource('merra2')
def merra2_rainfall(
    merra2_rainfall_rate: A[pd.Series, R.rainfall_rate(datasource='merra2')],
) -> pd.Series:
    result = rate_to_cumulative(merra2_rainfall_rate, resource_type='rainfall')
    return result


@standard_resource_type(R.relative_humidity, use_default_freq=True)
@datasource('merra2')
def merra2_relative_humidity(
    *,
    merra2_aerosol_mixing_table: A[pd.DataFrame, F(), R.merra2_aerosol_mixing_table],
    interval: pd.Interval,
) -> pd.Series:
    result = _merra2_3h_to_1h(merra2_aerosol_mixing_table['RH'], interval)
    return result


@standard_resource_type(R.snow_depth, use_default_freq=True)
@datasource('merra2')
def merra2_snow_depth(
    *,
    merra2_land_surface_table: A[pd.DataFrame, F(), R.merra2_land_surface_table],
) -> pd.Series:
    return merra2_land_surface_table['SNODP'].copy()


@standard_resource_type(R.snowfall_mass_rate, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall_mass_rate(
    *,
    merra2_surface_flux_table: A[pd.DataFrame, F(), R.merra2_surface_flux_table],
) -> pd.Series:
    return merra2_surface_flux_table['PRECSNO'].copy()


@standard_resource_type(R.snowfall_rate, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall_rate(
    *,
    snowfall_mass_rate: A[pd.Series, F(), R.snowfall_mass_rate],
    snow_density_value: A[float, F()] = 100,
) -> pd.Series:
    result = snowfall_mass_rate / snow_density_value
    unit_object = ureg(snowfall_mass_rate.attrs['unit']) / ureg('kg/m^3')
    result.attrs['unit'] = str(unit_object)
    result.attrs['resource_type'] = 'snowfall_rate'
    return result


@standard_resource_type(R.snowfall, use_default_freq=True)
@datasource('merra2')
def merra2_snowfall(
    *,
    snowfall_rate: A[pd.Series, F(), R.snowfall_rate],
) -> pd.Series:
    result = rate_to_cumulative(snowfall_rate, resource_type='snowfall')
    return result


@standard_resource_type(R.wind_speed, use_default_freq=True)
@datasource('merra2')
def merra2_wind_speed(
    *,
    merra2_meteo_table: A[pd.DataFrame, F(), R.merra2_meteo_table],
) -> pd.Series:
    u2m = merra2_meteo_table['U2M'].to_numpy()
    v2m = merra2_meteo_table['V2M'].to_numpy()
    total = np.sqrt(np.square(u2m) + np.square(v2m))
    result = pd.Series(total, index=merra2_meteo_table.index)
    result.attrs['unit'] = 'm/s'
    result.attrs['resource_type'] = 'wind_speed'
    result.attrs['agg'] = 'mean'
    return result


@standard_resource_type(R.aerosol_angstrom_exponent)
@datasource('merra2')
def merra2_aerosol_angstrom_exponent(
    *,
    merra2_aerosol_diagnostics_table: A[pd.DataFrame, F(), R.merra2_aerosol_diagnostics_table],
) -> pd.Series:
    return merra2_aerosol_diagnostics_table['TOTANGSTR'].copy()


@standard_resource_type(R.aerosol_scattering_optical_thickness)
@datasource('merra2')
def merra2_aerosol_scattering_optical_thickness(
    *,
    merra2_aerosol_diagnostics_table: A[pd.DataFrame, F(), R.merra2_aerosol_diagnostics_table],
) -> pd.Series:
    return merra2_aerosol_diagnostics_table['TOTSCATAU'].copy()


@standard_resource_type(R.aerosol_extinction_optical_thickness)
@datasource('merra2')
def merra2_aerosol_extinction_optical_thickness(
    *,
    merra2_aerosol_diagnostics_table: A[pd.DataFrame, F(), R.merra2_aerosol_diagnostics_table],
) -> pd.Series:
    return merra2_aerosol_diagnostics_table['TOTEXTTAU'].copy()


@standard_resource_type(R.aerosol_absorption_optical_thickness)
@datasource('merra2')
@synchronize_freq('highest')
def merra2_aerosol_absorption_optical_thickness(
    asot: A[pd.Series, F(), R.aerosol_scattering_optical_thickness(datasource='merra2')],
    aext: A[pd.Series, F(), R.aerosol_extinction_optical_thickness(datasource='merra2')],
):
    return aext - asot
