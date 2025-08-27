"""
Estimate the inverter power output.
"""

from typing import Annotated
import pvlib
import pandas as pd
from ..design import ArrayDesign, InverterDesign
from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_to_resource
from ...modeling.basics import LambdaArgument
from pydantic import Field


@standard_resource_type(R.inverter_power, override_unit=True)
def pvlib_inverter_pvwatts(
    dc_power: Annotated[pd.Series, R.dc_power],
    rated_ac_power: Annotated[float, LambdaArgument(ArrayDesign, lambda d: d.rated_ac_power)],
    nom_inv_eff: Annotated[float, LambdaArgument(InverterDesign, lambda d: d.nominal_efficiency)],
    ref_inv_eff: Annotated[float, Field(gt=0)] = 0.9637,
) -> pd.Series:
    """
    This simplified model describes all inverters as one big inverter connected to the all dc modules.
    """
    inverter_power = pvlib.inverter.pvwatts(
        pdc=dc_power,
        pdc0=rated_ac_power,
        eta_inv_nom=nom_inv_eff,
        eta_inv_ref=ref_inv_eff,
    )
    return inverter_power


@standard_resource_type(R.inverter_energy, override_unit=True)
def pvradar_inverter_energy_from_power(
    inverter_power: Annotated[pd.Series, R.inverter_power(to_unit='W')],
):
    return convert_to_resource(
        inverter_power,
        R.inverter_energy(to_freq='h', set_unit='Wh'),
    )
