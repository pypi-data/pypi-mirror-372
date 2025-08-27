from typing import Any, Callable, Mapping, Iterator, Optional, override
from abc import ABC, abstractmethod
from .model_wrapper import ModelWrapper


class Hook:
    pass


class BaseModelContext(ABC, Mapping):
    @abstractmethod
    def __setitem__(self, key, value): ...

    @abstractmethod
    @override
    def __getitem__(self, key): ...

    @abstractmethod
    def __delitem__(self, key): ...

    @override
    @abstractmethod
    def __contains__(self, key) -> bool: ...

    @override
    @abstractmethod
    def __iter__(self) -> Iterator[Any]: ...

    @override
    @abstractmethod
    def __len__(self) -> int: ...

    @abstractmethod
    def run(self, model: Callable | str, label: Optional[str] = None, _depth: int = 0, **kwargs): ...

    @abstractmethod
    def resource(self, name: Any, *, attrs: Mapping[str, Any] = {}, **kwargs) -> Any: ...

    @abstractmethod
    def register_model(
        self,
        model: Callable,
        *,
        defaults: Optional[dict[str, Any]] = None,
        for_resource_type: Optional[str | bool] = None,
    ) -> ModelWrapper: ...

    def __init__(self):
        self.binders: list[Callable] = []
        self.output_filters: list[Callable] = []
        self.models: dict = {}
        self.registered_hooks: list[Hook] = []

    def wrap_model(self, model: Callable | str) -> ModelWrapper: ...

    def with_dependencies(self, resource: Any, dependencies: Any) -> Any: ...
