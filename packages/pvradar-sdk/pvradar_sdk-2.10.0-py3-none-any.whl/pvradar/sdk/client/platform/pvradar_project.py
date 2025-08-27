from typing import Any, Optional, TypeVar, override
import warnings

from ...modeling.resource_types._list import PvradarResourceType
from ...modeling.model_wrapper import ModelBinding
from ...common.pvradar_location import PvradarLocation
from ...common.pandas_utils import period_str_to_interval
from ...modeling.basics import ModelParam
from ...modeling.model_context import ModelContext
from ...modeling.model_binder import AbstractBinder
from ..engine.engine_types import ModelContextLocator
from ..pvradar_site import GeoLocatedModelContext, PvradarSite
from ..client import PvradarClient
from ..api_query import Query
from ..platform.schemas import IAssembly, IProjectManifest
from .vtables import is_vtable, maybe_extend_df_with_dates, timed_vtable_to_df, vtable_to_df, is_timed_vtable
from .schemas import AssemblyName
from ..platform.technical_params_adaptor import make_site_design
from ...pv.design import make_fixed_design, make_tracker_design


_variant_id_map = {
    'snow-loss': 'wizard-snow-loss',
    'snow-v2': 'wizard-snow-loss',
    'cleaning': 'wizard-no-cleaning',
    'cascade': 'wizard-no-cleaning',
    'albedo-enhancer': 'wizard-albedo-improved',
}


def _remove_none_values(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


SelfType = TypeVar('SelfType', bound='GeoLocatedModelContext')


class PvradarProjectBinder(AbstractBinder):
    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        assert isinstance(context, PvradarProject)
        if resource_name == 'design':
            tp = context.platform_technical_params_base
            context['design'] = make_site_design(tp['design'], context.location)
            return context['design']

        if as_param and as_param.attrs:
            resource_type: PvradarResourceType = as_param.attrs.get('resource_type')  # type: ignore
            # TODO: reconsider this check
            if resource_type == 'soiling_loss_factor' and False:
                model = context.models['project_soiling_loss_factor']
                return ModelBinding(model=model, defaults=defaults or {})


def fetch_project_manifest(project_id: str) -> IProjectManifest:
    client = PvradarClient.instance()
    query = Query(project_id=project_id, path='manifest')
    data = client.get_json(query)
    if 'data' not in data and 'errors' in data:
        raise LookupError(f'Error fetching project manifest for {project_id}: {data["errors"][0]["detail"]}')
    if 'data' not in data or 'attributes' not in data['data']:
        raise RuntimeError(f'Unexpected JSON:API response while fetching project manifest for {project_id}')
    result = data['data']['attributes']
    return result


class PvradarProject(PvradarSite):
    def __init__(
        self,
        project_id: str,
        *,
        default_variant_id: Optional[str] = '',
        interval: Optional[Any] = None,
        default_tz: Optional[str] = None,
        **kwargs,
    ) -> None:
        new_kwargs = kwargs.copy()
        if 'platform_project_manifest' not in new_kwargs:
            new_kwargs['platform_project_manifest'] = fetch_project_manifest(project_id)
        if (
            not default_tz
            and 'default_tz' in new_kwargs['platform_project_manifest']
            and new_kwargs['platform_project_manifest']
        ):
            default_tz = new_kwargs['platform_project_manifest']['default_tz']
        if 'location' not in new_kwargs:
            m = new_kwargs['platform_project_manifest']
            new_kwargs['location'] = PvradarLocation(
                latitude=m['location']['lat'],
                longitude=m['location']['lon'],
            )
            if default_tz:
                new_kwargs['location'].tz = default_tz
        if not interval and 'interval' in new_kwargs['platform_project_manifest']:
            period_str = new_kwargs['platform_project_manifest']['interval']
            if isinstance(period_str, str) and period_str:
                interval = period_str_to_interval(period_str)

        super().__init__(interval=interval, default_tz=default_tz, **new_kwargs)
        self['project_id'] = project_id
        self._default_variant_id = default_variant_id
        self._assembly_cache = {}

        binder = PvradarProjectBinder()
        if len(self.binders) > 2:
            self.binders.insert(2, binder)
        else:
            warnings.warn(
                'PvradarProject context has less than 2 binders, adding project binder to the end of the list',
                UserWarning,
            )
            self.binders.append(binder)

    def _make_cache_key(self, assembly_name: str, variant_id: str, **kwargs) -> str:
        non_empty = {k: v for k, v in kwargs.items() if v is not None}
        sorted_keys = sorted(non_empty.keys())
        result = ''
        if variant_id != '':
            result += f'{variant_id}/'
        result += assembly_name
        for key in sorted_keys:
            result += f'&{key}={non_empty[key]}'
        return result

    def _resolve_variant_id(self, variant_id: Optional[str]) -> str:
        return variant_id or self._default_variant_id or ''

    @property
    def project_id(self) -> str:
        return self['project_id']

    @property
    @override
    def default_tz(self):
        if self._default_tz is None:
            location = self.location
            self._default_tz = location.tz
        return self._default_tz

    @default_tz.setter
    def default_tz(self, value: Any):
        GeoLocatedModelContext.default_tz.fset(self, value)  # type: ignore

    def get_assembly(
        self,
        assembly_name: str,
        *,
        variant_id: Optional[str] = None,
        year_index: Optional[int] = None,
        step: Optional[int] = None,
    ):
        variant_id = self._resolve_variant_id(variant_id)
        kwargs = {
            'year_index': year_index,
            'step': step,
        }
        kwargs = _remove_none_values(kwargs)
        cache_key = self._make_cache_key(assembly_name, variant_id, **kwargs)
        if cache_key in self._assembly_cache:
            return self._assembly_cache[cache_key]
        assembly = self._fetch_assembly(assembly_name, variant_id, **kwargs)
        self._assembly_cache[cache_key] = assembly
        return assembly

    def _fetch_assembly(self, assembly_name: str, variant_id: str, **kwargs):
        dims = {}
        if 'year_index' in kwargs:
            dims['yearIndex'] = kwargs['year_index']
        if 'step' in kwargs:
            dims['step'] = kwargs['step']
        query = Query(project_id=self['project_id'], variant_id=variant_id, path=f'assemblies/{assembly_name}', params=dims)
        response = PvradarClient.instance().get_json(query)
        if 'meta' not in response:
            raise ValueError(f'Unexpected response: {response}')
        return response['meta']['result']

    @property
    def default_variant_id(self) -> str:
        if self._default_variant_id:
            return self._default_variant_id
        manifest = self.platform_project_manifest
        return _variant_id_map[manifest['projectGoal']]

    def get_assembly_subject(
        self,
        assembly_name: AssemblyName,
        *,
        variant_id: Optional[str] = None,
        year_index: Optional[int] = None,
        step: Optional[int] = None,
    ) -> Any:
        if not variant_id:
            variant_id = self.default_variant_id
        assembly: IAssembly = self.get_assembly(
            assembly_name,
            variant_id=variant_id,
            year_index=year_index,
            step=step,
        )
        subject = assembly['subject']
        if is_timed_vtable(subject):
            tz = self.location.tz
            df = timed_vtable_to_df(subject, set_tz=tz)
            return df
        elif is_vtable(subject):
            df = vtable_to_df(subject)
            df = maybe_extend_df_with_dates(df)
            return df
        else:
            return subject

    def _fetch_and_cache_subject(self, assembly_name: AssemblyName, property_name: str = '') -> Any:
        if property_name == '':
            property_name = 'platform_' + assembly_name.replace('-', '_')
        if property_name in self:
            return self[property_name]
        self[property_name] = self.get_assembly_subject(assembly_name)
        return self[property_name]

    @property
    def platform_project_manifest(self) -> IProjectManifest:
        return self['platform_project_manifest']

    @property
    def platform_technical_params_base(self) -> dict[str, Any]:
        return self._fetch_and_cache_subject('technical-params-base')

    @property
    def name(self) -> str:
        return self['project_id']

    @staticmethod
    def from_locator(locator: ModelContextLocator, **kwargs) -> PvradarSite:
        new_kwargs = kwargs.copy()
        if 'default_tz' in locator:
            new_kwargs['default_tz'] = locator['default_tz']
        if 'interval' in locator and locator['interval']:
            if isinstance(locator['interval'], str):
                new_kwargs['interval'] = period_str_to_interval(locator['interval'])
            else:
                raise ValueError(f'Unsupported interval type in locator: {locator.__class__.__name__}')
        if 'latitude' in locator or 'longitude' in locator:
            if 'latitude' not in locator or 'longitude' not in locator:
                raise ValueError('Either both or none of latitude and longitude must be provided')
            new_kwargs['location'] = PvradarLocation(
                latitude=locator['latitude'],
                longitude=locator['longitude'],
                tz=locator.get('default_tz'),
            )

        project_id = locator.get('project_id', None)
        if project_id is None:
            result = PvradarSite(**new_kwargs)

            if isinstance(locator.get('fixed_design_spec'), dict):
                result.design = make_fixed_design(**locator.get('fixed_design_spec', {}))
            elif isinstance(locator.get('tracker_design_spec'), dict):
                result.design = make_tracker_design(**locator.get('tracker_design_spec', {}))
        else:
            result = PvradarProject(project_id=project_id, **new_kwargs)

        return result

    @override
    def copy(self: SelfType) -> SelfType:
        c = self.__class__(
            project_id=self._resources['project_id'],
            platform_project_manifest=self._resources['platform_project_manifest'],
            location=self._resources['location'],
        )
        self._copy_self(c)
        return c

    @override
    @classmethod
    def as_tracker_array(cls, **kwargs):
        raise NotImplementedError('as_tracker_array() only works with PvradarSite')

    @override
    @classmethod
    def as_fixed_array(cls, **kwargs):
        raise NotImplementedError('as_fixed_array() only works with PvradarSite')
