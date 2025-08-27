from typing import Optional, Any, override

from .caching_key_maker_pvradar_site import CachingKeyMakerPvradarSite
from .caching_key_maker_pvradar_site import interval_to_key
from ... import ModelContext, PvradarProject
from ...modeling.basics import ModelParam


class CachingKeyMakerProject(CachingKeyMakerPvradarSite):
    @override
    def make_key(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> str | None:
        assert isinstance(context, PvradarProject)
        project_id = context.project_id
        if not project_id:
            raise ValueError('{self.__class__.__name__} requires project_id pre-defined in context')
        if 'interval' not in context:
            return None
        if as_param and as_param.attrs and 'resource_type' in as_param.attrs:
            key = interval_to_key(context) + '__' + project_id + '__' + as_param.attrs['resource_type']
            key += self.get_source_suffix(as_param=as_param, defaults=defaults)
            return key
        return None
