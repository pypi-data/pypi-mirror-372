from abc import ABC, abstractmethod
import orjson
from typing import Any

from ...data_case.serializer import any_to_data_case
from ...data_case.deserializer import data_case_to_any
from ...data_case.types import DataCase


class NoDataAvailable:
    pass


class KVStorageAdaptor(ABC):
    # series | df -> data_case -> patched_data_case -> bytes -> save -> load -> bytes -> patched_data_case -> data_case -> series | df
    # serialize -> patch -> pack -> save -...> load -> unpack -> unpatch -> deserialize
    @abstractmethod
    def key_exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def save(self, key: str, value: bytes) -> None:
        pass

    @abstractmethod
    def load(self, key: str) -> bytes | None:
        pass

    def serialize(self, value: Any) -> DataCase:
        return any_to_data_case(value)

    def deserialize(self, serialized: DataCase) -> Any:
        return data_case_to_any(serialized)

    def patch(self, serialized: DataCase) -> DataCase:
        return serialized

    def unpatch(self, patched: DataCase, key: str) -> DataCase | type[NoDataAvailable]:
        return patched

    def pack(self, serialized: DataCase) -> bytes:
        return orjson.dumps(serialized, option=orjson.OPT_INDENT_2)

    def unpack(self, packed: bytes) -> DataCase:
        return orjson.loads(packed)

    def serialize_and_save(self, key: str, value: Any) -> None:
        serialized = self.serialize(value)
        patched = self.patch(serialized)
        packed = self.pack(patched)
        self.save(key, packed)

    def load_and_deserialize(self, key: str) -> Any:
        packed = self.load(key)
        if packed is None:
            return NoDataAvailable
        patched = self.unpack(packed)
        original = self.unpatch(patched, key)
        if original is NoDataAvailable:
            return NoDataAvailable
        return self.deserialize(original)  # pyright: ignore [reportArgumentType]

    @abstractmethod
    def truncate(self):
        pass
