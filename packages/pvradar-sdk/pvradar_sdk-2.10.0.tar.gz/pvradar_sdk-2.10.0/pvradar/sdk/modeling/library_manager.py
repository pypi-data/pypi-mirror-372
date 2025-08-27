import inspect
import pkgutil
import importlib
from typing import Any, Callable


from .model_context import ModelContext, known_model_binder
from .model_wrapper import ModelWrapper
from .base_model_context import BaseModelContext
from .hooks import hook_binder

_builtin_libraries = [
    'pvradar.sdk.client',
    'pvradar.sdk.pv',
    'pvradar.sdk.caching',
]


class BaseLibraryHandler:
    def get_models(self) -> list[ModelWrapper]:
        return []

    def get_binders(self) -> list[Callable]:
        return []

    def enrich_context(self, context: BaseModelContext) -> None:
        for model in self.get_models():
            context.register_model(model)
        for binder in self.get_binders():
            context.binders.append(binder)


handlers: list[BaseLibraryHandler] = []
_loaded = False


def extract_models(module_instance: Any) -> list[ModelWrapper]:
    result: list[ModelWrapper] = []
    members = inspect.getmembers(module_instance)
    for name, obj in members:
        if inspect.isfunction(obj) and hasattr(obj, 'resource_type'):
            result.append(ModelWrapper.wrap(obj))
    return result


def load_libraries() -> list[BaseLibraryHandler]:
    global _loaded, handlers
    if _loaded:
        return handlers

    module_names = _builtin_libraries.copy()

    try:
        import pvradar.library  # type: ignore

        module_infos = pkgutil.iter_modules(pvradar.library.__path__, 'pvradar.library.')  # pyright: ignore [reportAttributeAccessIssue]
        for module_info in module_infos:
            module_names.append(module_info.name)
    except ModuleNotFoundError:
        # no action, it's OK if there are no additional libraries were installed
        pass

    for module_name in module_names:
        module = importlib.import_module(module_name)

        if hasattr(module, 'handler'):
            handler = getattr(module, 'handler')
            assert isinstance(handler, BaseLibraryHandler)
            handlers.append(handler)
        else:
            raise ValueError(f'Library {module_name} does not have a default handler')

    _loaded = True
    return handlers


def enrich_context_from_libraries(context: ModelContext) -> None:
    for handler in load_libraries():
        handler.enrich_context(context)

    # move known_model_binder binder to the end of the list
    # to ensure that it is called last
    if known_model_binder in context.binders:
        context.binders.remove(known_model_binder)
        context.binders.append(known_model_binder)

    # move hook_binder to the start of the list
    # to ensure that it is called first
    if hook_binder in context.binders:
        context.binders.remove(hook_binder)
        context.binders.insert(0, hook_binder)
