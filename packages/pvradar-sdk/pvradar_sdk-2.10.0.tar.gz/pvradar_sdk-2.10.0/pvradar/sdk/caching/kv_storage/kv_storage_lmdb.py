from pathlib import Path
from typing import Any, override

from .kv_storage_binary_adaptor import KVStorageBinaryAdaptor
from .kv_storage_with_expiration_adaptor import KVStorageWithExpirationAdaptor

_databases: dict[str, Any] = {}


class KVStorageLMDB(KVStorageBinaryAdaptor, KVStorageWithExpirationAdaptor):
    def __init__(
        self,
        *,
        path: str | Path,
        caching_lmdb_max_bytes: int = 1024 * 1024 * 1024,
        max_spare_txns: int = 126,
        caching_max_age: int = 12 * 60 * 60,  # 12 hours
    ) -> None:
        self.caching_max_age = caching_max_age

        # Should be an optional dependency; if the package is not present, raise an exception
        import lmdb  # pyright: ignore [reportMissingImports]

        self.lmdb = lmdb
        self.caching_lmdb_max_bytes = caching_lmdb_max_bytes

        super().__init__()
        self.path = Path(path)

        # for the same path, we should reuse the same lmdb instance,
        # otherwise there will be locking issues when accessing the same file from the same process.
        # Also having the same DB initialized in parallel with different size params makes no sense any way.
        # see https://stackoverflow.com/questions/56905502/lmdb-badrsloterror-mdb-txn-begin-mdb-bad-rslot-invalid-reuse-of-reader-lockta#comment121552645_61814345
        str_path = str(path)
        if str_path in _databases:
            self.db = _databases[str_path]
            return

        if not Path(path).exists():
            try:
                Path(path).mkdir(parents=True)
            except Exception as e:
                raise ValueError(f'Failed to create LMDB cache directory at "{path}": {e}')

        self.db = lmdb.open(str_path, map_size=caching_lmdb_max_bytes, max_spare_txns=max_spare_txns)
        _databases[str_path] = self.db

    def close_and_remove(self):
        self.db.close()
        del _databases[str(self.path)]

        def rm_tree(subject: Path):
            for child in subject.iterdir():
                if child.is_file():
                    child.unlink()
                else:
                    rm_tree(child)

        rm_tree(self.path)

    @override
    def remove(self, key: str) -> None:
        with self.db.begin(write=True) as txn:
            txn.delete(key.encode())

    @override
    def get_all_keys(self) -> list[str]:
        with self.db.begin() as txn:
            return [key.decode() for key, _ in txn.cursor()]

    @override
    def get_caching_max_age(self) -> int:
        return self.caching_max_age

    @override
    def key_exists(self, key: str) -> bool:
        with self.db.begin() as txn:
            return txn.get(key.encode()) is not None and super().key_exists(key)

    @override
    def save(self, key: str, value: bytes) -> None:
        # assume we have a space at least for this value
        remaining_slots = 1
        while remaining_slots > 0:
            try:
                with self.db.begin(write=True) as txn:
                    txn.put(key.encode(), value)
                break
            except self.lmdb.MapFullError as e:
                remaining_slots = self.clean_expired()
                if remaining_slots == 0:
                    raise ValueError(f'LMDB cache is full, limit: {self.caching_lmdb_max_bytes // 1024 // 1024} MB') from e

    @override
    def load(self, key: str) -> bytes | None:
        with self.db.begin() as txn:
            return txn.get(key.encode())
