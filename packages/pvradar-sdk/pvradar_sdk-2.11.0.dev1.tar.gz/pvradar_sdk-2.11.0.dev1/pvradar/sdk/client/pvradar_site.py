import warnings
from collections.abc import Iterable
from typing import Any, Mapping, Optional, Self, override
import pandas as pd
from pvlib.location import Location
from .dock.dock_client_utils import measurement_table
from .pvradar_validation import validate_pvradar_attrs
from ..modeling.basics import PvradarResourceType, Attrs, ResourceTypeExtended
from ..modeling.geo_located_model_context import GeoLocatedModelContext
from ..modeling.library_manager import enrich_context_from_libraries
from ..display.map import GeoLocatedDataFrame, display_map
from ..pv.design import (
    ArrayDesign,
    ModuleDesign,
    StructureDesign,
    PvradarSiteDesign,
    FixedStructureDesign,
    make_fixed_design,
    get_azimuth_by_location,
    make_tracker_design,
)


class PvradarSite(GeoLocatedModelContext):
    def __init__(
        self,
        *,
        location: Optional[Location | tuple | str] = None,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        freq: Optional[str] = None,
        design: Optional[PvradarSiteDesign] = None,
        **kwargs,
    ) -> None:
        super().__init__(location=location, interval=interval, default_tz=default_tz, freq=freq, **kwargs)
        enrich_context_from_libraries(self)
        if design is not None:
            self.design = design

    def pvradar_resource_type(self, resource_type: PvradarResourceType, *, attrs: Optional[Attrs] = None, **kwargs):
        warnings.warn(
            '.pvradar_resource_type() is deprecated, use .resource(attrs(resource_type=...)) instead', DeprecationWarning
        )
        req: dict[str, Any] = {'resource_type': resource_type}
        if attrs:
            new_req = dict(attrs.copy())
            new_req.update(req)
            req = new_req

        return self.resource(req, **kwargs)

    @override
    def _convert_by_attrs(self, value: Any, param_attrs: Mapping[str, Any]) -> Any:
        if not self.config.get('disable_validation'):
            validate_pvradar_attrs(param_attrs)
        return super()._convert_by_attrs(value, param_attrs)

    @property
    def design(self) -> PvradarSiteDesign:
        return self.resource('design')

    @design.setter
    def design(self, value: PvradarSiteDesign):
        self['design'] = value

    @override
    def on_resource_set(self, key: str, value: Any) -> Any:
        if key == 'design':
            if not isinstance(value, PvradarSiteDesign):
                raise ValueError(f'Expected PvradarSiteDesign, got {value.__class__.__name__}')
        value = super().on_resource_set(key, value)

        def maybe_change_azimuth(design: PvradarSiteDesign, location: Location):
            structure = design.array.structure
            if isinstance(structure, FixedStructureDesign):
                if structure.use_azimuth_by_location and structure.azimuth in (0, 180):
                    structure.azimuth = get_azimuth_by_location(location)

        if key == 'design' and 'location' in self:
            maybe_change_azimuth(value, self.location)
        elif key == 'location' and 'design' in self:
            maybe_change_azimuth(self.design, value)

        return value

    @property
    def array(self) -> ArrayDesign:
        return self.design.array

    @property
    def module(self) -> ModuleDesign:
        return self.array.module

    @property
    def structure(self) -> StructureDesign:
        return self.array.structure

    @override
    def __repr__(self):
        response = 'Pvradar site'
        if 'location' in self:
            response += f' at {self.location}'
        if 'interval' in self:
            response += f' with interval {self.interval}'
        return response

    @classmethod
    def as_fixed_array(
        cls,
        *,
        # site parameters
        location: Location | tuple | str,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        #
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
    ) -> Self:
        """convenience method creating site with a single fixed array in one call"""
        instance = cls(
            location=location,
            interval=interval,
            default_tz=default_tz,
        )
        if azimuth is None:
            azimuth = get_azimuth_by_location(instance.location)
        design = make_fixed_design(
            tilt=tilt,
            azimuth=azimuth,
            clearance=clearance,
            #
            # common design parameters
            module_rated_power=module_rated_power,
            dc_capacity=dc_capacity,
            dc_ac_ratio=dc_ac_ratio,
            module_placement=module_placement,
        )
        instance.design = design
        return instance

    @classmethod
    def as_tracker_array(
        cls,
        *,
        # site parameters
        location: Location | tuple | str,
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        #
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
    ) -> Self:
        """convenience method creating site with a single array with a tracker in one call"""
        instance = cls(
            location=location,
            interval=interval,
            default_tz=default_tz,
        )
        design = make_tracker_design(
            axis_height=axis_height,
            axis_azimuth=axis_azimuth,
            axis_tilt=axis_tilt,
            max_tracking_angle=max_tracking_angle,
            night_stow_angle=night_stow_angle,
            backtracking=backtracking,
            #
            # common design parameters
            module_rated_power=module_rated_power,
            dc_capacity=dc_capacity,
            dc_ac_ratio=dc_ac_ratio,
            module_placement=module_placement,
        )
        instance.design = design
        return instance

    def measurement_table(
        self,
        *,
        max_distance_km: Optional[float] = 1000,
        private: Optional[bool] = None,
        resource_type: ResourceTypeExtended | Iterable[ResourceTypeExtended] | None = None,
        ids: Optional[Iterable[str]] = None,
        **kwargs,
    ) -> GeoLocatedDataFrame:
        """returns a table of all measurements in the vicinity of the site"""
        if self.location is None:
            raise ValueError('Location must be set before querying measurement_table')
        exclude_ids = None
        if hasattr(self, 'measurement_group_id'):
            exclude_ids = [getattr(self, 'measurement_group_id')]
        return measurement_table(
            location=self.location,
            max_distance_km=max_distance_km,
            private=private,
            resource_type=resource_type,
            exclude_ids=exclude_ids,
            ids=ids,
            **kwargs,
        )

    def display_map(
        self,
        table: pd.DataFrame,
        color_by: Optional[str] = None,
        size_by: Optional[str] = None,
        autofit: bool = True,
        figsize: Optional[tuple[Any, Any]] = None,
    ):
        """
        Displays a map with station locations from the measurement table.

        Args:
            center_tooltip (str | None): Tooltip for the center of the map.
            color_by (str | None): Column name for color scaling.
            size_by (str | None): Column name for marker size scaling.
            autofit (bool): Whether to fit the map to the data.

        Returns:
            GeoLocatedDataFrame: Map with markers.
        """
        return display_map(
            table,
            center=self.location,
            center_tooltip='Site Location',
            color_by=color_by,
            size_by=size_by,
            autofit=autofit,
            figsize=figsize,
        )
