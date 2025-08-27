from abc import abstractmethod, ABC
from typing import Optional, Any

from ...modeling.base_model_context import BaseModelContext
from ...modeling.basics import ModelParam
from ...modeling.model_wrapper import ModelWrapper


class CachingAdvisor(ABC):
    @abstractmethod
    def should_save(
        self,
        *,
        model_wrapper: ModelWrapper,
        result: Any,
        context: Optional[BaseModelContext] = None,
    ) -> bool:
        pass

    @abstractmethod
    def should_lookup(
        self,
        *,
        resource_name: str,
        as_param: Optional[ModelParam] = None,
        defaults: Optional[dict[str, Any]] = None,
        context: Optional[BaseModelContext] = None,
    ) -> bool:
        pass
