from typing import override
from ..modeling.base_model_context import BaseModelContext
from ..modeling.model_binder import FirstMatchingTypeBinder
from ..modeling.library_manager import BaseLibraryHandler, extract_models
from .pv_binder import PvBinder
from . import ac
from . import dc
from . import grid
from . import irradiance
from . import meteo
from . import market


class PvLibraryHandler(BaseLibraryHandler):
    @override
    def get_models(self):
        models = (
            extract_models(irradiance)
            + extract_models(ac)
            + extract_models(dc)
            + extract_models(grid)
            + extract_models(meteo)
            + extract_models(market)
        )
        return models

    @override
    def get_binders(self):
        return [
            PvBinder(),
            FirstMatchingTypeBinder(self.get_models(), name='pv'),
        ]

    @override
    def enrich_context(self, context: BaseModelContext) -> None:
        context.register_model(irradiance.pvlib_irradiance_perez_driesse, for_resource_type=True)
        super().enrich_context(context)


pv_handler = PvLibraryHandler()
