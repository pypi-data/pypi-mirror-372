"""This module is intended to hold some plot-related utilities that are used in the SunPeek Python package.

Plotting is primarily used to generate visual results for the Performance Check (PC) method, see
`sunpeek/core_methods/pc_method`.
Similar plots are generated for the D-CAT methods, see `sunpeek/core_methods/dcat`
(Note: D-CAT methods currently under development).

The goal is to have common settings for matplotlib based plot creation (like colorblind-friendly colors etc.),
and a common interface to plot methods (see :class:`PlotResult` etc.).

Some helpful matplotlib-related resources:
- https://matplotlib.org/stable/gallery/text_labels_and_annotations/demo_annotation_box.html
- https://matplotlib.org/stable/tutorials/intermediate/legend_guide.html
- https://matplotlib.org/stable/tutorials/advanced/transforms_tutorial.html
- packing text (HPacker, VPacker):
  https://stackoverflow.com/questions/63659519/plotting-text-using-textarea-and-annotationbbox-in-matplotlib
- https://matplotlib.org/stable/gallery/ticks/date_concise_formatter.html
- https://matplotlib.org/stable/api/ticker_api.html
- Customize matplotlib rc params: https://matplotlib.org/stable/tutorials/introductory/customizing.html
- matplotlib mathtext: https://matplotlib.org/stable/tutorials/text/mathtext.html
"""
import copy
import re
import enum
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Final, Union, Dict, Any, Tuple, List, Optional
import tempfile
import numpy as np
import pytz
import pandas as pd
from pathlib import Path
import datetime as dt

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.offsetbox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.offsetbox import AnnotationBbox, TextArea, HPacker, VPacker, OffsetImage
from matplotlib.artist import Artist

import sunpeek
from sunpeek.common.errors import SunPeekError
from sunpeek.common.unit_uncertainty import Q


if sunpeek.__version__ == '0.0.0.dev0':
    # dev version
    try:
        import git

        repo = git.Repo(search_parent_directories=True)
        sunpeek_version = f'dev {repo.head.object.name_rev[0:7]} on branch {repo.head.object.name_rev[41:]}'
    except (ModuleNotFoundError, ImportError):
        sunpeek_version = sunpeek.__version__
else:
    sunpeek_version = sunpeek.__version__


class _Assets(enum.StrEnum):
    favicon_path = 'static_assets/logos/png/SunPeek_Favicon_white_no_S.png'
    logo_path = 'static_assets/logos/png/SunPeek_Logo_white.png'
    sunpeek_url = 'https://docs.sunpeek.org'
    zenodo_dcat_url = 'https://zenodo.org/record/7615253'
    iso_string = 'ISO 24194:2022'
    dcat_string = 'D-CAT (Dynamic Collector Array Test)'


class _StrDefaults(enum.StrEnum):
    backend = 'Agg'
    # Inspired by Nature journal, see
    # https://github.com/garrettj403/SciencePlots/blob/master/scienceplots/styles/journals/nature.mplstyle
    # ['DejaVu Sans', 'Arial', 'Helvetica', 'Lucida Grande', 'Verdana', 'Geneva', 'Lucid', 'Avant Garde', 'sans-serif']
    font_family_sans = 'DejaVu Sans'
    font_family_serif = 'DejaVu Serif'
    mathtext_fontset = 'dejavusans'

    dimensionless_unit = '\u2013'  # en dash
    # dimensionless_unit = '\u2014'   # em  dash
    format_date = '%Y-%m-%d'
    format_time = '%H:%M'
    format_datetime = f'{format_date} {format_time}'

    # String representing a "not available" / NA numeric information.
    na_str = '\u2014'  # em dash


# Color: matplotlib style 'tableau-colorblind10'
# Style: https://viscid-hub.github.io/Viscid-docs/docs/dev/styles/tableau-colorblind10.html
# Color names https://stackoverflow.com/questions/74830439/list-of-color-names-for-matplotlib-style-tableau-colorblind10

# This class follows recommendations in https://personal.sron.nl/~pault/
# Colors are based on the "bright" color scheme.
class _Colors(enum.StrEnum):
    blue = '#4477AA'
    cyan = '#66CCEE'
    green = '#228833'
    yellow = '#CCBB44'
    red = '#EE6677'
    purple = '#AA3377'

    gray = '#BBBBBB'
    pale_grey = '#DDDDDD'
    dark_grey = '#ABABAB'
    very_dark_grey = '#464542'
    grey = gray
    pale_gray = pale_grey
    dark_gray = dark_grey
    very_dark_gray = very_dark_grey

    white = '#FFFFFF'
    almost_black = '#373737'
    missing_data = pale_grey


ASSETS: Final = _Assets
STR_DEFAULTS: Final = _StrDefaults
COLORS: Final = _Colors


@dataclass(frozen=True)
class _Defaults:
    # full_width=16.59 / 2.54,  # full page width data-in-brief Journal, cm to inches
    # page_ratio=0.5625,  # 1080/1920

    page_ratio = 0.7071  # A4 ratio
    full_width = 11.69   # A4 page width in landscape orientation
    full_height = 8.266  # full_width * page_ratio

    fontsize_normal = 11
    fontsize_presentation = 20
    fontsize_text = 9
    fontsize_table = 8
    linespacing_text = 1.2

    # Plot style
    marker_size_plot = 3
    # marker_size_scatter = 15
    marker_size_scatter = 25
    size_multiplier_yield = 8
    marker_facecolor = COLORS.blue
    marker_edgecolor = None
    marker_alpha = 0.8

    linewidth_table_topbottom = 0.75
    linewidth_table_divider = 0.5
    linewidth_thin = 1

    # Margins (in figure fraction coordinates)
    x_left = 0.1
    y_top = 0.92
    xy_topleft = (x_left, y_top)
    x_right = 0.9
    x_right_extreme = 0.93
    y_bottom = 0.15
    xy_bottomright = (x_right, y_bottom)
    y_bottom_extreme = 0.1

    # Separators (in points)
    sep_minor = 15
    sep_major = 20
    sep_huge = 35
    sep_axestitle = 6
    sep_table_rows = 3

    # Offsets (in points)
    offset_footer = (12, 12)
    offset_page_number = (-20, 12)


DEFAULTS: Final = _Defaults


def get_logo(relative_path: str):
    """Load image from given relative path. Works locally and in CI.
    """
    p = Path(relative_path)
    if not p.is_file():
        p = Path(__file__).resolve().parents[2] / relative_path
    if not p.is_file():
        raise FileNotFoundError(f"Logo not found at {p}")

    return plt.imread(p)


def str_or_na(x: Union[str, Q],
              idx: int = None,
              unit: str = None,
              fmt: str = '.2g',
              ) -> str:
    """Return string or formatted Quantity, if argument not empty, else return the default NA string.
    """
    default = STR_DEFAULTS.na_str

    # String
    if isinstance(x, str):
        if not x:
            return default
        return x

    # Quantity
    if isinstance(x, Q):
        if x is None:
            return default
        if idx is not None:
            x = x[idx]
        apply_format = lambda _x, _fmt: f'{_x.m:{_fmt}}'
        if unit is None:
            return apply_format(x, fmt)
        return apply_format(x.to(unit), fmt)
    # default
    return default


@dataclass
class PlotResult:
    figure: Figure
    filename: Union[Path, str]


class PlotTarget(enum.StrEnum):
    print = 'print'
    presentation = 'presentation'


@dataclass
class PlotSettings:
    """Settings for PC Method plots & pdf report generation.

    Parameters
    ----------
    target : Union[PlotTarget, str], optional
        Font sizes and some other settings depend on this.
        E.g. target == 'presentation' uses larger font size.
    with_interval_plots: bool, optional
        If True, full-resolution plots of each interval are produced.
        May result in quite a lot of pages, so not turned on by default.
    anonymize: bool, optional
        If True, plant and array names and some other information are anonymized, i.e.
        not stated explicitly in the plots / report.
    add_footer: bool, optional
        If True, a default footer is added to each plot (except for cover page).
    include_creation_date: bool = field(default=True),
        If True, the date the pdf report is generated is added to the cover page.
    """
    target: Union[PlotTarget, str] = field(default=PlotTarget.print)
    with_interval_plots: bool = field(default=False)
    anonymize: bool = field(default=False)
    add_footer: bool = field(default=True)
    include_creation_date: bool = field(default=True)


def update_rcparams(target: PlotTarget = PlotTarget.print,
                    font_family: str = None,
                    font_size: int = None,
                    ) -> Dict[str, Any]:
    """Update plot parameters, depending on plot target.
    """
    if target not in list(PlotTarget):
        raise ValueError(f'Invalid value for target: "{target}". '
                         f'Valid values are: {", ".join(list(PlotTarget))}')

    font_family = font_family or STR_DEFAULTS.font_family_serif
    if target == PlotTarget.print:
        font_size = font_size or DEFAULTS.fontsize_normal
    elif target == PlotTarget.presentation:
        font_size = font_size or DEFAULTS.fontsize_presentation

    # Publication quality plt settings inspired by http://aeturrell.com/2018/01/31/publication-quality-plots-in-python/
    # Avoid black unless necessary
    # Taken from https://atchen.me/research/code/data-viz/2022/01/04/plotting-matplotlib-reference.html
    # Axes props from https://github.com/garrettj403/SciencePlots/blob/master/scienceplots/styles/science.mplstyle
    plt.rcParams.update({
        'font.family': font_family,
        'font.size': font_size,
        'text.color': COLORS.almost_black,
        'text.usetex': False,
        # 'mathtext.default': 'it',
        'mathtext.default': 'regular',
        'mathtext.fontset': 'cm',

        'figure.dpi': 600,
        'figure.titlesize': font_size + 5,

        # 'figure.subplot.left':     DEFAULTS.x_left,
        # 'figure.subplot.bottom':     DEFAULTS.y_bottom,
        # 'figure.subplot.right':     DEFAULTS.x_right,
        # 'figure.subplot.top':     DEFAULTS.y_top,

        'axes.titlesize': font_size - 2,
        'axes.labelsize': font_size - 3,
        'axes.labelpad': 3,
        'axes.titlepad': 6,
        'axes.linewidth': 0.5,
        'axes.edgecolor': COLORS.almost_black,
        'axes.labelcolor': COLORS.almost_black,

        'grid.alpha': 0.5,
        'grid.linewidth': 0.5,
        'lines.linewidth': 1,

        'patch.linewidth': 0.25,
        'patch.edgecolor': COLORS.almost_black,
        'patch.force_edgecolor': True,
        # 'hatch.color': COLORS.almost_black,

        'legend.fontsize': font_size - 4,
        'legend.title_fontsize': font_size - 3,
        'legend.frameon': True,
        # 'legend.frameon': False,
        'legend.edgecolor': 'none',
        'legend.framealpha': 0.8,
        'legend.borderpad': 0.5,
        'legend.columnspacing': 1.5,
        'legend.labelspacing': 0.15,

        'xtick.direction': 'in',
        'xtick.top': True,
        'xtick.labelsize': font_size - 3,
        'xtick.color': COLORS.almost_black,
        'xtick.major.size': 3,
        # 'xtick.major.size': 2,
        'xtick.minor.size': 1.5,
        # 'xtick.minor.size': 2,
        'xtick.minor.visible': True,
        'xtick.major.pad': 3,
        # 'xtick.major.pad': 1,
        'xtick.major.width': 0.5,
        # 'xtick.minor.pad': 1,
        'xtick.minor.width': 0.5,

        'ytick.direction': 'in',
        'ytick.right': True,
        'ytick.labelsize': font_size - 3,
        'ytick.color': COLORS.almost_black,
        'ytick.major.size': 3,
        # 'ytick.major.size': 2,
        'ytick.major.pad': 3,
        # 'ytick.major.pad': 1,
        'ytick.major.width': 0.5,
        'ytick.minor.size': 1.5,
        # 'ytick.minor.size': 2,
        'ytick.minor.visible': True,
        # 'ytick.minor.pad': 1,
        'ytick.minor.width': 0.5,
    })

    return dict(
        font_family=font_family,
        font_size=font_size,
        font_size_text=font_size - 2,
    )


def prepare_figure(
        settings: PlotSettings = PlotSettings(),
        width: float = DEFAULTS.full_width,
        height: float = DEFAULTS.full_height,
        suppress_footer: bool = False,
) -> Tuple[matplotlib.figure.Figure, dict]:
    """Create default matplotlib figure in given dimensions, set backend, update rcParams, add footer.
    """
    plt.switch_backend(STR_DEFAULTS.backend)
    params = update_rcparams(target=settings.target)
    fig = plt.figure(figsize=(width, height))

    if settings.add_footer and not suppress_footer:
        set_footer(fig)

    return fig, params


def create_pdf(fig_list: List[matplotlib.figure.Figure],
               filename: str = 'sunpeek_report',
               export_folder: Union[str, Path] = None,
               add_page_numbers: bool = True,
               add_page_number_first_page: bool = False,
               metadata: dict = None,
               # **kwargs,
               ) -> Optional[Path]:
    """Combine matplotlib figures into a pdf report and save file to disk. Add page numbers and metadata to pdf file.

    Parameters
    ----------
    fig_list : List[matplotlib.figure.Figure]
        List of matplotlib figures used to create
        If `fig_list` is None, will create all figures using :func:`plot_all`.
    filename : str = 'pc_report', optional
        The generated pdf report will be saved under this name, with extension ".pdf".
    export_folder : Union[str, Path], optional
        Folder to which the pdf file is saved. If None, a temporary folder is used.
    add_page_numbers : bool, optional
        If True, page numbers are added
    add_page_number_first_page : bool, optional
        If False, first report page (cover page, see :func:`plot_cover`) has no page number.
    metadata : dict, optional
        Metadata information to be attached to the pdf file. Empty dict if None.
    """
    if not fig_list:
        return None
    if isinstance(fig_list, matplotlib.figure.Figure):
        raise SunPeekError('Internal error: create_pdf expected list, but got Figure.')

    # Write pdf
    full_fn = get_filename(filename=filename, extension='.pdf', folder=export_folder)
    metadata = metadata or {}
    pdf_doc = PdfPages(full_fn, metadata=metadata)
    with pdf_doc as d:
        n_pages = len(fig_list)
        for i, fig in enumerate(fig_list, start=1):
            add_page_number = add_page_numbers and (True if i > 1 else add_page_number_first_page)
            if add_page_number:
                set_page_number(fig, i, n_pages)
            d.savefig(fig)
            plt.close(fig)

    return full_fn


def get_filename(filename: str,
                 extension: str,
                 folder: Union[str, Path],
                 ) -> Path:
    """Create & return Path to store figure. Create folder if doesn't exist. Create unique filename if file exists.
    """
    fldr = tempfile.TemporaryDirectory().name if folder is None else folder
    fldr = Path(fldr)
    fldr.mkdir(exist_ok=True)

    full_path = lambda fn: fldr.joinpath(fn).with_suffix(extension)

    # If file does not exist yet, return it
    filename_path = full_path(filename)
    if not filename_path.is_file():
        return filename_path

    # If file exists, create a unique filename
    i = 1
    filename_path = full_path(f"{filename}-{i}")
    while filename_path.is_file():
        i += 1
        filename_path = full_path(f"{filename}-{i}")
    return filename_path


def filename_from_string(s: str, max_length: int = 255) -> str:
    """ Return string that is valid as a filename from given string s.
    """
    s = re.sub(r'[^\w\s-]', '', s).strip()
    s = re.sub(r'\s+', '-', s)
    return s[:max_length].strip('-').lower()


def set_footer(fig) -> None:
    """Add footer string and SunPeek small logo at bottom right of fig page.
    """
    # Logo
    box = HPacker(children=[OffsetImage(get_logo(ASSETS.favicon_path), zoom=0.04)],
                  pad=0, sep=DEFAULTS.sep_minor)
    artist = annotation_bbox(box, xy=(0.015, 0), xybox=DEFAULTS.offset_footer, box_alignment=(0, 0))
    fig.add_artist(artist)

    # Text
    footer_text = (f'{ASSETS.sunpeek_url}\n'
                   f'Generated with SunPeek version {sunpeek_version}.')
    textprops = dict(style='italic', size=plt.rcParams['font.size'] - 4, ha='left', va='bottom')
    box = HPacker(children=[TextArea(footer_text, textprops=textprops)],
                  pad=0, sep=DEFAULTS.sep_minor)
    artist = annotation_bbox(box, xy=(0, 0), xybox=(60, DEFAULTS.offset_footer[1]), box_alignment=(0, 0))
    fig.add_artist(artist)


def set_page_number(fig, page_number: int, n_pages: int = None) -> None:
    """Add page number at top right of fig page.
    """
    txt_n_pages = f' / {n_pages}' if n_pages else ''
    page_text = f'Page {page_number}{txt_n_pages}'

    textprops = dict(style='italic', size=plt.rcParams['font.size'] - 4, ha='right', va='bottom')
    box = HPacker(children=[TextArea(page_text, textprops=textprops)], pad=0, sep=DEFAULTS.sep_minor)
    artist = annotation_bbox(box, xy=(1, 0), xybox=DEFAULTS.offset_page_number, box_alignment=(1, 0))
    fig.add_artist(artist)


def dict_to_box(d: OrderedDict,
                textprops: dict,
                vsep: float = DEFAULTS.sep_table_rows,
                hsep: float = DEFAULTS.sep_minor) -> matplotlib.offsetbox.HPacker:
    """Arrange dictionary keys and values aligned in tabular format.
    """
    d_ = OrderedDict((k, v) for k, v in d.items() if v)
    return HPacker(children=[
        VPacker(children=[TextArea(k, textprops=textprops) for k in d_], sep=vsep),
        VPacker(children=[TextArea(v, textprops=textprops) for v in d_.values()], sep=vsep),
    ], sep=hsep)


def box_title(title_str, textprops: dict = None, fontsize: float = None) -> matplotlib.offsetbox.TextArea:
    """Create default title text box used on most pages.
    font_size overwrites textprops, if both are given.
    """
    if textprops is None:
        textprops = dict(weight='bold', size=plt.rcParams['figure.titlesize'])
    if fontsize is not None:
        textprops['size'] = fontsize
    return TextArea(title_str, textprops=textprops)


def anonymize(d: OrderedDict,
              do_anonymize: bool = False,
              anon_txt: str = '<anonymized>',
              na_txt: str = 'N/A') -> OrderedDict:
    """Replace empty values with 'N/A', and sensitive information with '<anonymized>' string.
    """
    d = OrderedDict((k, (na_txt if not v else v)) for k, v in d.items())
    if do_anonymize:
        d = OrderedDict((k, anon_txt) for k in d)
    return d


def utc_str(d: Union[dt.datetime, pd.Timestamp],
            tz: pytz.timezone,
            format_spec: str = '%Y-%m-%d %H:%M') -> str:
    """Pretty-print a timezone-aware datetime to e.g. '2017-05-25 10:31 (UTC+1)'.
    """
    d_tz = pd.to_datetime(d).tz_convert(tz)
    return f'{d_tz:{format_spec}} (UTC{int(d_tz.utcoffset().total_seconds() / 3600):+0})'


def get_xy_below(artist: Artist,
                 vsep: float = DEFAULTS.sep_major,
                 ) -> Tuple[float, float]:
    """Given some artist, get the vertical position where the "next lower" element can be drawn, in figure fraction.
    The next element is: the artist's bottom value minus some vertical separation (given in points).

    Returns
    -------
    Tuple (x, y) (or left, top) of the "next lower" element, in figure fraction coordinates.
    """
    fig = artist.figure
    fig.draw_without_rendering()
    artist_bbox = artist.get_window_extent().transformed(fig.transFigure.inverted())
    vsep_in_figure_fraction = points_to_figfraction(artist.figure, y_points=vsep)[1]

    return artist_bbox.xmin, artist_bbox.ymin - vsep_in_figure_fraction


def get_rectangle_below(artist: Artist,
                        bottom: float = DEFAULTS.y_bottom_extreme,
                        right: float = DEFAULTS.x_right,
                        vsep: float = DEFAULTS.sep_major,
                        hoffset: float = 0,
                        ) -> Tuple[float, float, float, float]:
    """Like get_xy_below(), but returns rectangle (left, bottom, width, height) as required by fig.add_axes().
    """
    left, top = get_xy_below(artist, vsep=vsep)
    hoffset_fig_fraction = points_to_figfraction(artist.figure, x_points=hoffset)[0]
    left = left + hoffset_fig_fraction
    width = right - left
    height = top - bottom

    return left, bottom, width, height


def annotation_bbox(box: matplotlib.offsetbox.OffsetBox,
                    xy: Tuple[float, float],
                    xycoords: str = 'figure fraction',
                    xybox: Tuple[float, float] = (0, 0),
                    boxcoords: str = 'offset points',
                    box_alignment: Tuple[float, float] = (0, 1),
                    frameon: bool = False,
                    pad: float = 0,
                    ) -> matplotlib.offsetbox.AnnotationBbox:
    """Returns a normal AnnotationBbox. This is just a helper to overcome the often-forgot pad=0 argument,
    which easily leads to misaligned artists.
    """
    return AnnotationBbox(box, xy=xy, xycoords=xycoords, xybox=xybox, boxcoords=boxcoords,
                          box_alignment=box_alignment, frameon=frameon, pad=pad)


def points_to_figfraction(fig: matplotlib.figure.Figure,
                          x_points: float = 0,
                          y_points: float = 0,
                          ) -> Tuple[float, float]:
    """Transform a value in points to figure fraction coordinates in y direction.
    """
    # y_pixels = y_points * plt.rcParams['figure.dpi'] / 72.
    # return fig.transFigure.inverted().transform([(0, y_pixels)])[0][1]

    dpi = plt.rcParams['figure.dpi']
    x_pixels = dpi * x_points / 72.
    y_pixels = dpi * y_points / 72.
    np_arr = np.array([[x_pixels, y_pixels]])

    return tuple(fig.transFigure.inverted().transform(np_arr)[0])


def points_to_data(ax: matplotlib.pyplot.Axes,
                   x_points: float = 0,
                   y_points: float = 0,
                   ) -> Tuple[float, float]:
    """Transform an offset value in points to data coordinates.
    """
    xy_pixels = [v * plt.rcParams['figure.dpi'] / 72. for v in [x_points, y_points]]
    xy = ax.get_window_extent().min + tuple(xy_pixels)
    x, y = ax.transData.inverted().transform(xy)

    return float(x), float(y)


@dataclass
class TableColumnFormat:
    header_str: str = field(default=None)
    unit_str: str = field(default=None)
    width: float = field(default=1.)
    bold: bool = field(default=False)
    ha: str = field(default='left')
    fontsize: float = field(default=DEFAULTS.fontsize_table)


def add_table(ax: matplotlib.pyplot.Axes,
              df: pd.DataFrame,
              col_formats: Dict[str, TableColumnFormat] = None,
              divider_lines: Union[range, List[int]] = None,
              hpad: float = 2,
              vpad: float = 1,
              vpad_header: float = 2,
              vpad_lines: float = 0,
              cell_vspace: float = 1.9,
              cell_vspace_header: float = 2.5,
              header_facecolor=COLORS.pale_grey,
              ) -> int:
    """Create matplotlib table using only standard components (text, plot etc.).
    Column formats can be adapted via TableColumns class.
    Passed axes is reduced to necessary height and is returned, so it can be used to place subsequent artists.
    Inspired by: https://www.sonofacorner.com/beautiful-tables/

    Returns
    -------
    Number of rendered rows of df (might not be all if there is not enough space on the page).
    """
    df = copy.deepcopy(df.loc[::-1, :])
    df = df.set_index(pd.RangeIndex(start=len(df) - 1, stop=-1, step=-1))
    # Fallback: Use df column names as headers
    if col_formats is None:
        col_formats = dict()
    # Make sure col_formats keys match df columns
    if not all([k in df.columns for k in col_formats]):
        raise ValueError('Invalid inputs: Need a TableColumn object for each DataFrame column.')
    # Undefined formats: Use default
    for k in df.columns:
        if k not in col_formats.keys():
            col_formats[k] = TableColumnFormat()

    has_units = any([cf.unit_str is not None for cf in col_formats.values()])
    nrows_caption = (2 if has_units else 1)
    nrows_main, ncols = df.shape

    # Calculate required vertical table height
    fig = ax.figure
    max_fontsize = max([cf.fontsize for cf in col_formats.values()])
    cell_height__points = cell_vspace * max_fontsize
    header_height__points = cell_vspace_header * max_fontsize
    total_header_height__points = nrows_caption * header_height__points

    def get_table_height_ff(nrows_main_):
        table_height__points = nrows_main_ * cell_height__points + total_header_height__points + 2 * vpad_lines
        table_height__ff = points_to_figfraction(fig, y_points=table_height__points)[1]
        return table_height__ff

    # Auto-pagination: Treat case if table does not fit completely in axes
    required_height = get_table_height_ff(nrows_main)
    available_height = ax.get_position().height
    if required_height <= available_height:
        # Full DataFrame can be rendered
        nrows_main = len(df)
        table_height = required_height
    else:
        # Render part of DataFrame, return number of rendered rows
        overhead_height__ff = points_to_figfraction(fig, y_points=total_header_height__points)[1]
        available_height_rows = available_height - overhead_height__ff
        cell_height__ff = points_to_figfraction(fig, y_points=cell_height__points)[1]
        nrows_main = int(np.floor(available_height_rows / cell_height__ff))
        table_height = get_table_height_ff(nrows_main)
        divider_lines = [d for d in divider_lines if d <= nrows_main]
        df = df.loc[df.index < nrows_main]

    # Set axes
    ax_pos = ax.get_position()
    # Reduce height to table_height (axes was passed with maximum available height, make it only as large as needed)
    ax.set_position((ax_pos.xmin, ax_pos.ymax - table_height, ax_pos.width, table_height))
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows_main + nrows_caption)
    [hpad__data, vpad__data] = points_to_data(ax, hpad, vpad)
    vpad_header__data = points_to_data(ax, y_points=vpad_header)[1]
    vpad_lines__data = points_to_data(ax, y_points=vpad_lines)[1]
    header_height__data = points_to_data(ax, 0, header_height__points)[1]
    ax.set_ylim(-vpad_lines__data, nrows_main + nrows_caption * header_height__data + vpad_lines__data)
    header_height__data = points_to_data(ax, 0, header_height__points)[1]
    ax.set_ylim(-vpad_lines__data, nrows_main + nrows_caption * header_height__data + vpad_lines__data)

    # Calculate column positions, normalize widths
    widths = [col_formats[k].width for k in df.columns]
    norm_ratio = ncols / sum(widths)
    norm_widths = [w * norm_ratio for w in widths]
    x_positions: list[float] = [0.0]
    x_positions.extend(list(np.cumsum(norm_widths)))
    x_positions_final = x_positions
    for i, col in enumerate(df.columns):
        ha = col_formats[col].ha
        if ha == 'center':
            x_positions_final[i] = 0.5 * (x_positions[i] + x_positions[i + 1])
        elif ha == 'left':
            x_positions_final[i] = x_positions[i] + hpad__data
        elif ha == 'right':
            x_positions_final[i] = x_positions[i + 1] - hpad__data
        else:
            raise ValueError(f'Invalid horizontal alignment: "{ha}".')

    # Add table's main text
    for i in range(nrows_main):
        y_data = i + 0.5 + vpad__data
        for column, x_data in zip(df.columns, x_positions_final):
            cf = col_formats[column]
            ax.annotate(
                xy=(x_data, y_data),
                text=df[column].iloc[i],
                fontsize=cf.fontsize,
                weight='bold' if cf.bold else 'normal',
                ha=cf.ha,
                va='center_baseline',
            )

    # Add units
    if has_units:
        y_data = nrows_main + 0.5 * header_height__data + vpad_header__data
        for column, x_data in zip(df.columns, x_positions_final):
            cf = col_formats[column]
            ax.annotate(
                xy=(x_data, y_data),
                text=cf.unit_str,
                fontsize=cf.fontsize - 1,
                ha=cf.ha,
                va='center_baseline',
                weight='normal',
                # style='italic',
            )

    # Add column headers
    y_data = ax.get_ylim()[1] - vpad_lines__data - vpad_header__data
    for column, x_data in zip(df.columns, x_positions_final):
        cf = col_formats[column]
        ax.annotate(
            xy=(x_data, y_data),
            text=column if cf.header_str is None else cf.header_str,
            fontsize=cf.fontsize,
            ha=cf.ha,
            weight='bold',
            va='top',
        )

    # Top & bottom line
    style = dict(color=COLORS.almost_black,
                 linewidth=DEFAULTS.linewidth_table_topbottom, marker='')
    for y in [ax.get_ylim()[0], nrows_main, ax.get_ylim()[1]]:
        ax.plot(list(ax.get_xlim()), [y, y], zorder=1.5, **style)
    # Divider lines
    style = dict(color=COLORS.almost_black,
                 linewidth=DEFAULTS.linewidth_table_divider,
                 alpha=plt.rcParams['grid.alpha'],
                 linestyle='-', marker='')
    divider_lines = [] if divider_lines is None else divider_lines
    for y in divider_lines:
        ax.plot(list(ax.get_xlim()), [y, y], zorder=1.5, **style)

    # Fill header
    if header_facecolor is not None:
        ax.fill_between(
            x=ax.get_xlim(),
            y1=ax.get_ylim()[1],
            y2=nrows_main,
            facecolor=header_facecolor,
            edgecolor='None',
            alpha=0.5,
        )

    ax.set_axis_off()

    return nrows_main
