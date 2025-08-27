import orjson
from typing import Any, Optional, Self
from authlib.integrations.base_client import OAuthError
from authlib.integrations.httpx_client import AsyncOAuth2Client
from pandas import DataFrame
import httpx
from httpx._types import QueryParamTypes  # pyright: ignore [reportPrivateImportUsage]
from httpx import AsyncClient, Response
import asyncio
import nest_asyncio

from ...common.settings import SdkSettings
from ..client_utils import make_timeout_object
from .jsonapi_utils import jsonapi_to_object
from ..api_query import Query

_client_instances: dict[str, Any] = {}


def _await(coroutine: Any) -> Any:
    global _loop
    _loop = asyncio.get_event_loop()
    return _loop.run_until_complete(coroutine)


class PlatformSyncClient:
    def __init__(
        self,
        base_url: str = '',
        username: str = '',
        password: str = '',
        token: str = '',
        default_project_id: Optional[str] = None,
        default_variant_id: Optional[str] = None,
    ) -> None:
        self._base_url = base_url
        self._username = username
        self._password = password
        self._token = token
        self._default_project_id = default_project_id
        self._default_variant_id = default_variant_id

        self._authed_client: Optional[AsyncOAuth2Client] = None
        self._client_with_token: Optional[AsyncClient] = None

    @classmethod
    def instance(
        cls,
        base_url: str = '',
        username: str = '',
        password: str = '',
        token: str = '',
    ) -> Self:
        id = f'{base_url}'
        global _client_instances
        _client_instance = _client_instances.get(id)
        if not _client_instance:
            if not base_url:
                raise ValueError('instance() requires a non-empty base_url')
            else:
                _client_instance = cls(base_url=base_url, username=username, password=password, token=token)
            _client_instances[id] = _client_instance
        return _client_instance

    def _get_authed(self) -> AsyncOAuth2Client:
        nest_asyncio.apply()
        if self._authed_client:
            return self._authed_client
        keycloak_config = httpx.get(self._base_url + '/pvwave-util/keycloak-config').json()
        openid_configuration = httpx.get(keycloak_config['openid-configuration']).json()
        s = SdkSettings.instance()
        self._authed_client = AsyncOAuth2Client(
            client_id='platform',
            token_endpoint=openid_configuration['token_endpoint'],
            timeout=make_timeout_object(),
            base_url=self._base_url,
            verify=s.httpx_verify,
        )

        scope = 'openid email profile'
        endpoint = openid_configuration['token_endpoint']
        coroutine = self._authed_client.fetch_token(endpoint, username=self._username, password=self._password, scope=scope)
        _await(coroutine)
        return self._authed_client

    def _get__client_with_token(self) -> AsyncClient:
        s = SdkSettings.instance()
        nest_asyncio.apply()
        if not self._client_with_token:
            self._client_with_token = httpx.AsyncClient(
                base_url=self._base_url,
                headers={
                    'Authorization': f'Bearer {self._token}',
                },
                timeout=make_timeout_object(),
                verify=s.httpx_verify,
            )
        return self._client_with_token

    def _auto_correct_path(self, path: str, project_id: Optional[str] = None, variant_id: Optional[str] = None) -> str:
        if path.startswith('/'):
            return path
        prefix = '/'
        if project_id is not None:
            prefix += f'projects/{project_id}/'
        if variant_id is not None:
            prefix += f'variants/{variant_id}/'
        return f'{prefix}{path}'

    def _get_async_httpx(self) -> AsyncClient:
        if self._token:
            client = self._get__client_with_token()
        else:
            client = self._get_authed()
        return client

    def get(self, query: str | Query, params: QueryParamTypes | None = None, retry: int = 1) -> Response:
        client = self._get_async_httpx()

        if isinstance(query, str):
            url = self._auto_correct_path(query, project_id=self._default_project_id, variant_id=self._default_variant_id)
            coroutine = client.get(url=url, params=params)
        else:
            url = self._auto_correct_path(
                query.path,
                project_id=query.project_id or self._default_project_id,
                variant_id=query.variant_id or self._default_variant_id,
            )
            coroutine = client.get(url=url, params=query.make_query_params())

        try:
            return _await(coroutine)
        except OAuthError as e:
            if retry > 0:
                # probably something happened to token, e.g. expired,
                # so we need to re-authenticate and retry
                # FIXME: add logging of these events here
                self._authed_client = None
                return self.get(query, params, retry - 1)
            else:
                raise e

    def get_csv(self, query: str | Query, params: QueryParamTypes | None = None) -> str: ...

    def get_json(self, query: str | Query, params: QueryParamTypes | None = None) -> Any:
        return orjson.loads(self.get(query, params).text)

    def get_data_case(self, query: str | Query, params: QueryParamTypes | None = None) -> Any:
        raise NotImplementedError('get_data_case is not implemented in OutletSyncClient')

    def get_jsonapi_dict(self, query: str | Query, params: QueryParamTypes | None = None) -> dict[str, Any]:
        raw = self.get_json(query, params)
        if not raw:
            raise ValueError('empty response')
        processed = jsonapi_to_object(raw, 'id')
        return processed

    def get_df(
        self,
        query: str | Query,
        params: QueryParamTypes | None = None,
    ) -> DataFrame: ...
