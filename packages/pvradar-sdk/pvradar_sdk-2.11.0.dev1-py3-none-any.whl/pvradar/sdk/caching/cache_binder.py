from typing import Optional, Any, override

from .advisor.caching_advisor import CachingAdvisor
from .key_maker.caching_key_maker import CachingKeyMaker
from .kv_storage.kv_storage_adaptor import KVStorageAdaptor, NoDataAvailable
from .. import ModelContext
from ..modeling.basics import ModelParam, BindingNotFound
from ..modeling.model_binder import AbstractBinder
from ..modeling.model_wrapper import ModelBinding, ModelWrapper


class CacheBinder(AbstractBinder):
    def __init__(self, key_maker: CachingKeyMaker, kv_storage: KVStorageAdaptor, advisor: CachingAdvisor):
        self.key_maker = key_maker
        self.kv_storage = kv_storage
        self.storage_model_wrapper = ModelWrapper(self.read_cached_resource)
        self.advisor = advisor

    def read_cached_resource(self, key: str) -> Any:
        result = self.kv_storage.load_and_deserialize(key)

        # KV storage may return this due to cache eviction
        # while the difference is important inside of caching itself,
        # when the result is returned to the user, it should be None
        if result is NoDataAvailable:
            result = None

        return result

    @override
    def bind(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> type[BindingNotFound] | ModelBinding:
        if not self.advisor.should_lookup(resource_name=resource_name, as_param=as_param, defaults=defaults, context=context):
            return BindingNotFound
        key = self.key_maker.make_key(resource_name=resource_name, as_param=as_param, defaults=defaults, context=context)
        if not key:
            return BindingNotFound
        if self.kv_storage.key_exists(key):
            return ModelBinding(self.storage_model_wrapper, defaults={'key': key})
        return BindingNotFound
