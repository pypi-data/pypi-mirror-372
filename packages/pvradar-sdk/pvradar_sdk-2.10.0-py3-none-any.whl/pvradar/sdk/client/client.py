import re
import tomllib
from typing import Any, Self, override
from pandas import DataFrame
from httpx import Response
from httpx._types import QueryParamTypes  # pyright: ignore [reportPrivateImportUsage]
import pandas as pd
import warnings

from .dock.dock_sync_client import DockSyncClient
from ..common.exceptions import PvradarSdkError, ApiError
from ..common.settings import SdkSettings, _get_settings_dir_path, _get_settings_file_path
from ..common.pandas_utils import crop_by_interval
from .outlet.outlet_sync_client import OutletSyncClient
from .platform.platform_sync_client import PlatformSyncClient, _await
from .engine.engine_types import ModelRunResourceLink, ModelRunResponse

from .api_query import Query, ProviderType

_client_instance = None


class PvradarClient:
    def __init__(
        self,
        settings: SdkSettings,
    ):
        self.settings = settings
        self._outlet_client = None
        self._platform_client = None

    @override
    def __repr__(self) -> str:
        return (
            f'<PvradarClient'
            f' dock={self.settings.dock_base_url}'
            f' outlet={self.settings.outlet_base_url}'
            f' platform={self.settings.platform_base_url}>'
        )

    def _guess_provider(self, query: Query | str) -> ProviderType:
        # TODO: Maybe add `dock` provider here
        path = query
        if isinstance(query, Query):
            if query.provider:
                return query.provider
            if query.project_id:
                return 'platform'
            path = query.path
        if 'assemblies' in path:
            return 'platform'
        return 'outlet'

    @classmethod
    def _make_outlet_client(cls, settings: SdkSettings) -> OutletSyncClient:
        return OutletSyncClient(
            token=settings.outlet_token,
            base_url=settings.outlet_base_url,
        )

    def _get_outlet_client(self) -> OutletSyncClient:
        if isinstance(self._outlet_client, OutletSyncClient):
            return self._outlet_client
        c = self._make_outlet_client(self.settings)
        self._outlet_client = c
        return c

    @classmethod
    def _make_platform_client(cls, settings: SdkSettings) -> PlatformSyncClient:
        return PlatformSyncClient(
            base_url=settings.platform_base_url,
            username=settings.platform_username,
            password=settings.platform_password,
            token=settings.platform_token,
        )

    def _get_platform_client(self) -> PlatformSyncClient:
        if isinstance(self._platform_client, PlatformSyncClient):
            return self._platform_client
        c = self._make_platform_client(self.settings)
        self._platform_client = c
        return c

    def _subclient(self, query: Query | str) -> OutletSyncClient | DockSyncClient | PlatformSyncClient:
        provider = self._guess_provider(query)
        if provider == 'outlet':
            return self._get_outlet_client()
        elif provider == 'dock':
            return DockSyncClient()
        else:
            return self._get_platform_client()

    def get(self, query: str | Query, params: QueryParamTypes | None = None) -> Response:
        return self._subclient(query).get(query, params)

    def get_csv(self, query: str | Query, params: QueryParamTypes | None = None) -> str:
        return self._subclient(query).get_csv(query=query, params=params)

    def get_json(self, query: str | Query, params: QueryParamTypes | None = None) -> Any:
        return self._subclient(query).get_json(query=query, params=params)

    def get_df(
        self,
        query: str | Query,
        *,
        params: QueryParamTypes | None = None,
        crop_interval: pd.Interval | None = None,
    ) -> DataFrame:
        result = self._subclient(query).get_df(query=query, params=params)
        if crop_interval:
            result = crop_by_interval(result, crop_interval)
        return result

    def get_data_case(
        self,
        query: str | Query,
        *,
        params: QueryParamTypes | None = None,
        crop_interval: pd.Interval | None = None,
    ) -> Any:
        result = self._subclient(query).get_data_case(query=query, params=params)
        if crop_interval:
            result = crop_by_interval(result, crop_interval)
        return result

    def execute_model_run(self, link: ModelRunResourceLink) -> ModelRunResponse:
        c = self._get_platform_client()._get_async_httpx()
        coroutine = c.post(url='engine/model-runs', json=link)
        result = _await(coroutine)
        data = result.json()
        return data

    @classmethod
    def from_config(cls, config_path_str='') -> Self:
        warnings.warn('from_config() is deprecated. Use instance() or PvradarClient(settings)', DeprecationWarning)
        return cls(SdkSettings.instance())

    @classmethod
    def instance(cls) -> Self:
        global _client_instance
        if not _client_instance:
            _client_instance = cls(SdkSettings.instance())
        return _client_instance

    @classmethod
    def set_api_key(
        cls,
        api_key: str,
        disable_httpx_verify=False,
    ) -> None:
        api_key = str(api_key).strip()
        if not api_key:
            raise PvradarSdkError('API key cannot be empty.')

        if len(api_key) < 16:
            raise PvradarSdkError('API key too short. Are you sure you copied it correctly?')

        if not re.match(r'^[a-zA-Z0-9_.-]{16,}$', api_key):
            raise PvradarSdkError(f'Invalid API key format "{api_key}". Please copy-paste it without any extra characters.')

        current_contents = ''
        file_path = _get_settings_file_path()

        if file_path.exists():
            with file_path.open('r') as f:
                current_contents = f.read()

        if re.findall(r'^\s*(platform_|outlet_)token\s*=', current_contents, re.MULTILINE):
            raise PvradarSdkError(f'API key is already set for individual services. Please edit manually in "{file_path}"')

        if re.findall(r'^\s*token\s*=', current_contents, re.MULTILINE):
            current_contents = re.sub(r'^[ \t]*token\s*=.*$', f"token='{api_key}'", current_contents, flags=re.MULTILINE)
        else:
            current_contents += f"\ntoken='{api_key}'\n"

        if disable_httpx_verify:
            current_contents = re.sub(r'^[ \t]*httpx_verify\s*=.*$', '', current_contents, flags=re.MULTILINE)
            current_contents += '\nhttpx_verify=false\n'

        # remove extra newlines (or newlines with spaces)
        current_contents = re.sub(r'\n\s*\n+', '\n\n', current_contents)

        print('validating... ', end='')

        values = tomllib.loads(current_contents)
        new_settings = SdkSettings.from_dict(values)
        SdkSettings.set_instance(new_settings)
        outlet_client = cls._make_outlet_client(new_settings)
        try:
            summary = outlet_client.get_json('util/summary')
        except ApiError as e:
            print('failed')
            raise PvradarSdkError(str(e)) from e

        if not isinstance(summary, dict):
            raise PvradarSdkError('unexpected response')
        print('OK, server version: ' + summary.get('api_version', ''))

        dir_path = _get_settings_dir_path()
        dir_path.mkdir(parents=True, exist_ok=True)

        with file_path.open('w') as f:
            f.write(current_contents)
