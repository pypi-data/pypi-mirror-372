import importlib.util
import textwrap
from typing import Annotated, Optional, Self, Any
from h3 import Literal
import pandas as pd
from dataclasses import dataclass, field

from .describe import get_attrs_description
from ..common.pandas_utils import is_series_or_frame, crop_by_interval
from ..common.settings import SdkSettings
from ..modeling.utils import resample_series
from ..modeling.base_model_context import BaseModelContext
from ..modeling.time_series_model_context import interpret_interval

_letters_per_inch = 10.5
_default_figsize = (12, 2.5)  # in inches
_ignored_attrs = [
    'api_call',
    'origin',
    # 'model_run_stats',
]

PlotRenderer = Literal['matplotlib', 'plotly', 'kaleido']


def _detect_installed(renderer: PlotRenderer) -> bool:
    match renderer:
        case 'matplotlib':
            return importlib.util.find_spec('matplotlib') is not None
        case 'plotly':
            return importlib.util.find_spec('plotly') is not None
        case 'kaleido':
            return importlib.util.find_spec('plotly') is not None and importlib.util.find_spec('kaleido') is not None
        case _:
            raise ValueError(f'Unsupported renderer: {renderer}')


def compare_attrs(attrs_dicts: list[dict]) -> tuple[list[dict], dict]:
    """returns list of dictionaries with differing keys and a dictionary of common keys"""
    if not attrs_dicts:
        raise ValueError('At least one attrs dictionary must be provided.')

    # Exclude keys like "api_call" and "origin" from comparison
    filtered_dicts = [{k: v for k, v in d.items() if k not in _ignored_attrs} for d in attrs_dicts]

    # Identify all unique keys across all attrs_dicts
    all_keys = set().union(*filtered_dicts)

    ignored_keys = set()
    differing_keys = set()
    for key in all_keys:
        val = filtered_dicts[0].get(key)
        for d in filtered_dicts:
            if isinstance(d.get(key), dict):
                ignored_keys.add(key)
                differing_keys.discard(key)
            elif key not in d or d[key] != val:
                differing_keys.add(key)

    # Construct return dictionaries with only differing keys for each resource
    return_dicts = []
    for d in filtered_dicts:
        return_dicts.append({k: v for k, v in d.items() if k in differing_keys})

    # Construct a dictionary of common keys
    common_keys = {}
    for key in all_keys:
        if key in ignored_keys:
            continue
        values = {str(d.get(key)) for d in filtered_dicts}
        if len(values) == 1:
            common_keys[key] = values.pop()
    common_keys = {k: v for k, v in common_keys.items() if k not in _ignored_attrs}

    return return_dicts, common_keys


def _merge_intervals(intervals: list[pd.Interval]) -> pd.Interval:
    assert len(intervals) > 0, 'Cannot merge an empty list of intervals'
    min_left = intervals[0].left
    max_right = intervals[0].right
    for interval in intervals[1:]:
        min_left = min(min_left, interval.left)
        max_right = max(max_right, interval.right)
    result = pd.Interval(left=min_left, right=max_right, closed=intervals[0].closed)
    return result


def _extract_group_id(series: pd.Series, *, group_by: str = 'unit') -> str:
    if not isinstance(series, pd.Series):
        raise ValueError(f'Expected a pandas Series, got: {type(series)}')
    if series.empty:
        raise ValueError('Cannot extract group ID from an empty Series')
    group_id = series.attrs.get(group_by)
    return group_id or str(series.name) or 'unknown'


def _wrap_label(text: str, height: float, max_lines: int = 4, separator: str = '\n') -> str:
    """Wraps y-axis label text if it exceeds available height."""
    max_chars = int(height * _letters_per_inch)
    wrapped_text = separator.join(textwrap.wrap(text, width=max_chars))
    return separator.join(wrapped_text.split(separator)[:max_lines])  # Limit to max_lines


@dataclass
class PlottingItem:
    group_id: str
    interval: pd.Interval
    series: pd.Series
    unique_attrs: dict = field(default_factory=dict)
    label: str = ''


@dataclass
class PlottingChart:
    group_id: str
    interval: pd.Interval
    items: list[PlottingItem]
    group_by: str = 'unit'
    common_attrs: dict = field(default_factory=dict)
    label: str = ''


@dataclass
class PlottingCollection:
    interval: pd.Interval
    charts: list[PlottingChart]
    figsize: tuple[float, float]
    group_by: str = ''

    @classmethod
    def from_series(
        cls,
        series: pd.Series | list[pd.Series | BaseModelContext],
        *,
        to_freq: Optional[str] = None,
        figsize: tuple[float, float] = _default_figsize,
        group_by: str = 'unit',
        interval: Optional[pd.Interval | str | int] = None,
        include_resource_type: bool = False,
    ) -> Self:
        if isinstance(series, tuple):
            series = list(series)
        elif isinstance(series, pd.Series):
            series = [series]

        if isinstance(interval, (str, int)):
            interval = interpret_interval(interval)
        assert isinstance(interval, (pd.Interval, type(None))), 'interval must be a pandas Interval, str, int or None'

        extracted_series = []
        for index, s in enumerate(series):
            if isinstance(s, BaseModelContext):
                # cannot import MeasurementGroup here to avoid circular import
                if hasattr(s, 'measurement') and hasattr(s, 'available_measurements'):
                    df = s.available_measurements  # pyright: ignore [reportAttributeAccessIssue]
                    for resource_type in df.index.values:
                        extracted_series.append(s.measurement(resource_type))  # pyright: ignore [reportAttributeAccessIssue]
                else:
                    raise ValueError(f'Only MeasurementGroup is recognized as series source, got: {type(s)}')

        if extracted_series:
            series = [s for s in series if not isinstance(s, BaseModelContext)] + extracted_series  # pyright: ignore [reportAssignmentType]

        assert len(series) > 0, 'At least one series must be provided.'

        main_tz = None
        for index, s in enumerate(series[:]):
            if not isinstance(s, pd.Series):
                raise ValueError(f'While preparing for plotting, got a non-series in position {index}:  {type(s)}')
            if isinstance(s.index, pd.DatetimeIndex):
                if main_tz is None:
                    main_tz = s.index.tz
                    continue
                if s.index.tz != main_tz:
                    series[index] = s.tz_convert(main_tz)

        if main_tz and interval and interval.left.tz is None:
            # If the interval is naive, convert it to the main timezone
            interval = pd.Interval(
                left=interval.left.tz_localize(main_tz),
                right=interval.right.tz_localize(main_tz),
                closed=interval.closed,
            )

        if interval:
            series = [crop_by_interval(s, interval) for s in series]  # pyright: ignore [reportArgumentType]

        if to_freq:
            series = [resample_series(s, freq=to_freq) for s in series]  # pyright: ignore [reportAssignmentType, reportArgumentType]

        attr_list = []
        items = []
        for s in series:
            if not isinstance(s, pd.Series):
                raise ValueError(f'Expected a pandas Series, got: {type(s)}')
            if s.empty:
                continue
            group_id = _extract_group_id(s, group_by=group_by)
            sub_interval = interval or pd.Interval(s.index.min(), s.index.max(), closed='both')

            items.append(
                PlottingItem(
                    group_id=str(group_id),
                    interval=sub_interval,
                    series=s,
                )
            )
            attr_list.append(s.attrs)

        chart_map = {}
        for item in items:
            group_id = item.group_id
            if group_id not in chart_map:
                chart_map[group_id] = PlottingChart(
                    group_id=group_id,
                    interval=item.interval,
                    items=[],
                )
            chart_map[group_id].items.append(item)

        charts = list(chart_map.values())
        for chart in charts:
            chart.interval = _merge_intervals([item.interval for item in chart.items])

            attr_list = [item.series.attrs for item in chart.items]
            differences, common = compare_attrs(attr_list)
            explicit_label_used = False
            for i, item in enumerate(chart.items):
                item.unique_attrs = differences[i]
                if include_resource_type and not item.unique_attrs.get('resource_type'):
                    if common.get('resource_type'):
                        item.unique_attrs['resource_type'] = common['resource_type']

                if is_series_or_frame(item.series) and item.series.attrs.get('label'):
                    item.label = item.series.attrs['label']
                    explicit_label_used = True
                else:
                    item.label = get_attrs_description(item.unique_attrs, quantity_placeholder='')
            chart.common_attrs = common
            chart.label = get_attrs_description(chart.common_attrs)
            if len(chart.items) == 1 and chart.items[0].label and explicit_label_used:
                chart.label = chart.items[0].label

        interval = _merge_intervals([chart.interval for chart in charts])

        collection = cls(
            interval=interval,
            charts=charts,
            figsize=figsize,
            group_by=group_by,
        )
        return collection

    def plot_matplotlib(
        self,
        legend_loc='upper right',
    ) -> None:
        """Plot a PlottingCollection using matplotlib."""
        if not _detect_installed('matplotlib'):
            raise ImportError('matplotlib package is not installed, while rendering using plotly was requested')
        import matplotlib.pyplot as plt  # pyright: ignore [reportMissingImports]
        from matplotlib.axes import Axes  # pyright: ignore [reportMissingImports]
        import matplotlib.dates as mdates  # pyright: ignore [reportMissingImports]

        figsize = (self.figsize[0], self.figsize[1] * len(self.charts))
        fig, ax = plt.subplots(len(self.charts), 1, figsize=figsize, sharex=True)

        if len(self.charts) == 1:
            ax = [ax]

        for chart_index, chart in enumerate(self.charts):
            axe: Axes = ax[chart_index]
            for item in chart.items:
                label = item.label or '?'
                # item.series.plot(ax=axe, label=label)

                # TODO: consider using bar for agg='sum'
                axe.plot(
                    item.series.index,
                    item.series.values,  # pyright: ignore [reportArgumentType]
                    label=label,
                )
            axe.set_ylabel(_wrap_label(chart.label, self.figsize[1]))
            if len(chart.items) > 1:
                axe.legend(loc=legend_loc)

        last_ax = ax[-1]
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        last_ax.xaxis.set_major_locator(locator)
        last_ax.xaxis.set_major_formatter(formatter)

        plt.show()

    def make_plotly_fig(
        self,
        vertical_spacing: float = 0.1,
        dpi: Annotated[float, 'DPI for converting inches to pixels'] = 92,
        scatter_mode: Annotated[
            str, 'Any combination of "lines", "markers", "text" joined with + characters, e.g. lines+markers'
        ] = 'lines',
        margin_left: int = 20,
        margin_right: int = 20,
        margin_top: int = 40,
        margin_bottom: int = 0,
        layout_bgcolor: str = 'white',
        layout_gridcolor: str = 'lightgray',
        layout_zerolinecolor: str = 'black',
    ) -> Any:
        if not _detect_installed('plotly'):
            raise ImportError('plotly package is not installed, while rendering using plotly was requested')

        import plotly.graph_objects as go  # pyright: ignore [reportMissingImports]
        from plotly.subplots import make_subplots  # pyright: ignore [reportMissingImports]

        figsize = (self.figsize[0], self.figsize[1] * len(self.charts))
        fig_width = figsize[0] * dpi
        fig_height = figsize[1] * dpi

        subplot_titles = [chart.label for chart in self.charts]
        fig = make_subplots(
            rows=len(self.charts),
            cols=1,
            shared_xaxes=True,
            subplot_titles=subplot_titles,
            vertical_spacing=vertical_spacing,
        )

        layout_updates = {}
        for chart_index, chart in enumerate(self.charts):
            row = chart_index + 1
            for item in chart.items:
                resource_type = item.series.attrs.get('resource_type')
                label = item.label or resource_type or '?'
                label = _wrap_label(label, 3, max_lines=3, separator='<br>')
                fig.add_trace(
                    go.Scatter(
                        x=item.series.index,
                        y=item.series.values,
                        mode=scatter_mode,
                        name=label,
                    ),
                    row=row,
                    col=1,
                )
            if self.group_by == 'unit' or len(chart.items) == 1:
                unit = chart.items[0].series.attrs.get('unit', '')
                if unit and unit != 'fraction' and unit != 'dimensionless':
                    layout_updates[f'yaxis{row}'] = dict(
                        ticksuffix=' ' + unit,
                    )

        fig.update_xaxes(zerolinecolor=layout_zerolinecolor, gridcolor=layout_gridcolor)
        fig.update_yaxes(zerolinecolor=layout_zerolinecolor, gridcolor=layout_gridcolor)

        fig.update_layout(
            width=fig_width,
            height=fig_height,
            margin={
                'l': margin_left,
                'r': margin_right,
                't': margin_top,
                'b': margin_bottom,
            },
            plot_bgcolor=layout_bgcolor,
            **layout_updates,
        )
        return fig

    def plot_plotly(
        self,
        vertical_spacing: float = 0.1,
        dpi: Annotated[float, 'DPI for converting inches to pixels'] = 92,
        scatter_mode: Annotated[
            str, 'Any combination of "lines", "markers", "text" joined with + characters, e.g. lines+markers'
        ] = 'lines',
        margin_left: int = 20,
        margin_right: int = 20,
        margin_top: int = 40,
        margin_bottom: int = 0,
        layout_bgcolor: str = 'white',
        layout_gridcolor: str = 'lightgray',
        layout_zerolinecolor: str = 'black',
    ) -> None:
        self.make_plotly_fig(
            vertical_spacing=vertical_spacing,
            dpi=dpi,
            scatter_mode=scatter_mode,
            margin_left=margin_left,
            margin_right=margin_right,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            layout_bgcolor=layout_bgcolor,
            layout_gridcolor=layout_gridcolor,
            layout_zerolinecolor=layout_zerolinecolor,
        ).show()

    def plot_kaleido(
        self,
        vertical_spacing: float = 0.1,
        dpi: Annotated[float, 'DPI for converting inches to pixels'] = 92,
        scatter_mode: Annotated[
            str, 'Any combination of "lines", "markers", "text" joined with + characters, e.g. lines+markers'
        ] = 'lines',
        margin_left: int = 20,
        margin_right: int = 20,
        margin_top: int = 40,
        margin_bottom: int = 0,
        layout_bgcolor: str = 'white',
        layout_gridcolor: str = 'lightgray',
        layout_zerolinecolor: str = 'black',
    ) -> Any:
        if importlib.util.find_spec('IPython') is None:
            raise ImportError('IPython package is not installed, while rendering using kaleido was requested')
        if not _detect_installed('kaleido'):
            if not _detect_installed('plotly'):
                raise ImportError('plotly package is not installed, while rendering using plotly was requested')
            raise ImportError('kaleido package is not installed, while rendering using plotly was requested')
        from IPython.display import Image, display  # pyright: ignore [reportMissingImports]

        display(
            Image(
                self.make_plotly_fig(
                    vertical_spacing=vertical_spacing,
                    dpi=dpi,
                    scatter_mode=scatter_mode,
                    margin_left=margin_left,
                    margin_right=margin_right,
                    margin_top=margin_top,
                    margin_bottom=margin_bottom,
                    layout_bgcolor=layout_bgcolor,
                    layout_gridcolor=layout_gridcolor,
                    layout_zerolinecolor=layout_zerolinecolor,
                ).to_image(
                    format='png',
                    width=self.figsize[0] * dpi,
                    height=self.figsize[1] * len(self.charts) * dpi,
                    scale=2,
                ),
                width=self.figsize[0] * dpi,
            )
        )


def resource_plot(
    *args,
    to_freq: Annotated[Optional[str], 'convert all series to the same frequency before plotting'] = None,
    group_by: str = 'unit',
    figsize: tuple[float, float] = _default_figsize,
    interval: Optional[pd.Interval | str | int] = None,
    renderer: str = '',
    **kwargs,
) -> None:
    """Plot multiple resource as subplots with shared X-axis using matplotlib or plotly"""
    if renderer == '':
        renderer = SdkSettings.instance().default_plot_renderer
    renderer_list = renderer.split(',')
    selected_renderer = ''
    for r in renderer_list:
        if _detect_installed(r):  # pyright: ignore [reportArgumentType]
            selected_renderer = r
            break

    if selected_renderer == '':
        raise ImportError('No plot renderer found. Please install one of the following packages: ' + ', '.join(renderer_list))

    default_include_resource_type = selected_renderer == 'plotly'
    collection = PlottingCollection.from_series(
        args,  # pyright: ignore [reportArgumentType]
        group_by=group_by,
        figsize=figsize,
        to_freq=to_freq,
        interval=interval,
        include_resource_type=kwargs.get('include_resource_type', default_include_resource_type),
    )

    if selected_renderer == 'matplotlib':
        collection.plot_matplotlib(**kwargs)
    elif selected_renderer == 'plotly':
        collection.plot_plotly(**kwargs)
    elif selected_renderer == 'kaleido':
        collection.plot_kaleido(**kwargs)
    else:
        raise ValueError(f'Unsupported renderer: {selected_renderer}')
