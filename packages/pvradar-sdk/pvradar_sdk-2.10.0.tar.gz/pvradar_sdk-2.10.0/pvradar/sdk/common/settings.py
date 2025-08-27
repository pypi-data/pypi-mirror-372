import warnings
import sys
from pathlib import Path
import tomllib
from typing import Any, Optional, Self
from platformdirs import user_config_path, user_data_path
from pydantic import BaseModel, Field

from ..common.exceptions import PvradarSdkException

_sdk_toml_instance = None


def _get_settings_dir_path() -> Path:
    return user_config_path('pvradar')


def _get_settings_file_path() -> Path:
    return _get_settings_dir_path() / 'sdk.toml'


def _get_default_verify() -> bool:
    try:
        import ssl
        import truststore

        result = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        return result
    except Exception:
        warnings.warn('Unable to load system trust store, using default SSL context.')
        return True


# the following class resembles the behavior of pydantic-settings
# but is more lightweight and does not require additional dependencies
class SdkSettings(BaseModel):
    dock_base_url: str = 'https://api.pvradar.com/v3'
    dock_token: str = ''
    outlet_base_url: str = 'https://api.pvradar.com/v2'
    outlet_token: str = ''
    platform_base_url: str = 'https://platform.pvradar.com/api'
    platform_username: str = ''
    platform_password: str = ''
    platform_token: str = ''
    caching_enabled: bool = True
    caching_kv_storage: str = 'lmdb'  # alternatives: 'memory', 'file', 'external'
    caching_lmdb_path: Optional[str] = None
    caching_lmdb_max_mbytes: Optional[int] = None
    caching_file_path: Optional[str] = None
    caching_max_age: int = 12 * 3600
    collect_api_metadata: bool = False
    default_flowchart_renderer: str = 'kroki_png'
    default_plot_renderer: str = 'plotly,matplotlib'
    httpx_timeout: float = 60.0
    httpx_connect_timeout: float = 10.0
    httpx_verify: Any = Field(default_factory=_get_default_verify)
    sources_path: Optional[str] = None

    @staticmethod
    def from_dict(d: dict) -> 'SdkSettings':
        d = d.copy()
        if 'token' in d:
            if 'outlet_token' not in d:
                d['outlet_token'] = d['token']
            if 'platform_token' not in d:
                d['platform_token'] = d['token']
            if 'dock_token' not in d:
                d['dock_token'] = d['token']
            del d['token']

        # reduce potential side-effects of running tests
        if 'pytest' not in sys.modules:
            if 'caching_lmdb_path' not in d:
                d['caching_lmdb_path'] = str((user_data_path('pvradar') / 'lmdb_cache').absolute())
            if 'caching_file_path' not in d:
                d['caching_file_path'] = str((user_data_path('pvradar') / 'file_cache').absolute())

        if 'base_url' in d:
            raise ValueError('base_url is not a valid key, did you mean outlet_base_url instead?')

        result = SdkSettings(**d)

        for key in d:
            if not hasattr(result, key):
                raise ValueError(f'Unknown key: {key}')

        return result

    @staticmethod
    def from_config_path(path: str | Path) -> 'SdkSettings':
        try:
            with Path(path).open('rb') as conf_file:
                values = tomllib.load(conf_file)

                # always disable caching while running tests and reading global settings
                if 'pytest' in sys.modules:
                    values['caching_enabled'] = False

                return SdkSettings.from_dict(values)
        except OSError:
            raise PvradarSdkException(
                f'CRITICAL: No config found, expected file: {path} . '
                + 'Please contact PVRADAR tech. support if unsure what it is.'
            )
        except tomllib.TOMLDecodeError as e:
            raise PvradarSdkException(
                f'CRITICAL: Invalid config format found in file: {path} .'
                + ' If unsure what it means, contact PVRADAR tech. support.'
            ) from e

    @classmethod
    def set_instance(cls, instance: None | Self) -> None | Self:
        global _sdk_toml_instance
        previous = _sdk_toml_instance
        _sdk_toml_instance = instance
        return previous  # pyright: ignore [reportReturnType]

    @staticmethod
    def instance() -> 'SdkSettings':
        global _sdk_toml_instance
        if _sdk_toml_instance is None:
            settings_path = _get_settings_file_path()
            _sdk_toml_instance = SdkSettings.from_config_path(settings_path)
        return _sdk_toml_instance
