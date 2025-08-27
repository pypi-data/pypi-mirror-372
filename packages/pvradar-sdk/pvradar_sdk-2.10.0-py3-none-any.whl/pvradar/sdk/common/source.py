from dataclasses import dataclass
import orjson
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Optional, TypedDict, NotRequired, override

from ..measurements import default_confidentiality
from ..modeling.basics import Confidentiality

default_encoding = 'utf8'


@dataclass(kw_only=True)
class SourceManifest:
    id: str
    description: Optional[str] = None
    confidentiality: Confidentiality = default_confidentiality
    org_id: Optional[str] = None
    meta: Optional[dict[str, Any]] = None
    origin: Optional[str] = None
    update_date: Optional[str] = None
    size: Optional[int] = None


class ReadFileOpRecipe(TypedDict):
    op: str
    path: str | Path
    encoding: NotRequired[str]


class AbstractSource(ABC):
    @abstractmethod
    def get_file_contents(self, path: str | Path, encoding: Optional[str] = default_encoding) -> str: ...

    @abstractmethod
    def check_file_exists(self, path: str | Path) -> bool: ...

    @abstractmethod
    def get_dirname(self) -> str: ...

    @abstractmethod
    def list_files(self, path: str | Path) -> list[str]: ...

    def to_op(self) -> Callable:
        def read_file(op_recipe: dict[str, Any], value: Any = None) -> str:
            assert 'path' in op_recipe, 'path is required in op_recipe'
            return self.get_file_contents(op_recipe['path'], getattr(op_recipe, 'encoding', default_encoding))

        return read_file

    def get_source_manifest(self) -> SourceManifest | None:
        try:
            raw = self.get_file_contents('source.json')
        except Exception:
            # Absent manifest or network error
            raw = None
        try:
            if raw is not None:
                raw_dict = orjson.loads(raw)
                if 'id' not in raw_dict:
                    raw_dict['id'] = self.get_dirname()
                return SourceManifest(**raw_dict)
        except Exception:
            # Malformed manifest
            return None


class LocalSource(AbstractSource):
    def __init__(self, dir: str | Path) -> None:
        self.dir = Path(dir)
        self.dirname = self.dir.name

    def _get_full_path(self, path: str | Path) -> Path:
        return Path.joinpath(self.dir, path)

    @override
    def get_file_contents(self, path: str | Path, encoding: Optional[str] = default_encoding) -> str:
        with open(self._get_full_path(path), 'r', encoding=encoding) as f:
            return f.read()

    @override
    def check_file_exists(self, path: str | Path) -> bool:
        return self._get_full_path(path).exists()

    @override
    def get_dirname(self) -> str:
        return self.dirname

    @override
    def list_files(self, path: str | Path) -> list[str]:
        full_path = self._get_full_path(path)
        if not full_path.is_dir():
            raise ValueError(f'Path {full_path} is not a directory.')
        result = [file.relative_to(self.dir).as_posix() for file in full_path.glob('*') if file.is_file()]
        return sorted(result)

    @override
    def get_source_manifest(self) -> SourceManifest | None:
        result = super().get_source_manifest()
        if result is not None:
            result.origin = 'local:' + self.dir.as_posix()
        return result
