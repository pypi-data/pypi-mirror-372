from typing import override

from ..sync_client import SyncClient
from ...common.settings import SdkSettings
from ...common.singleton import Singleton


class DockSyncClient(SyncClient, Singleton):
    @override
    def get_token(self) -> str:
        return SdkSettings.instance().dock_token

    @override
    def get_base_url(self) -> str:
        return SdkSettings.instance().dock_base_url
