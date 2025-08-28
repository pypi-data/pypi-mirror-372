import base64
import io
import os
from typing import Callable
import numpy as np


def _figure_to_html(
    fig,
    fmt='svg',
    embed=True,
    html_dir=None,
    img_rel_path=None,
    dpi=100,
    dpi_html=90,
) -> str:
    w, h = fig.get_size_inches()
    kwargs = {'format': fmt, 'bbox_inches': 'tight', 'metadata': {'Date': None}}
    if fmt == 'png':
        kwargs['dpi'] = dpi

    if not embed:
        img_abs_path = os.path.join(html_dir, img_rel_path)
        img_dir = os.path.dirname(img_abs_path)
        os.makedirs(img_dir, exist_ok=True)
        fig.savefig(img_abs_path, **kwargs)
        return f'<img src="{img_rel_path}" width="{w * dpi_html}" height="{h * dpi_html}"/>'

    if fmt == 'svg':
        buf = io.StringIO()
        fig.savefig(buf, **kwargs)
        return buf.getvalue()

    if fmt == 'png':
        pic_io_bytes = io.BytesIO()
        fig.savefig(pic_io_bytes, **kwargs)
        pic_io_bytes.seek(0)
        base64_img = base64.b64encode(pic_io_bytes.read()).decode('utf8')
        src = f'data:image/png;base64, {base64_img}'
        return f'<img src="{src}" width="{w * dpi_html}" height="{h * dpi_html}"/>'

    raise ValueError('Unsupported image format.')


def figure_to_html(
    fig : 'matplotlib.figure.Figure',
    fmt : str = 'svg',
    embed : bool = True,
    html_dir : str = None,
    img_rel_path : str = None,
    dpi : int = 100,
    dpi_html : int = 90,
    callback : Callable[[], None] = None,
) -> str:
    """Convert a matplotlib Figure into HTML.  
       See example: [examples/#example-4-plot](../examples/#example-4-plot)

    Args:
        fig: A matplotlib Figure object
        fmt: Image format
        embed: Whether to embed the image as a data URI in the HTML or save it as a separate file
        html_dir: Output directory of the HTML report (used when embed=False)
        img_rel_path: Relative path from the HTML file to the image file (used when embed=False)
        dpi: Resolution used only when fmt='png'
        dpi_html: Used to calculate the display size in the HTML file
        callback: A function to call after converting (e.g., matplotlib.pyplot.close)

    Returns:
        An HTML string that embeds or links the image
    """
    html = _figure_to_html(fig, fmt, embed, html_dir, img_rel_path, dpi)
    if callback is not None:
        callback()
    return html


def style_float_cols(
    styled: 'pandas.io.formats.style.Styler',
    fmt: str = '{:.3f}',
):
    """Format float columns and right-align them.  
       See example: [examples/#example-5-data-frame](../examples/#example-5-data-frame)

    Args:
        styled: A pandas Styler object
        fmt: A format string to apply to float columns
    """
    formatter = {  
        col: fmt for col, dtype in styled.data.dtypes.items()
        if np.issubdtype(dtype, np.floating)
    }
    return styled.format(formatter).set_properties(
        subset=list(formatter.keys()), **{'text-align': 'right'},
    )


def style_top_ranks_per_row(
    styled: 'pandas.io.formats.style.Styler',
    targets: list[str],
    ascending: bool = True,
    styles: dict[int, str] = {
        1: 'background: #8dce6f;',
        2: 'background: #ccf188;',
    },
):
    """Apply styles to the top 1st and 2nd values in each row.  
       See example: [examples/#example-5-data-frame](../examples/#example-5-data-frame)

    Args:
        styled: A pandas Styler object
        targets: List of column names to apply highlighting to
        ascending: Whether to rank in ascending order (default: True)
        styles: A mapping from rank (1, 2, ...) to CSS style string
    """
    def _highlight(row):
        rank = row.rank(ascending=ascending, method='min')
        return rank.map(lambda x: styles.get(x, ''))
    return styled.apply(_highlight, axis=1, subset=targets)


def lighten_color(hex_color: str, ratio: float=0.5) -> str:
    """Lightens a color given in hex string and returns it as a hex string.

    Args:
        hex_color: A color in hex format
        ratio: The proportion of white to mix with the original color  
               Should be between 0.0 (no change) and 1.0 (full white)  

    Returns:
        A lightened color in hex format

    Example:
        ```python
        from shirotsubaki import utils as stutils
        color = stutils.lighten_color('#336699', ratio=0.5)  # -> '#99B2CC'
        ```
    """
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (
        f'#{int(r + (255 - r) * ratio):02X}'
        f'{int(g + (255 - g) * ratio):02X}'
        f'{int(b + (255 - b) * ratio):02X}'
    )
