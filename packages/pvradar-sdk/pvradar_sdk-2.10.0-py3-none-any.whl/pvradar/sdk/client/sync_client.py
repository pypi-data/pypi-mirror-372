import re
from abc import abstractmethod, ABC
from functools import cached_property
from typing import Any, override

import orjson
from httpx import Client, Response
from httpx._types import QueryParamTypes  # pyright: ignore [reportPrivateImportUsage]
from pandas import DataFrame

from .api_query import Query
from .client_utils import make_timeout_object
from ..common.constants import API_VERSION
from ..common.exceptions import ApiException, ClientException
from ..common.pandas_utils import api_csv_string_to_df
from ..common.settings import SdkSettings
from ..data_case.deserializer import data_case_to_any


class SyncClient(ABC):
    @abstractmethod
    def get_token(self) -> str:
        """Returns the token used for authentication."""
        raise NotImplementedError

    @abstractmethod
    def get_base_url(self) -> str:
        """Returns the base URL of the API."""
        raise NotImplementedError

    def __init__(self):
        self._session = None

    @override
    def __repr__(self) -> str:
        return f'<PvradarSyncClient url={self.get_base_url()}>'

    @cached_property
    def session(self) -> Client:
        s = SdkSettings.instance()
        timeout = make_timeout_object(override_timeout=300)  # 5 minutes
        session = Client(base_url=self.get_base_url(), timeout=timeout, verify=s.httpx_verify)
        session.headers.update({'Authorization': f'Bearer {self.get_token()}'})
        session.headers.update({'Accept-version': API_VERSION})
        return session

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

    def post(
        self,
        subpath: str,
        *,
        json: Any = None,
    ) -> Any:
        return self.session.post(url=subpath, json=json)

    def post_data_case(
        self,
        subpath: str,
        *,
        json: Any = None,
    ) -> Any:
        r = self.post(subpath, json=json)

        self.maybe_raise(r)
        json_data = orjson.loads(r.text)

        payload = json_data.get('data')
        if not payload:
            raise ClientException('post_data_case() expects "data" as key for successful response')
        result = data_case_to_any(payload)
        return result
