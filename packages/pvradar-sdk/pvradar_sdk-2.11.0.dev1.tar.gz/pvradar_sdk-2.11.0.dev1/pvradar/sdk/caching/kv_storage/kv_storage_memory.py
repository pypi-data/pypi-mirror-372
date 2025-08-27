from typing import override
from .kv_storage_adaptor import KVStorageAdaptor


class KVStorageMemory(KVStorageAdaptor):
    def __init__(self, max_key_count: int = 100):
        self.max_key_count = max_key_count
        self.truncate()

    @override
    def key_exists(self, key: str) -> bool:
        return key in self.storage

    @override
    def save(self, key: str, value: bytes) -> None:
        exists = self.key_exists(key)
        self.storage[key] = value
        if not exists:
            self.fifo.append(key)
        if len(self.fifo) > self.max_key_count:
            del self.storage[self.fifo.pop(0)]

    @override
    def load(self, key: str) -> bytes | None:
        return self.storage.get(key)

    @override
    def truncate(self):
        self.storage = {}
        self.fifo = []
