from pathlib import Path
from typing import Optional


from ..common.settings import SdkSettings
from ..common.exceptions import PvradarSdkException
from .kv_storage.kv_storage_lmdb import KVStorageLMDB
from .kv_storage.kv_storage_memory import KVStorageMemory
from .kv_storage.kv_storage_file import KVStorageFile
from .kv_storage.kv_storage_adaptor import KVStorageAdaptor
from .advisor.remote_only_advisor import RemoteOnlyAdvisor
from .advisor.caching_advisor import CachingAdvisor


def make_kv_storage_lmdb(settings: Optional[SdkSettings] = None) -> KVStorageLMDB:
    if not settings:
        settings = SdkSettings.instance()
    caching_lmdb_max_bytes = 1024 * 1024 * 1024  # 1GB
    if not settings.caching_lmdb_path:
        raise PvradarSdkException('caching_lmdb_path is required for KVStorageLMDB')
    path = settings.caching_lmdb_path
    if settings.caching_lmdb_max_mbytes:
        caching_lmdb_max_bytes = int(float(settings.caching_lmdb_max_mbytes) * 1024 * 1024)

    return KVStorageLMDB(
        path=path,
        caching_lmdb_max_bytes=caching_lmdb_max_bytes,
        caching_max_age=settings.caching_max_age,
    )


def make_kv_storage_file(settings: Optional[SdkSettings] = None) -> KVStorageFile:
    if not settings:
        settings = SdkSettings.instance()
    path = settings.caching_file_path
    if not path:
        raise ValueError('caching_file_path is required for KVStorageFile')
    return KVStorageFile(
        Path(path),
        caching_max_age=settings.caching_max_age,
    )


def make_kv_storage(settings: Optional[SdkSettings] = None) -> KVStorageAdaptor:
    if not settings:
        settings = SdkSettings.instance()
    storage = settings.caching_kv_storage
    if storage == 'lmdb':
        return make_kv_storage_lmdb(settings)
    elif storage == 'file':
        return make_kv_storage_file(settings)
    elif storage == 'memory':
        return KVStorageMemory()
    else:
        raise ValueError(f'Unknown caching_kv_storage: {storage}')


def make_caching_advisor(settings: Optional[SdkSettings] = None) -> CachingAdvisor:
    return RemoteOnlyAdvisor()
