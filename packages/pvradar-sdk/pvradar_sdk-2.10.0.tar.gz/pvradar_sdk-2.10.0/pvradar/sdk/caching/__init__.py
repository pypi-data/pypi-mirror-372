from typing import Optional

from .caching_handler import CachingLibraryHandler
from .kv_storage.kv_storage_adaptor import KVStorageAdaptor

handler = CachingLibraryHandler()


def set_caching_external_kv_storage(kv_storage_override: Optional[KVStorageAdaptor] = None):
    """
    Will use default KVStorageAdaptor if kv_storage is None
    :param kv_storage_override:
    :return:
    """
    handler.external_kv_storage = kv_storage_override
