from typing import Annotated
from pydantic import Field
import pandas as pd

from ...common.exceptions import PvradarSdkError
from ...common.pandas_utils import api_csv_string_to_df, crop_by_interval
from ...modeling.time_series_model_context import interval_to_str
from ..engine.engine_types import ModelRunResourceLink
from ..client import PvradarClient
from ...modeling.decorators import standard_resource_type
from .pvradar_project import PvradarProject
from ...modeling import resource_types as R


@standard_resource_type(R.soiling_loss_factor)
def project_soiling_loss_factor(
    context: Annotated[PvradarProject, Field()],
    interval: pd.Interval,
):
    body: ModelRunResourceLink = {
        'resource_link_type': 'model_run',
        'model_context_locator': {
            'id': None,
            'project_id': context.platform_project_manifest['id'],
            'interval': interval_to_str(interval),
        },
        'model_recipe': {'model_name': 'project_soiling_loss_factor', 'params': {}},
    }

    response = PvradarClient.instance().execute_model_run(body)
    if 'errors' in response:
        raise PvradarSdkError(f'Errors in model run: {response["errors"]}')
    if 'data' not in response:
        raise PvradarSdkError('No data in model run response')
    csv_string = response['data'].get('data')
    assert isinstance(csv_string, str), 'Expected CSV string in response'
    df = api_csv_string_to_df(csv_string)

    assert 'soiling_level_percentage' in df.columns, 'Expected soiling_level_percentage column in response'
    series = df['soiling_level_percentage'] / 100.0

    assert isinstance(series.index, pd.DatetimeIndex), 'Expected DatetimeIndex in response'
    new_index = series.index.tz_localize(None).tz_localize(interval.left.tz)
    series.index = new_index

    cropped = crop_by_interval(series, interval)
    return cropped
