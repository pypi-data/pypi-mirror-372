from dataclasses import dataclass
from typing import Annotated, Any, Literal, List, Optional
from pydantic import Field
from pvlib.location import Location
import math
import pandas as pd


StructureType = Literal['fixed', 'tracker']
ModuleOrientation = Literal['horizontal', 'vertical']
ModuleConstruction = Literal['glass_glass', 'glass_polymer']


# ----------------------------- HELPERS ----------------------------------------


def sin_deg(angle_deg: float) -> float:
    """
    The sine of an angle given in degrees.
    """
    angle_rad = math.radians(angle_deg)  # Convert degrees to radians
    return math.sin(angle_rad)


# ----------------------------- PV MODULE ----------------------------------------


@dataclass
class ModuleDesign:
    rated_power: float
    """The power of the module under standard-test conditions (STC): 25°C and 1000
    W/m^2"""

    short_side: float = 1
    """The length of the short side of the module [m]"""

    long_side: float = 2
    """The length of the long side of the module [m]"""

    bifaciality_factor: float = 0
    """A unit-less factor with values between 0 and 1 that describes the ratio of
    the efficiency of the rear side of the module and the efficiency of the front
    side. Bifacial modules typically have a bifaciality factor or 0.7, monofacial
    modules have a bifaciality factor of zero."""

    degradation_rate: float = 0
    """The rate of power reduction over time [%/year]"""

    temperature_coefficient_power: float = -0.003
    """The temperature coefficient of the maximum power point [1/°C]"""

    cell_string_count: int = 3
    """The number of parallel strings into which all cells of the module are
    divided [dimensionless]."""

    half_cell: bool = False
    """True: half-cell module, False: full-cell module."""

    module_construction: ModuleConstruction = 'glass_polymer'
    """Choose between 'glass_polymer' and 'glass_glass'"""

    @property
    def module_area(self) -> float:
        """The area of the module [m^2]."""
        return self.short_side * self.long_side


# ----------------------------- INVERTER -----------------------------------------
@dataclass
class InverterDesign:
    rated_power: float
    nominal_efficiency: float = 0.98
    # TODO: Finalize, review how pvlib implements inverters


# ----------------------------- FIXED-TILT STRUCTURE -----------------------------
@dataclass
class FixedStructureDesign:
    tilt: float
    """The tilt angle of the module surface [degees]. A value of 0 means modules
    are facing up. A Value of 90 means modules are facing the horizon. Values must
    be >= 0 and <= 90."""

    azimuth: float = 180
    """The azimuth angle of the module surface. A value of 0 means modules are facing
    north [degrees] In the northern hemisphere fixed-tilt structures are typically
    oriented towards the south (azimuth = 180 degrees), while in the southern
    hemisphere they are typically oriented towards the north (azimuth = 0 degrees).
    Values must be >= 0 and <= 360.
    """

    clearance: float = 1
    """The shortest distance between any module and the ground [m]. Values must be >= 0"""

    rear_side_shading_factor = 0.1
    """The fraction of rear-side irradiance blocked by mechanical components behind the
    module, reducing the effective light contribution to energy generation."""

    use_azimuth_by_location: bool = True
    """If True, then after assigning the location to the site, the azimuth will be automatically
    adjusted based on location"""


# ----------------------------- TRACKER STRUCTURE --------------------------------
@dataclass
class TrackerStructureDesign:
    axis_height: float = 1.5
    """The distance between the axis of rotation and the ground [m]."""

    axis_azimuth: float = 0
    """The angle between the tracker axis and a line oriented toward true north
    [degrees]. Values must be >=0 and <=90. A value of 0 means the tracker axis is
    oriented north-south. A value of 90 means the tracker axis is oriented
    east-west."""

    axis_tilt: float = 0
    """The angle between the axis of rotation and a flat horizontal surface
    [degrees]. Values must be >= 0 and <= 45 degrees."""

    max_tracking_angle: float = 60
    """The maximum possible rotation angle [degrees]. Commercial
    horizontal-single-axis-trackers (HSAT) allow tracking angles up to 50-60
    degrees. Values must be >= 0 and <= 90 degrees."""

    night_stow_angle: float = 0
    """The angle at which the tracker is stowed at night [degrees]. Values must
    be >= 0 and <= 90 degrees."""

    backtracking: bool = True
    """True: backtracking enabled, False: No backtracking"""

    rear_side_shading_factor = 0.1
    """The fraction of rear-side irradiance blocked by mechanical components behind the
    module, reducing the effective light contribution to energy generation."""


# ----------------------------- ARRAY --------------------------------------------
type StructureDesign = FixedStructureDesign | TrackerStructureDesign


@dataclass
class ArrayDesign:
    # --- Components ---

    module: ModuleDesign
    """The PV modules mounted on the structure."""

    structure: StructureDesign
    """Modules are either mounted on a rigid structure with a fixed tilt angle or
    on a Horizontal-Single-Axis-Tracker (HSAT), following the sun from east to west."""

    inverter: InverterDesign
    """The inverter transforming DC to AC current."""

    # --- Arrangement of components ---
    rated_dc_power: float
    """The rated DC power of the array meaning the nominal module power at STC
    conditions multiplied
    with the number of modules [W]. Also called the DC capacity."""

    module_placement: Annotated[str, Field('2v', pattern=r'^\d[vh]$')]  # placement_type
    """A string identifying the arrangement of modules on the structure. For example,
    '2v' indicates two vertically oriented (portrait) modules in the cross-section of
    the structure, with their short sides aligned with the structure's main axis.
    Conversely, '3h' indicates three horizontally oriented (landscape) modules, with
    their long sides aligned with the structure's main axis."""

    dc_ac_ratio: float = 1.2
    """The ratio between the nominal dc and the nominal ac power [fraction]."""

    ground_cover_ratio: float = 0.35
    """The ratio between the collector width and the structure pitch."""

    modules_per_string: int = 28
    """The number of modules per string."""

    modules_per_structure: int = 84
    """The number of modules installed per structure. Typically this number is a
    multiple of the number of modules per string."""

    structures_per_structure_line: int = 1
    """The number of structures connected to lines for efficient robotic cleaning."""

    # --- Ground below PV modules ---

    albedo_value: float = 0.2
    """A single value describing the albedo of the ground below the modules [fraction].
    The default value is 0.2 meaning that 20% of the incoming irradiance is reflected
    (in all directions)."""

    slope_tilt: float = 0
    """The angle of the slope (ground) containing the tracker axes, relative to horizontal
    [degrees]. The default is zero degrees (flat surface)."""

    slope_azimuth: float = 0
    """Direction of the normal to the slope (ground) containing the tracker axes, when
    projected on the horizontal [degrees]. The default is zero degrees (flat surface)."""

    # --- Properties ---

    @property
    def module_count(self) -> float:
        """The number of PV modules belonging to this array."""
        return self.rated_dc_power / self.module.rated_power

    @property
    def rated_ac_power(self) -> float:
        """The nominal ac power of the array meaning the nominal inverter power
        multiplied with the number of inverters [W]. Also called the AC capacity."""
        return self.rated_dc_power / self.dc_ac_ratio

    @property
    def inverter_count(self) -> float:
        """The number of inverters belonging to this array."""
        return self.rated_dc_power / self.inverter.rated_power

    @property
    def string_count(self) -> float:
        """The number of strings belonging to this array."""
        return self.module_count / self.modules_per_string

    @property
    def structure_count(self) -> float:
        """The number of structures belonging to this array."""
        return self.module_count / self.modules_per_structure

    @property
    def total_module_surface_area(self) -> float:  # area_sizing
        """The total module surface area belonging to this array [m^2]."""
        return self.module_count * self.module.module_area

    @property
    def structure_type(self) -> StructureType:
        """The type of structure used: fixed or tracker"""
        if isinstance(self.structure, FixedStructureDesign):
            return 'fixed'
        else:
            return 'tracker'

    @property
    def module_orientation(self) -> ModuleOrientation:
        """The orientation of the long side of the module
        Two options: horizontal, vertical"""
        orientation_char = self.module_placement[1]
        if orientation_char == 'v':
            return 'vertical'
        else:
            return 'horizontal'

    @property
    def number_modules_cross_section(self) -> int:
        """The number of modules in the cross-section of the structure."""
        return int(self.module_placement[0])

    @property
    def collector_width(self) -> float:
        """The width of the rectangle formed by the PV modules placed on top of the structure."""
        if self.module_orientation == 'horizontal':
            return self.number_modules_cross_section * self.module.short_side
        else:  # 'vertical'
            return self.number_modules_cross_section * self.module.long_side

    @property
    def module_clearance(self) -> float:
        """The shortest distance (at any moment of the day) between the lower edge of any PV module and the ground."""
        if isinstance(self.structure, FixedStructureDesign):
            return self.structure.clearance
        else:
            return self.structure.axis_height - 0.5 * self.collector_width * sin_deg(self.structure.max_tracking_angle)

    @property
    def pitch(self) -> float:
        """The distance between the axes of two adjacent structures [m]"""
        return self.collector_width / self.ground_cover_ratio


# ----------------------------- TRANSFORMER --------------------------------------
@dataclass
class TransformerDesign:
    no_load_loss = 0.2 / 100
    """The constant losses experienced by a transformer, even when the transformer is not under load.
    % of transformer rating [fraction]."""

    full_load_loss = 0.7 / 100
    """The load dependent losses experienced by the transformer. % of transformer rating [fraction]."""


# ----------------------------- GRID ---------------------------------------------
@dataclass
class GridDesign:
    grid_limit: float | pd.Series | None = None


# ----------------------------- SITE ----------------------------------------
@dataclass
class PvradarSiteDesign:
    arrays: List[ArrayDesign]
    transformer: TransformerDesign  # ac
    grid: GridDesign

    @property
    def array(self) -> ArrayDesign:
        if not self.arrays:
            raise ValueError('No arrays defined in the design')
        if len(self.arrays) == 1:
            return self.arrays[0]
        else:
            raise NotImplementedError(f'.array property ambiguous, since site design has {len(self.arrays)} arrays')

    def _make_base_design_spec(self) -> dict[str, Any]:
        return dict(
            module_rated_power=self.array.module.rated_power,
            dc_capacity=self.array.rated_dc_power,
            dc_ac_ratio=self.array.dc_ac_ratio,
            module_placement=self.array.module_placement,
            ground_cover_ratio=self.array.ground_cover_ratio,
            grid_limit=self.grid.grid_limit,
        )

    def to_tracker_design_spec(self) -> dict[str, Any]:
        s = self.array.structure
        assert isinstance(s, TrackerStructureDesign), 'Site design must have a tracker structure'
        return dict(
            **self._make_base_design_spec(),
            axis_height=s.axis_height,
            axis_azimuth=s.axis_azimuth,
            axis_tilt=s.axis_tilt,
            max_tracking_angle=s.max_tracking_angle,
            night_stow_angle=s.night_stow_angle,
            backtracking=s.backtracking,
        )

    def to_fixed_design_spec(self) -> dict[str, Any]:
        s = self.array.structure
        assert isinstance(s, FixedStructureDesign), 'Site design must have a fixed structure'
        return dict(
            **self._make_base_design_spec(),
            tilt=s.tilt,
            azimuth=s.azimuth,
            clearance=s.clearance,
        )


# ----------------------------- FACTORY FUNCTIONS ---------------------------


def _make_site_design(
    *,
    structure_design: StructureDesign,
    module_rated_power: float = 400,
    dc_capacity: float = 100 * 1e6,  # 100 MW
    dc_ac_ratio: float = 1.2,
    module_placement='2v',
    grid_limit: Optional[float] = None,
    ground_cover_ratio: float = 0.35,
) -> PvradarSiteDesign:
    module = ModuleDesign(rated_power=module_rated_power)
    inverter = InverterDesign(rated_power=10000)
    array = ArrayDesign(
        module=module,
        structure=structure_design,
        inverter=inverter,
        rated_dc_power=dc_capacity,
        dc_ac_ratio=dc_ac_ratio,
        module_placement=module_placement,
        ground_cover_ratio=ground_cover_ratio,
    )
    grid = GridDesign(grid_limit=grid_limit)
    transformer = TransformerDesign()
    site_design = PvradarSiteDesign(
        arrays=[array],
        transformer=transformer,
        grid=grid,
    )
    return site_design


def get_azimuth_by_location(location: Location) -> float:
    return 180 if location.latitude > 0 else 0


def make_fixed_design(
    *,
    # structure parameters
    tilt: float = 20,
    azimuth: Optional[float] = None,
    clearance: float = 1,
    #
    # common design parameters
    module_rated_power: float = 400,
    dc_capacity: float = 100 * 1e6,  # 100 MW
    dc_ac_ratio: float = 1.2,
    module_placement='2v',
    grid_limit: Optional[float] = None,
    ground_cover_ratio: float = 0.35,
):
    """
    Create a fixed-tilt single-array design

    Args:
        azimuth: The azimuth angle of the module surface. If None, it will be set
            to 180 degrees in the northern hemisphere and 0 degrees in the southern
    """
    use_azimuth_by_location = azimuth is None
    azimuth = azimuth if azimuth is not None else 180
    structure = FixedStructureDesign(
        tilt=tilt,
        azimuth=azimuth,
        clearance=clearance,
        use_azimuth_by_location=use_azimuth_by_location,
    )
    site_design = _make_site_design(
        structure_design=structure,
        module_rated_power=module_rated_power,
        dc_capacity=dc_capacity,
        dc_ac_ratio=dc_ac_ratio,
        module_placement=module_placement,
        grid_limit=grid_limit,
        ground_cover_ratio=ground_cover_ratio,
    )
    return site_design


def make_tracker_design(
    *,
    # structure parameters
    axis_height: float = 1.5,
    axis_azimuth: float = 0,
    axis_tilt: float = 0,
    max_tracking_angle: float = 60,
    night_stow_angle: float = 0,
    backtracking: bool = True,
    #
    # common design parameters
    module_rated_power: float = 400,
    dc_capacity: float = 100 * 1e6,  # 100 MW
    dc_ac_ratio: float = 1.2,
    module_placement='2v',
    grid_limit: Optional[float] = None,
    ground_cover_ratio: float = 0.35,
):
    structure = TrackerStructureDesign(
        axis_height=axis_height,
        axis_azimuth=axis_azimuth,
        axis_tilt=axis_tilt,
        max_tracking_angle=max_tracking_angle,
        night_stow_angle=night_stow_angle,
        backtracking=backtracking,
    )
    site_design = _make_site_design(
        structure_design=structure,
        module_rated_power=module_rated_power,
        dc_capacity=dc_capacity,
        dc_ac_ratio=dc_ac_ratio,
        module_placement=module_placement,
        grid_limit=grid_limit,
        ground_cover_ratio=ground_cover_ratio,
    )
    return site_design
