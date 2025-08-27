from typing import Annotated
import pvlib
import pandas as pd
import pvlib.transformer

from ...modeling.decorators import standard_resource_type
from ...modeling import R
from ...modeling.utils import convert_power_to_energy_Wh
from ...modeling.basics import LambdaArgument
from ...pv.design import TransformerDesign, ArrayDesign


@standard_resource_type(R.ac_power, override_unit=True)
def pvlib_transformer_simple_efficiency(
    inverter_power: Annotated[pd.Series, R.inverter_power],
    no_load_loss: Annotated[float, LambdaArgument(TransformerDesign, lambda d: d.no_load_loss)],
    full_load_loss: Annotated[float, LambdaArgument(TransformerDesign, lambda d: d.full_load_loss)],
    transformer_rating: Annotated[float, LambdaArgument(ArrayDesign, lambda d: d.rated_ac_power)],
) -> pd.Series:
    ac_power = pvlib.transformer.simple_efficiency(
        input_power=inverter_power,
        no_load_loss=no_load_loss,
        load_loss=full_load_loss,
        transformer_rating=transformer_rating,  # match inverter rating
    )
    return ac_power


@standard_resource_type(R.ac_energy)
def pvradar_ac_energy_from_power(
    ac_power: Annotated[pd.Series, R.ac_power(to_unit='W')],
):
    return convert_power_to_energy_Wh(ac_power, str(R.ac_energy))
