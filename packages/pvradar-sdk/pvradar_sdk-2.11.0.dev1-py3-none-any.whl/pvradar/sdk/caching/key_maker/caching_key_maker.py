from abc import abstractmethod, ABC
from typing import Optional, Any

from ... import ModelContext
from ...modeling.basics import ModelParam


class CachingKeyMaker(ABC):
    @abstractmethod
    def make_key(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ) -> str | None:
        pass

    def __call__(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[ModelContext] = None,
    ):
        return self.make_key(resource_name=resource_name, as_param=as_param, defaults=defaults, context=context)
