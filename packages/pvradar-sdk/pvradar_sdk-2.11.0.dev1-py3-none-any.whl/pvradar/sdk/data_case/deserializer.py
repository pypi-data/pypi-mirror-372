import pandas as pd
from .types import DataCase, DataCaseSeries, DataCaseTable, is_data_case_series, is_data_case_table


def data_case_to_series(data_case: DataCaseSeries) -> pd.Series:
    meta = dict(data_case.get('meta', {}))

    # assume that name='' is the same as name=None
    name = data_case['name'] or None

    if data_case['data_type'] == 'unix_timestamp':
        if 'tz' in meta:
            tz = meta['tz']
            series = pd.to_datetime(pd.Series(data_case['data'], name=name), unit='s', utc=True)  # type: ignore
            series = series.dt.tz_convert(tz)
        else:
            series = pd.to_datetime(data_case['data'], unit='s')  # type: ignore
            series.name = name
    else:
        series = pd.Series(data_case['data'], name=name)
    if 'index' in data_case:
        if 'index_type' in meta and meta['index_type'] == 'unix_timestamp':
            index = pd.to_datetime(data_case['index'], unit='s').tz_localize('UTC')  # type: ignore
            if 'tz' in meta:
                index = index.tz_convert(meta['tz'])
        else:
            index = data_case['index']
        series.index = index  # type: ignore
        if 'freq' in meta:
            converted = series.asfreq(meta['freq'])
            if len(converted) == len(series) and converted.index[-1] == series.index[-1]:
                series = converted
    if 'index_type' in meta:
        meta.pop('index_type')  # type: ignore
    series.attrs = meta  # type: ignore
    return series


def data_case_to_df(data_case: DataCaseTable) -> pd.DataFrame:
    columns: list[pd.Series] = []
    df = pd.DataFrame()
    for column in data_case['columns']:
        name = column['name']
        if name == '((index))':
            assert 'meta' in column, 'when deserializing ((index)) must always have meta'
            index_series = data_case_to_series(column)
            index = pd.to_datetime(index_series.values, utc=True)
            if 'tz' in column['meta']:
                index = index.tz_convert(column['meta']['tz'])
            df.index = index
        else:
            series = data_case_to_series(column)
            columns.append(series)
            df[series.name] = series

    if 'meta' in data_case:
        df.attrs.update(data_case['meta'])  # type: ignore
        if 'freq' in df.attrs:
            df = df.asfreq(df.attrs['freq'])

    for column in columns:
        df[column.name].attrs = column.attrs

    return df


def data_case_to_any(data_case: DataCase) -> pd.Series | pd.DataFrame:
    if not isinstance(data_case, dict):
        raise ValueError(f'only an actual dict is supported as DataCase, got {type(data_case)}')
    if 'case_type' not in data_case:
        raise ValueError('missing case_type in data case dict')
    if is_data_case_series(data_case):
        return data_case_to_series(data_case)
    elif is_data_case_table(data_case):
        return data_case_to_df(data_case)
    elif data_case['case_type'] == 'int':
        assert 'data' in data_case, 'int data case must have data'
        return int(data_case['data'])
    elif data_case['case_type'] == 'float':
        assert 'data' in data_case, 'float data case must have data'
        return float(data_case['data'])
    elif data_case['case_type'] == 'string':
        assert 'data' in data_case, 'string data case must have data'
        return str(data_case['data'])
    elif data_case['case_type'] == 'dict':
        assert 'data' in data_case, 'dict data case must have data'
        return data_case['data']
    else:
        raise ValueError(f'unsupported data case type: {data_case["case_type"]}')
