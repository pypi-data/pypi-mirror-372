from typing import Optional
from httpx import Timeout

from ..common.settings import SdkSettings


def make_timeout_object(override_timeout: Optional[float] = None) -> Timeout:
    s = SdkSettings.instance()
    main_timeout = override_timeout if override_timeout is not None else s.httpx_timeout
    return Timeout(main_timeout, connect=s.httpx_connect_timeout)
