from typing import Optional, Literal
import httpx
import importlib.util

from ..common.settings import SdkSettings


FlowchartRenderer = Literal['markdown', 'kroki_svg', 'kroki_png']


def display_flowchart(flowchart_script, *, renderer: Optional[FlowchartRenderer] = None):
    settings = SdkSettings.instance()
    if renderer is None:
        renderer = settings.default_flowchart_renderer  # pyright: ignore [reportAssignmentType]
    if importlib.util.find_spec('IPython') is None:
        raise ImportError('IPython package is not installed. Please install Jupyter kernel')
    if renderer == 'markdown':
        from IPython.display import display, Markdown, clear_output  # pyright: ignore [reportMissingImports]

        clear_output(wait=True)
        display(Markdown('```mermaid\n' + flowchart_script + '\n```'))
    elif renderer == 'kroki_svg' or renderer == 'kroki_png':
        from IPython.display import display, SVG, Image, clear_output  # pyright: ignore [reportMissingImports]

        # see https://docs.kroki.io/kroki/setup/http-clients/
        format = 'svg' if renderer == 'kroki_svg' else 'png'
        url = f'https://kroki.io/mermaid/{format}'
        headers = {'Content-Type': 'text/plain'}

        try:
            response = httpx.post(
                url,
                content=flowchart_script,
                headers=headers,
                verify=settings.httpx_verify,
                timeout=settings.httpx_timeout,
            )
        except httpx.RequestError as e:
            raise RuntimeError(
                f'Failed to generate the chart using Kroki: {e}. '
                'You may consider a different flowchart renderer, e.g. "markdown"'
            ) from e

        if response.status_code == 200:
            if renderer == 'kroki_svg':
                display(SVG(response.content))
            elif renderer == 'kroki_png':
                display(Image(response.content))
        else:
            print(f'Error: {response.status_code} - {response.text}')
    else:
        raise ValueError(f'Unsupported flowchart renderer: {renderer}')
