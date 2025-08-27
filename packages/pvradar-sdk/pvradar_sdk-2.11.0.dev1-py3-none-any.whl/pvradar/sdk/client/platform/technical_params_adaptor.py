from typing import Any, Mapping
from ...pv.design import (
    ArrayDesign,
    GridDesign,
    InverterDesign,
    ModuleDesign,
    FixedStructureDesign,
    PvradarSiteDesign,
    TrackerStructureDesign,
    TransformerDesign,
)
from pvlib.location import Location


def make_array_design(input: Mapping[str, Any], location: Location) -> ArrayDesign:
    hub_module = input['moduleDesign']
    module = ModuleDesign(
        rated_power=hub_module['nameplatePower'],
        long_side=hub_module['longSide'],
        short_side=hub_module['shortSide'],
        bifaciality_factor=hub_module['bifacialityFactor'],
    )
    inverter = InverterDesign(
        rated_power=input['invDesign']['nameplateNominalPower'],
    )

    hub_structure = input['structure']
    structure = None
    if hub_structure['structureType'] == 'fixed':
        structure = FixedStructureDesign(
            azimuth=180 if location.latitude > 0 else 0,
            tilt=hub_structure['tilt'] if not hub_structure['hasTiltByLatitude'] else location.latitude,
        )
    elif hub_structure['structureType'] == 'tracker':
        structure = TrackerStructureDesign(
            max_tracking_angle=hub_structure['trackingAngle'],
        )
        if 'nightStowAngle' in hub_structure:
            structure.night_stow_angle = float(hub_structure['nightStowAngle'])
    else:
        raise ValueError(f'Unknown structure type: {hub_structure["structureType"]}')

    rated_dc_power = input['modulesPerString'] * input['stringCount'] * module.rated_power

    return ArrayDesign(
        module=module,
        structure=structure,
        inverter=inverter,
        rated_dc_power=rated_dc_power,
        module_placement=hub_structure['placementType'],
        ground_cover_ratio=input['layout']['groundCoverRatio'],
        dc_ac_ratio=input['dcAcRatio'],
    )


def make_site_design(hub_design: Mapping[str, Any], location: Location) -> PvradarSiteDesign:
    array_designs = [make_array_design(array, location) for array in hub_design['subarrays']]
    grid = GridDesign()
    if 'gridLimit' in hub_design['grid']:
        grid.grid_limit = hub_design['grid']['gridLimit']

    return PvradarSiteDesign(
        arrays=array_designs,
        transformer=TransformerDesign(),
        grid=grid,
    )
