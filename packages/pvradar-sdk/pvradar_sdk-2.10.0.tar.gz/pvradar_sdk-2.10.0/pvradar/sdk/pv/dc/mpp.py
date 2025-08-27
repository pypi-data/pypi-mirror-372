"""
Estimate the output of a PV module at Maximum-Power-Point (MPP) conditions.
"""

from typing import Annotated
import pvlib
import pandas as pd
from ..design import ArrayDesign, ModuleDesign
from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling.basics import LambdaArgument


@standard_resource_type(R.dc_power, override_unit=True)
@synchronize_freq('default')
def pvlib_pvsystesm_pvwatts_dc(
    effective_poa: Annotated[pd.Series, R.effective_poa],
    cell_temp: Annotated[pd.Series, R.cell_temperature],
    rated_dc_power: Annotated[float, LambdaArgument(ArrayDesign, lambda d: d.rated_dc_power)],
    gamma_pdc: Annotated[float, LambdaArgument(ModuleDesign, lambda d: d.temperature_coefficient_power)],
    module_power: Annotated[float, LambdaArgument(ModuleDesign, lambda d: d.rated_power)],
    ref_temp: float = 25.0,
) -> pd.Series:
    #  g_poa_effective is deprecated in pvlib >= 0.13.0, use effective_irradiance instead
    if pvlib.__version__ >= '0.13.0':
        power_one_module = pvlib.pvsystem.pvwatts_dc(
            effective_irradiance=effective_poa,  # pyright: ignore[reportCallIssue]
            temp_cell=cell_temp,
            pdc0=module_power,
            gamma_pdc=gamma_pdc,
            temp_ref=ref_temp,
        )
    else:
        power_one_module = pvlib.pvsystem.pvwatts_dc(
            g_poa_effective=effective_poa,  # pyright: ignore[reportCallIssue]
            temp_cell=cell_temp,
            pdc0=module_power,
            gamma_pdc=gamma_pdc,
            temp_ref=ref_temp,
        )
    dc_power = power_one_module / module_power * rated_dc_power
    return dc_power


@standard_resource_type(R.dc_energy, override_unit=True)
def pvradar_dc_energy_from_power(
    dc_power: Annotated[pd.Series, R.dc_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(dc_power, str(R.dc_power))
