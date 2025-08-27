# See PVGIS API documentation:
# https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/getting-started-pvgis/api-non-interactive-service_en

import re
from typing import Mapping, NotRequired, TypedDict, Literal, Self
import httpx
import pandas as pd

from ..client_utils import make_timeout_object
from ...common.pandas_utils import api_csv_string_to_df
from ...common.settings import SdkSettings


PvgisDatabase = Literal['pvgis-sarah3', 'pvgis-era5']


class PvgisSeriescalcParams(TypedDict):
    lon: float
    lat: float
    usehorizon: NotRequired[int]
    userhorizon: NotRequired[str]
    raddatabase: NotRequired[Literal['PVGIS-SARAH3', 'PVGIS-ERA5']]
    startyear: NotRequired[int]
    endyear: NotRequired[int]
    angle: NotRequired[float]  # Inclination angle from horizontal plane of the (fixed) PV system.
    aspect: NotRequired[float]  # Orientation (azimuth) angle of the (fixed) PV system, 0=south, 90=west, -90=east


_client_instance = None


class PvgisClient:
    def __init__(self):
        self.base_url = 'https://re.jrc.ec.europa.eu/api'

    def _mapping_to_str_dict(self, mapping: Mapping) -> dict[str, str]:
        result: dict[str, str] = {}
        for key, value in mapping.items():
            result[key] = str(value)
        return result

    def get_seriescalc(self, params: PvgisSeriescalcParams) -> httpx.Response:
        # for reference actual request example:
        # https://re.jrc.ec.europa.eu/api/v5_3/seriescalc?lat=43.110&lon=11.536&raddatabase=PVGIS-SARAH3&browser=1&outputformat=csv&userhorizon=&usehorizon=1&angle=0&aspect=-180&startyear=2005&endyear=2005&mountingplace=&optimalinclination=0&optimalangles=0&js=1&select_database_hourly=PVGIS-SARAH3&hstartyear=2005&hendyear=2005&trackingtype=0&hourlyangle=0&hourlyaspect=-180&components=1

        url = f'{self.base_url}/v5_3/seriescalc'
        processed_params = self._mapping_to_str_dict(params)

        s = SdkSettings.instance()

        response = httpx.get(
            url,
            params=processed_params,
            timeout=make_timeout_object(),
            verify=s.httpx_verify,
        )
        return response

    @classmethod
    def instance(cls) -> Self:
        global _client_instance
        if not _client_instance:
            _client_instance = cls()
        return _client_instance


def pvgis_csv_to_pandas(csv: str | httpx.Response, tz: str | None = None) -> pd.DataFrame:
    if isinstance(csv, httpx.Response):
        csv = csv.text
    lines = csv.splitlines()
    in_csv = False
    acc = ''
    timestr_matcher = re.compile(r'^(\d{4})(\d{2})(\d{2}):(\d{2})(\d{2})$')
    database = ''
    for line in lines:
        if line.startswith('Radiation database:'):
            database = line.split(':')[1].strip()
            continue
        if not in_csv:
            if line.startswith('time,'):
                acc += re.sub('^time,', 'isoDate,', line) + '\n'
                in_csv = True
            continue
        chunks = line.split(',')
        if len(chunks) == 1:
            break  # empty line means end of csv
        timestr = chunks[0]
        matched = timestr_matcher.match(timestr)
        if not matched:
            raise ValueError(f'Invalid time string: {timestr}')

        iso_time = ''

        g = matched.groups()
        # pvgis only returns minutes, so seconds are always 00
        iso_time = f'{g[0]}-{g[1]}-{g[2]}T{g[3]}:{g[4]}:00Z'

        if not iso_time:
            raise ValueError(f'Failed to parse PVGIS timestamp {timestr}')

        acc += f'{iso_time},{",".join(chunks[1:])}\n'
    df = api_csv_string_to_df(acc, tz=tz)
    if database:
        df.attrs['dataset'] = database.lower()
    return df
