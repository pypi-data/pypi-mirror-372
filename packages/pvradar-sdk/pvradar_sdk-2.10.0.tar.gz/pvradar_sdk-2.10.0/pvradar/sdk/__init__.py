# ruff: noqa
from .client.api_query import Query
from .client.client import PvradarClient
from .client.platform.pvradar_project import PvradarProject
from .client.pvradar_site import PvradarSite
from .common.constants import API_VERSION
from .common.pandas_utils import interval_to_index, interval_from_series, crop_by_interval
from .common.pvradar_location import PvradarLocation
from .common.exceptions import *
from .common.constants import SDK_VERSION as __version__
from .display.describe import *
from .display.plotting import resource_plot
from .display.map import display_map
from .modeling import *
from .pv.design import *
from .measurements import MeasurementGroup

__all__ = [
    '__version__',
    # ------------------------------
    'PvradarProject',
    'PvradarSite',
    'PvradarClient',
    'Query',
    'API_VERSION',
    # ------------------------------
    # Exceptions
    'DataUnavailableError',
    'ApiError',
    'PvradarSdkError',
    # ------------------------------
    # Basics
    #
    'ModelConfig',
    'ModelParamAttrs',
    'attrs',
    'Attrs',
    'Datasource',
    'LambdaArgument',
    'PvradarLocation',
    'PvradarResourceType',
    'is_pvradar_resource_type',
    # ------------------------------
    # Model Contexts
    #
    'ModelContext',
    'ModelWrapper',
    'GeoLocatedModelContext',
    # ------------------------------
    # Decorators
    #
    'set_unit',
    'to_unit',
    'label',
    'resource_type',
    'pvradar_resource_type',
    'audience',
    # ------------------------------
    # Utils
    #
    'resample_series',
    'convert_series_unit',
    'convert_to_resource',
    'ureg',
    # ------------------------------
    # PV Design
    #
    'ModuleDesign',
    'ArrayDesign',
    'PvradarSiteDesign',
    'FixedStructureDesign',
    'TrackerStructureDesign',
    'StructureDesign',
    # Hooks
    #
    'for_argument',
    'for_resource',
    'use_arguments',
    # Measurements
    #
    'MeasurementGroup',
    #
    # Display
    #
    'resource_plot',
    'describe',
    'display_map',
    # ------------------------------
    # Other
    #
    'PvradarProfiler',
    'R',
    'interval_from_series',
    'interval_to_index',
    'crop_by_interval',
    'load_libraries',
    'BaseModelContext',
    'measurements',
]
