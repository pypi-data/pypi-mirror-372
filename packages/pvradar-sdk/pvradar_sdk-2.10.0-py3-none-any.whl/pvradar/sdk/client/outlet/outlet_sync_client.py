import re
from typing import Any, Self, override
import warnings
import orjson
from pandas import DataFrame
from httpx import Client, Response
from httpx._types import QueryParamTypes  # pyright: ignore [reportPrivateImportUsage]

from ..client_utils import make_timeout_object
from ...common.settings import SdkSettings
from ...common.constants import API_VERSION, SDK_VERSION
from ...common.pandas_utils import api_csv_string_to_df
from ...common.exceptions import ApiException, ClientException, PvradarSdkException
from ..api_query import Query
from ...data_case.deserializer import data_case_to_any

default_url = 'https://api.pvradar.com/v2'
_client_instances: dict[str, Any] = {}


class OutletSyncClient:
    _token: str
    _base_url: str
    _session: Client | None

    def __init__(
        self,
        token: str = 'pvradar_public',
        base_url: str = default_url,
    ):
        self._token = token
        self._base_url = base_url
        self._session = None

    @override
    def __repr__(self) -> str:
        return f'<PvradarSyncClient url={self._base_url}>'

    def make_session(self) -> Client:
        s = SdkSettings.instance()
        timeout = make_timeout_object()
        session = Client(base_url=self._base_url, timeout=timeout, verify=s.httpx_verify)
        session.headers.update({'Authorization': f'Bearer {self._token}'})
        session.headers.update({'Accept-version': API_VERSION})
        session.headers.update({'X-PVRADAR-SDK-Version': SDK_VERSION})
        return session

    @property
    def session(self) -> Client:
        if not self._session:
            self._session = self.make_session()
        return self._session

    def get(self, query: str | Query, params: QueryParamTypes | None = None) -> Response:
        if isinstance(query, str):
            return self.session.get(url=query, params=params)
        return self.session.get(url=query.path, params=query.make_query_params())

    def maybe_raise(self, r: Response):
        if r.status_code >= 400:
            raise ApiException(r.status_code, r.text, r)

    def get_csv(self, query: str | Query, params: QueryParamTypes | None = None) -> str:
        r = self.get(query=query, params=params)
        self.maybe_raise(r)
        return r.text

    def get_json(self, query: str | Query, params: QueryParamTypes | None = None) -> dict[str, Any]:
        r = self.get(query=query, params=params)
        self.maybe_raise(r)
        return orjson.loads(r.text)

    def get_data_case(self, query: str | Query, params: QueryParamTypes | None = None) -> Any:
        json_data = self.get_json(query, params)
        payload = json_data.get('data')
        if not payload:
            raise ClientException('get_data_case() expects "data" as key for successful response')
        result = data_case_to_any(payload)
        return result

    def get_df(
        self,
        query: str | Query,
        params: QueryParamTypes | None = None,
    ) -> DataFrame:
        r = self.get(query=query, params=params)
        self.maybe_raise(r)
        pure_type = re.sub(r';.*$', '', r.headers['content-type']).strip()
        if pure_type in ['text/csv', 'application/csv']:
            df = api_csv_string_to_df(r.text, query.tz if isinstance(query, Query) else None)
            settings = SdkSettings.instance()
            if settings.collect_api_metadata:
                df.attrs['api_call'] = {
                    'query': query.as_dict() if isinstance(query, Query) else query,
                    'params': params,
                    'url': str(r.url),
                }
            return df
        raise ClientException(f'unexpected content type: {pure_type}', r)

    @classmethod
    def from_config(cls, config_path_str='') -> Self:
        if config_path_str:
            raise PvradarSdkException('from_config() is deprecated and config_path_str is no longer supported')
        warnings.warn('from_config() is deprecated. Use instance() or OutletSyncClient(...)', DeprecationWarning)
        settings = SdkSettings.instance()
        return cls(
            token=settings.outlet_token,
            base_url=settings.outlet_base_url,
        )

    @classmethod
    def instance(cls, base_url: str = '', **kwargs) -> Self:
        if base_url:
            raise PvradarSdkException('instance(base_url) is is no longer supported, please use without parameters')
        settings = SdkSettings.instance()
        id = str(settings.outlet_base_url)
        global _client_instances
        _client_instance = _client_instances.get(id)
        if not _client_instance:
            _client_instance = cls(base_url=base_url, token=settings.outlet_token)
            _client_instances[id] = _client_instance
        return _client_instance
