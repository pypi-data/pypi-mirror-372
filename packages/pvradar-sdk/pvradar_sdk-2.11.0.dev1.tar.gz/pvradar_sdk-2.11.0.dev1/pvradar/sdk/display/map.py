import importlib.util
from typing import Any, Literal, Optional
from pvlib.location import Location
import pandas as pd
import numpy as np


MapRenderer = Literal['folium']


def _detect_installed(renderer: str) -> bool:
    return importlib.util.find_spec(renderer) is not None


def display_map(
    table: pd.DataFrame,
    *,
    center: Location | tuple[float, float] | None = None,
    center_tooltip: str | None = None,
    color_by: str | None = None,
    size_by: str | None = None,
    autofit: bool = True,
    renderer: MapRenderer = 'folium',
    figsize: Optional[tuple[Any, Any]] = None,  # in inches - (12, 5), or in CSS notation ('100%', '300px')
):
    if not _detect_installed(renderer):
        raise ImportError(f'{renderer} package is not installed. Please install it to use display_map feature')

    if not _detect_installed('matplotlib'):
        raise ImportError(
            'Currently display_map() also requires matplotlib to be installed. Please install it to use display_map feature'
        )

    import folium  # pyright: ignore [reportMissingImports]
    from matplotlib import cm, colors as mcolors  # pyright: ignore [reportMissingImports]

    assert {'latitude', 'longitude'}.issubset(table.columns), "Table must contain 'latitude' and 'longitude' columns"

    if color_by:
        assert color_by in table.columns, f"Column '{color_by}' not found in table."
        assert table[color_by].dtype in [np.float64, np.float32], f"Column '{color_by}' must contain only float values."
        assert not table[color_by].isna().any(), f"Column '{color_by}' contains NaN values."
        norm_color = (table[color_by] - table[color_by].min()) / (table[color_by].max() - table[color_by].min())
        colormap = cm.get_cmap('Blues')
        colors = norm_color.apply(lambda x: mcolors.to_hex(colormap(x)))
    else:
        colors = ['grey'] * len(table)

    if size_by:
        assert size_by in table.columns, f"Column '{size_by}' not found in table."
        assert table[size_by].dtype in [np.float64, np.float32], f"Column '{size_by}' must contain only float values."
        assert not table[size_by].isna().any(), f"Column '{size_by}' contains NaN values."
        norm_size = (table[size_by] - table[size_by].min()) / (table[size_by].max() - table[size_by].min())
        sizes = norm_size * 10 + 5  # Scale size between 5 and 15
    else:
        sizes = [8] * len(table)

    explicit_center = None
    if isinstance(center, Location):
        explicit_center = (center.latitude, center.longitude)
    elif isinstance(center, tuple):
        explicit_center = center

    if explicit_center:
        map_center = explicit_center
    else:
        map_center = (table['latitude'].mean(), table['longitude'].mean())

    DPI = 92  # dots per inch
    if figsize is None:
        figsize = ('100%', '400px')
    map_width = figsize[0] if isinstance(figsize[0], str) else figsize[0] * DPI
    map_height = figsize[1] if isinstance(figsize[1], str) else figsize[1] * DPI

    m = folium.Map(location=map_center, zoom_start=6, width=map_width, height=map_height)

    if explicit_center is not None:
        folium.Marker(
            location=explicit_center,
            icon=folium.Icon(color='red'),
            tooltip=center_tooltip or 'Center',
        ).add_to(m)

    counter = 0

    fg = folium.FeatureGroup(name='Markers')
    for i, row in table.iterrows():
        # iterate over the DataFrame columns and create a popup for each marker
        # based on all columns

        popup_text = '<br>'.join(f'{col}: {row[col]}' for col in table.columns if pd.notna(row[col]))
        popup_text = f'<b>{i}</b><br>{popup_text}'

        marker = folium.CircleMarker(
            location=(row['latitude'], row['longitude']),
            radius=sizes[counter],
            color=colors[counter],
            fill=True,
            fill_color=colors[counter],
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=str(i),
        )
        marker.add_to(fg)
        marker.add_to(m)
        counter += 1

    if autofit and len(table) > 1:
        bounds = fg.get_bounds()
        if bounds:
            m.fit_bounds(bounds)  # type: ignore

    f = folium.Figure(width=map_width, height=map_height)
    m.add_to(f)
    return m


class GeoLocatedDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return GeoLocatedDataFrame

    def display_map(
        self,
        center_tooltip: str | None = None,
        color_by: str | None = None,
        size_by: str | None = None,
        autofit: bool = True,
        figsize: Optional[tuple[Any, Any]] = None,
    ):
        return display_map(
            self,
            center=self.attrs.get('location'),
            center_tooltip=center_tooltip,
            color_by=color_by,
            size_by=size_by,
            autofit=autofit,
            figsize=figsize,
        )
