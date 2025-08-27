from typing import override
from ..modeling.base_model_context import BaseModelContext
from ..modeling.library_manager import BaseLibraryHandler, extract_models
from .client_binder import PvradarClientBinder, pvradar_client_models
from .platform import platform_models


class ClientLibraryHandler(BaseLibraryHandler):
    @override
    def get_models(self):
        pure_client_models = list(pvradar_client_models.values())
        platform_model_functions = extract_models(platform_models)
        result = pure_client_models + platform_model_functions
        return result

    @override
    def enrich_context(self, context: BaseModelContext) -> None:
        super().enrich_context(context)
        context.binders.append(PvradarClientBinder())


pvgis_handler = ClientLibraryHandler()
