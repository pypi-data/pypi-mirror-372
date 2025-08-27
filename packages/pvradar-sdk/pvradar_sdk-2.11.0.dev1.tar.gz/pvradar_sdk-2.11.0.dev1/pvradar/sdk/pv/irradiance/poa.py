from ...modeling.decorators import standard_resource_type, synchronize_freq
from ...modeling import R
from typing import Literal, Annotated
import pandas as pd


ModuleSide = Literal['both', 'front', 'back']


### --- GLOBAL PLANE OF ARRAY IRRADIANCE --- ###


@standard_resource_type(R.global_poa_on_front, override_unit=True)
@synchronize_freq('default')
def sum_global_poa_on_front(
    ground_diffuse_poa_on_front: Annotated[pd.Series, R.ground_diffuse_poa_on_front],
    sky_diffuse_poa_on_front: Annotated[pd.Series, R.sky_diffuse_poa_on_front],
    direct_poa_on_front: Annotated[pd.Series, R.direct_poa_on_front],
) -> pd.Series:
    """
    The global irradiance on the front side of a tilted or tracked pv module.
    'global' means sum of all components but without losses.
    """
    global_on_front = ground_diffuse_poa_on_front + sky_diffuse_poa_on_front + direct_poa_on_front
    global_on_front = global_on_front.fillna(0)
    if 'datasource' in global_on_front.attrs:
        del global_on_front.attrs['datasource']
    return global_on_front


# @standard_resource_type(R.global_poa_on_back, override_unit=True)
# def sum_global_poa_on_back(
#     ground_diffuse_poa_on_back: Annotated[pd.Series, R.ground_diffuse_poa_on_back],
# ) -> pd.Series:
#     """
#     The global irradiance on the front side of a tilted or tracked pv module.
#     'global' means sum of all components but without losses.
#     """
#     global_on_rear = ground_diffuse_poa_on_back.copy()
#     global_on_rear = global_on_rear.fillna(0)
#     return global_on_rear


@standard_resource_type(R.global_poa, override_unit=True)
@synchronize_freq('default')
def sum_global_poa(
    poa_on_front: Annotated[pd.Series, R.global_poa_on_front],
    # poa_on_rear: Annotated[pd.Series, R.global_poa_on_back],
) -> pd.Series:
    return poa_on_front  # + poa_on_rear


### --- EFFECTIVE POA IRRADIANCE --- ###
@standard_resource_type(R.effective_poa, override_unit=True)
@synchronize_freq('default')
def pvradar_effective_poa(
    ground_diffuse_poa_on_front: Annotated[pd.Series, R.ground_diffuse_poa_on_front],
    sky_diffuse_poa_on_front: Annotated[pd.Series, R.sky_diffuse_poa_on_front],
    direct_poa_on_front: Annotated[pd.Series, R.direct_poa_on_front],
    # ground_diffuse_poa_on_back: pd.Series,
    soiling_loss_factor: Annotated[pd.Series, R.soiling_loss_factor],
    snow_loss_factor: Annotated[pd.Series, R.snow_loss_factor],
    reflection_loss_factor: Annotated[pd.Series, R.reflection_loss_factor],
    # array: ArrayDesign,
) -> pd.Series:
    diffuse_on_front = ground_diffuse_poa_on_front + sky_diffuse_poa_on_front
    effective_on_front = (
        (diffuse_on_front + direct_poa_on_front * (1 - reflection_loss_factor))
        # * (1 - spectral_mismatch_loss_factor) # to be added later
        * (1 - soiling_loss_factor)
        * (1 - snow_loss_factor)
    )
    # effective_on_rear = (
    #     ground_diffuse_poa_on_back * (1 - array.structure.rear_side_shading_factor) * array.module.bifaciality_factor
    #     # * spectral_mismatch_loss_factor # to be added later
    # )
    effective_poa = effective_on_front  # + effective_on_rear
    return effective_poa
