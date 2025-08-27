import time
from abc import ABC, abstractmethod
from typing import override

from .kv_storage_adaptor import KVStorageAdaptor, NoDataAvailable
from ...data_case.types import DataCase

meta_prop = 'meta'
cache_expires_at_prop = 'cache_expires_at'


class KVStorageWithExpirationAdaptor(KVStorageAdaptor, ABC):
    def is_expired_and_removed(self, data_case: DataCase, key: str) -> bool:
        assert meta_prop in data_case
        expired = data_case[meta_prop][cache_expires_at_prop] < time.time()
        if expired:
            self.remove(key)
        return expired

    @override
    def key_exists(self, key: str) -> bool:
        packed = self.load(key)
        if packed is None:
            return False
        data_case = self.unpack(packed)
        return not self.is_expired_and_removed(data_case, key)

    @override
    def patch(self, serialized: DataCase) -> DataCase:
        assert meta_prop in serialized
        serialized[meta_prop][cache_expires_at_prop] = int(time.time()) + self.get_caching_max_age()
        return serialized

    @override
    def unpatch(self, patched: DataCase, key: str) -> DataCase | type[NoDataAvailable]:
        if self.is_expired_and_removed(patched, key):
            return NoDataAvailable
        return patched

    @abstractmethod
    def get_all_keys(self) -> list[str]: ...

    @abstractmethod
    def remove(self, key: str) -> None: ...

    @abstractmethod
    def get_caching_max_age(self) -> int: ...

    def clean_expired(self) -> int:
        removed_count = 0
        for key in self.get_all_keys():
            packed = self.load(key)
            if packed is None:
                continue
            data_case = self.unpack(packed)
            if data_case is not None and data_case != NoDataAvailable:
                removed_count += self.is_expired_and_removed(data_case, key)
        return removed_count

    @override
    def truncate(self):
        for key in self.get_all_keys():
            self.remove(key)
