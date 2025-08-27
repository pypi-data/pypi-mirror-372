import sys
from typing import override

from .kv_storage.kv_storage_adaptor import KVStorageAdaptor
from ..modeling.base_model_context import BaseModelContext
from ..modeling.library_manager import BaseLibraryHandler
from ..common.settings import SdkSettings
from .key_maker.caching_key_maker_pvradar_site import CachingKeyMakerPvradarSite
from .cache_binder import CacheBinder
from .caching_output_filter import CachingOutputFilter
from .caching_factory import make_kv_storage, make_caching_advisor


class CachingLibraryHandler(BaseLibraryHandler):
    external_kv_storage: KVStorageAdaptor | None = None

    @override
    def enrich_context(self, context: BaseModelContext) -> None:
        if 'pytest' in sys.modules:
            return

        settings = SdkSettings.instance()
        if not settings.caching_enabled:
            return

        key_maker = CachingKeyMakerPvradarSite()
        advisor = make_caching_advisor(settings)
        kv_storage = self.external_kv_storage or make_kv_storage(settings)

        binder = CacheBinder(
            key_maker=key_maker,
            kv_storage=kv_storage,
            advisor=advisor,
        )
        output_filter = CachingOutputFilter(
            key_maker=key_maker,
            kv_storage=kv_storage,
            advisor=advisor,
            context=context,
        )
        context.binders.insert(0, binder)
        context.output_filters.append(output_filter)
