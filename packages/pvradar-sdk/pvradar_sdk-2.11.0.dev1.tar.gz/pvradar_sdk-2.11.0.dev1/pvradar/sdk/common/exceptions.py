from typing import Optional, Union
from httpx import Response
import pandas as pd


class ApiError(Exception):
    status_code: int
    response: Union[(Response, None)]

    def __init__(self, status_code: int, message: str, response: Union[(Response, None)] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ApiException(ApiError):
    """deprecated, use ApiError instead"""

    pass


class ClientError(Exception):
    response: Union[(Response, None)]

    def __init__(self, message: str, response: Union[(Response, None)] = None):
        super().__init__(message)
        self.response = response


class ClientException(ClientError):
    """deprecated, use ClientError instead"""

    pass


class PvradarSdkError(RuntimeError):
    pass


class PvradarSdkException(PvradarSdkError):
    """deprecated, use PvradarSdkError instead"""

    pass


class DataUnavailableError(PvradarSdkException):
    def __init__(self, message: str = '', interval: Optional[pd.Interval] = None, where='', *args):
        self.interval = interval
        self.where = where

        if message == '':
            message = 'Data is unavailable'
            if where:
                message += f' in {where}'
            if interval is not None:
                interval_str = f'{interval.left.strftime("%Y-%m-%d")}..{interval.right.strftime("%Y-%m-%d")}'
                message += f' for interval {interval_str}'
        super().__init__(message, *args)
