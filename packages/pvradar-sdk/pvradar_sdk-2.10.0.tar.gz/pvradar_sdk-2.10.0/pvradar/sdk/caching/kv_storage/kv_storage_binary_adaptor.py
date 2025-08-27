import pickle
import zlib
from abc import ABC
from typing import override

from .kv_storage_adaptor import KVStorageAdaptor
from ...data_case.types import DataCase


class KVStorageBinaryAdaptor(KVStorageAdaptor, ABC):
    @override
    def pack(self, serialized: DataCase) -> bytes:
        return zlib.compress(pickle.dumps(serialized))

    @override
    def unpack(self, packed: bytes) -> DataCase:
        return pickle.loads(zlib.decompress(packed))
