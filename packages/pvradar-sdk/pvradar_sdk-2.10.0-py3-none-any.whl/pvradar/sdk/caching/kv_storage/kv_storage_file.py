import os
from hashlib import sha1
from pathlib import Path
from typing import override

from .kv_storage_with_expiration_adaptor import KVStorageWithExpirationAdaptor


class KVStorageFile(KVStorageWithExpirationAdaptor):
    """the main purpose of this is debugging. Use LMDB for proper local caching"""

    @override
    def get_all_keys(self) -> list[str]:
        return [f.name for f in os.scandir(self.path) if f.is_file() and f.name.endswith('.json')]

    @override
    def remove(self, key: str) -> None:
        file_path = self.get_file_path(key)
        if file_path.exists():
            file_path.unlink()

    def __init__(
        self,
        path: Path | str,
        caching_max_age: int = 12 * 60 * 60,  # 12 hours
    ):
        super().__init__()
        self.caching_max_age = caching_max_age
        path = Path(path)
        if not path.exists():
            try:
                path.mkdir(parents=True)
            except Exception as e:
                raise ValueError(f'Failed to create LMDB cache directory at "{path}": {e}')

        self.path = path

    def get_file_path(self, key: str) -> Path:
        return self.path / f'{sha1(key.encode()).hexdigest()}.json'

    @override
    def key_exists(self, key: str) -> bool:
        return self.get_file_path(key).exists() and super().key_exists(key)

    @override
    def save(self, key: str, value: bytes) -> None:
        self.get_file_path(key).write_bytes(value)

    @override
    def load(self, key: str) -> bytes | None:
        return self.get_file_path(key).read_bytes() if self.key_exists(key) else None

    @override
    def get_caching_max_age(self) -> int:
        return self.caching_max_age
