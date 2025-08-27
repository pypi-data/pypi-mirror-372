from typing import Any, Mapping, Optional, override

from ..modeling.library_manager import extract_models
from ..modeling.model_wrapper import ModelBinding, ModelWrapper
from ..modeling.model_context import ModelContext
from ..modeling.model_binder import AbstractBinder
from ..client.pvradar_resources import check_is_pvradar_resource_type
from ..modeling.basics import BaseResourceAttrs, BindingNotFound, ModelParam
from ..modeling.resource_types._list import default_datasources

from .models import merra2_models
from .models import era5_models
from .models import noaa_models
from .pvgis import pvgis_models
from .models import aemet_grid_models
from .models import inmet_models


pvradar_client_models: dict[str, ModelWrapper] = dict()


def _import_models(module_instance: Any):
    wrappers = extract_models(module_instance)
    for wrapper in wrappers:
        pvradar_client_models[wrapper.name] = wrapper


_import_models(merra2_models)
_import_models(era5_models)
_import_models(noaa_models)
_import_models(pvgis_models)
_import_models(aemet_grid_models)
_import_models(inmet_models)


class PvradarClientBinder(AbstractBinder):
    @override
    def __call__(self, *args, **kwargs):
        return self.bind(*args, **kwargs)

    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> Any:
        name = resource_name
        defaults = defaults or {}

        attrs: Mapping = {}

        datasource: Optional[str] = None

        if as_param and as_param.attrs is not None:
            attrs = as_param.attrs
            if 'resource_type' in attrs:
                name = attrs['resource_type']
            if 'datasource' in attrs:
                datasource = attrs['datasource']
            elif 'params' in attrs and 'dataset' in attrs['params'] and '-' in attrs['params']['dataset']:
                chunks = attrs['params']['dataset'].split('-')
                datasource = chunks[0]

        if not check_is_pvradar_resource_type(name):
            return BindingNotFound

        def make_binding(model: ModelWrapper):
            extended_defaults = defaults.copy()
            base_attrs = BaseResourceAttrs.__optional_keys__
            for k in attrs:
                if k not in base_attrs:
                    extended_defaults[k] = attrs[k]
            return ModelBinding(model=model, defaults=extended_defaults)

        # if a specific datasource is requested, we will only return a model that has that datasource
        if datasource:
            for obj in pvradar_client_models.values():
                if name == getattr(obj, 'resource_type'):
                    if datasource == obj.datasource:
                        return make_binding(obj)
            return BindingNotFound

        # otherwise prefer the default datasource as defined in Resource DB
        else:
            prefer_datasource = default_datasources.get(name)
            candidate = None

            for obj in pvradar_client_models.values():
                if name == getattr(obj, 'resource_type'):
                    if obj.datasource == prefer_datasource:
                        return make_binding(obj)
                    else:
                        candidate = make_binding(obj)

            if candidate:
                return candidate

        return BindingNotFound
