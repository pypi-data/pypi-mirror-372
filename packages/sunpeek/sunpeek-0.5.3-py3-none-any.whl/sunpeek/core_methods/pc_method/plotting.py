"""Module for creating plots and pdf report for the PC method.

Notes
-----
- Main method is :fun:`create_pdf_report`.
- Plots can be created individually by functions like :fun:`plot_cover()` etc., or also
by using the methods in the :class:`PCPlots` class. The functions are thin wrappers around the class methods.
- Settings are documented in the :class:`plot_utils.PlotSettings` class.
- Tests for this module are in :mod:`test_pc__FHW_plot.py`
- Only tested for FHW plant. Not guaranteed to work if `array.tp` is None.
"""
from collections import OrderedDict
from typing import Union, Optional, List
import numpy as np
import pandas as pd
import datetime as dt
from pathlib import Path
import pendulum
import pytz

import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.ticker as mtick
from matplotlib.offsetbox import AnnotationBbox, TextArea, HPacker, VPacker, OffsetImage
from matplotlib.colors import LinearSegmentedColormap

from sunpeek.common.errors import PCMethodError
from sunpeek.common.utils import sp_logger
from sunpeek.common import plot_utils as pu
from sunpeek.common.unit_uncertainty import Q
import sunpeek.components.outputs_pc_method as results
from sunpeek.core_methods.pc_method.main import METHOD_DESCRIPTION


def create_pdf_report(pc_output: results.PCMethodOutput,
                      settings: Optional[pu.PlotSettings] = None,
                      fig_list: List[matplotlib.figure.Figure] = None,
                      filename: str | None = None,
                      export_folder: Union[str, Path] = None,
                      add_page_numbers: bool = True,
                      add_page_number_first_page: bool = False,
                      **kwargs,
                      ) -> Optional[Path]:
    """Create PC method report, with page numbers and metadata.

    Parameters
    ----------
    pc_output : results.PCMethodOutput
        Main object to hold the data used to create the plots.
    settings: :class:`pu.PlotSettings`
        Settings used by the various :class:`PCPlots` methods.
    fig_list: List[matplotlib.figure.Figure]
        List of matplotlib figures used to create
        If `fig_list` is None, will create all figures using :func:`plot_all`.
    filename: str = 'pc_report', optional
        The generated pdf report will be saved under this name, with extension ".pdf".
        If None, a default filename is generated, based on the PC settings.
    export_folder: Union[str, Path], optional
        Folder to which the pdf file is saved. If None, a temporary folder is used.
    add_page_numbers: bool, optional
        If True, page numbers are added
    add_page_number_first_page: bool, optional
        If False, first report page (cover page, see :func:`plot_cover`) has no page number.

    Notes
    -----
    - kwargs are passed to individual plot methods of PCPlots class via `plot_all()`.
    - square_axis_range : List
        Axes limits (minimum and maximum), used for x and y axis in :func:`plot_square`.
    - y_ratio_limits : List
        Axes limits (minimum and maximum), used for y axis in :func:`plot_time`.
    - axes_limits_interval_plots : dict
        Maximum y axis limits, used for the subplot axes in :func:`plot_intervals`.
        Must contain keys 'te_max', 'rd_max', 'tp_max', 'vf_sp_max'.
    """
    pc_plots = PCPlots(pc_output, settings)
    fig_list = fig_list or pc_plots.plot_all(**kwargs)
    if not fig_list:
        raise ValueError('Cannot produce report: No report page plots given, or none returned from plot_all().')

    # pdf Metadata
    metadata = {'Title': METHOD_DESCRIPTION,
                'Author': f'SunPeek, {pu.ASSETS.sunpeek_url}',
                'Creator': f'SunPeek, {pu.ASSETS.sunpeek_url}',
                'Subject': f'Performance Check for Large Solar Thermal Plants according to {pu.ASSETS.iso_string}',
                'Producer': 'SunPeek using matplotlib',
                'CreationDate': dt.datetime.now(tz=pytz.timezone(pc_output.plant.local_tz_string_with_DST)),
                'Keywords': '',
                }

    # Create pdf document
    full_fn = pu.create_pdf(fig_list=fig_list,
                            filename=filename or default_filename(pc_output, pc_plots.settings.with_interval_plots),
                            export_folder=export_folder,
                            add_page_numbers=add_page_numbers,
                            add_page_number_first_page=add_page_number_first_page,
                            metadata=metadata,
                            )

    sp_logger.info(f'Saved PC report to "{full_fn}"')

    return full_fn


def default_filename(pc_output: results.PCMethodOutput,
                     with_interval_plots: bool) -> str:
    return (f'PC_report, {pc_output.plant.name}, '
            f'{pc_output.evaluation_mode}, '
            f'formula_{pc_output.formula}, '
            f'wind_{"used" if pc_output.wind_used else "ignored"}'
            f'{"" if not with_interval_plots else ", with_interval_plots"}')


def plot_all(pc_output: results.PCMethodOutput,
             settings: Optional[pu.PlotSettings] = None,
             **kwargs,
             ) -> Optional[List[matplotlib.figure.Figure]]:
    """Produce "all" PC figures that should go into a report.
    """
    return PCPlots(pc_output, settings).plot_all(**kwargs)


def plot_cover(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
               ) -> Optional[pu.PlotResult]:
    """Cover page for Power Check report.
    include_creation_date : Overwrites value in settings if not None.
    """
    return PCPlots(pc_output, settings).plot_cover()


def plot_bars(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
              ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plot overview result plot, horizontal bars with average powers in PC intervals, measured vs. estimated.
    """
    return PCPlots(pc_output, settings).plot_bars()


def plot_shadow_and_intervals(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                              ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plots ratio of measured vs. estimated power over time.
    """
    return PCPlots(pc_output, settings).plot_shadow_and_intervals()


def plot_square(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                axis_range: Optional[List] = None,
                ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plot measured vs. estimated yield in intervals. Always creates 2 subplots (with, w/o f_safe).
    """
    return PCPlots(pc_output, settings).plot_square(axis_range)


def plot_time(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
              y_ratio_limits: Optional[List] = None,
              ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plot ratio of measured vs. estimated power over time.
    """
    return PCPlots(pc_output, settings).plot_time(y_ratio_limits)


def plot_plant_overview(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                        ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plant overview page: plant details, arrays + areas etc.
    """
    return PCPlots(pc_output, settings).plot_plant_overview()


def plot_collector_overview(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                            ) -> Optional[List[matplotlib.figure.Figure]]:
    """Collector overview page: collector details, IAMs etc.
    """
    return PCPlots(pc_output, settings).plot_collector_overview()


def plot_data_overview(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                       ) -> Optional[List[matplotlib.figure.Figure]]:
    """Page with considered data: Table with data points considered, on the basis of ISO 24194 Annex A.
    """
    return PCPlots(pc_output, settings).plot_data_overview()


def plot_symbols_overview(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                          ) -> Optional[List[matplotlib.figure.Figure]]:
    """Page with symbols / abbreviations used in the report.
    """
    return PCPlots(pc_output, settings).plot_symbols_overview()


def plot_intervals(pc_output: results.PCMethodOutput, settings: Optional[pu.PlotSettings] = None,
                   axes_limits: Optional[List] = None,
                   ) -> Optional[List[matplotlib.figure.Figure]]:
    """Plot full-resolution data for temperatures, power, volume flow etc. for all intervals.
    """
    return PCPlots(pc_output, settings).plot_intervals(axes_limits)


class PCPlots:
    pc_output: Optional[results.PCMethodOutput] = None
    settings: pu.PlotSettings

    def __init__(self, pc_output, settings):
        self.pc_output = pc_output
        self.settings = settings or pu.PlotSettings()

    def plot_all(self,
                 **kwargs
                 ) -> Optional[List[matplotlib.figure.Figure]]:
        """Produce "all" PC figures that should go into a report.
        """
        if self.no_output():
            raise PCMethodError('Cannot produce Performance Check report: No intervals found.')

        fig_list = []
        fig_list.extend(self.plot_cover())
        fig_list.extend(self.plot_bars())
        fig_list.extend(self.plot_shadow_and_intervals())

        # Add square and time plots, in plant / array order
        squares = self.plot_square(kwargs.get('square_axis_range'))
        times = self.plot_time(kwargs.get('y_ratio_limits'))
        squares_and_times = [v for pair in zip(squares, times) for v in pair]
        fig_list.extend(squares_and_times)

        fig_list.extend(self.plot_plant_overview())
        fig_list.extend(self.plot_collector_overview())
        fig_list.extend(self.plot_data_overview())
        fig_list.extend(self.plot_symbols_overview())

        if self.settings.with_interval_plots:
            fig_list.extend(self.plot_intervals(kwargs.get('axes_limits_interval_plots')))

        return fig_list

    def plot_cover(self,
                   ) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_cover` function.
        """
        if self.no_output():
            return None

        # Plot
        fig, params = pu.prepare_figure(settings=self.settings, suppress_footer=True)

        # Title
        box_title = pu.box_title(METHOD_DESCRIPTION,  # 'Power Check according to ISO 24194',
                                 fontsize=plt.rcParams['figure.titlesize'] + 3)

        # ISO Text
        textprops = dict(size=params['font_size_text'], linespacing=pu.DEFAULTS.linespacing_text)
        txt_iso = (
            f'This report is based on {pu.ASSETS.iso_string} "Solar energy — Collector fields — Check of performance".\n'
            f'Report generated with SunPeek: {pu.ASSETS.sunpeek_url}'
            # f'Report generated with the FOSS software SunPeek: {pu.sunpeek_url}'
        )

        # Plant Text
        p = self.pc_output.plant
        txt_plant = OrderedDict([
            ('Plant name', p.name),
            ('Plant owner', p.owner),
            ('Included arrays', f'{", ".join([ao.array.name for ao in self.pc_output.array_output])}'),
        ])
        txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
        txt_plant['Measuring period'] = (
            f'{pu.utc_str(self.pc_output.datetime_eval_start, p.tz_data)} to '
            f'{pu.utc_str(self.pc_output.datetime_eval_end, p.tz_data)}')
        box_plant = pu.dict_to_box(txt_plant, textprops=textprops)

        # Method Text
        txt_method = OrderedDict([
            ('Report date', f'{pendulum.now().to_date_string()}' if self.settings.include_creation_date else ''),
            ('Software version', f'SunPeek version {pu.sunpeek_version}'),
            ('Algorithm details', self.algorithm_details()),
            # ('Algorithm details', (
            #     f'Formula: {self.pc_output.formula}. '
            #     f'Wind: {"Used" if self.pc_output.wind_used else "Not used"}. '
            #     f'Mode: {self.pc_output.evaluation_mode}.')),
        ])
        box_method = pu.dict_to_box(txt_method, textprops=textprops)
        # Include accuracy_level? Only once it is included in web-ui.

        box_main = VPacker(children=[
            box_plant,
            box_method,
            TextArea(txt_iso, textprops=textprops),
        ], pad=0, sep=pu.DEFAULTS.sep_minor)

        # Logo
        box_logo = OffsetImage(pu.get_logo(pu.ASSETS.logo_path), zoom=0.08)
        box_logo.set_url(pu.ASSETS.sunpeek_url)

        # Place objects
        box = VPacker(children=[box_title,
                                box_main,
                                box_logo,
                                ], pad=0, sep=pu.DEFAULTS.sep_huge)

        artist = pu.annotation_bbox(box, xy=(0.15, 0.8))
        fig.add_artist(artist)

        return [fig]

    def plot_bars(self) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_bars` function.
        """
        if self.no_output():
            return None

        # Data to plot
        data = dict(
            tp_sp_estimated_safety=np.mean(self.pc_output.plant_output.tp_sp_estimated_safety.magnitude),
            tp_sp_measured=np.mean(self.pc_output.plant_output.tp_sp_measured.magnitude),
            min_intervals_ok=self.pc_output.plant_output.n_intervals >= self.pc_output.settings[
                'min_intervals_in_output'],
        )
        data['tp_ratio'] = data['tp_sp_measured'] / data['tp_sp_estimated_safety']

        # Plot
        fig, params = pu.prepare_figure(settings=self.settings)

        # Title
        box = VPacker(children=[pu.box_title(METHOD_DESCRIPTION)],  # 'Power Check ISO 24194')],
                      pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)
        title_artist = artist  # saved for use further down

        # Text on top of axes
        textprops = dict(size=pu.DEFAULTS.fontsize_text, linespacing=pu.DEFAULTS.linespacing_text,
                         family=params['font_family'])
        txt_plant = OrderedDict([
            ('Plant', self.pc_output.plant.name),
            ('Included arrays', f'{", ".join([ao.array.name for ao in self.pc_output.array_output])}'),
        ])
        txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
        box_component = pu.dict_to_box(txt_plant, textprops=textprops)

        # Text above plot
        box_check = TextArea(f'Power Check {"not " if data["tp_ratio"] < 1 else ""}fulfilled:',
                             textprops=dict(weight='bold', size=params['font_size_text']))

        textprops = dict(size=params['font_size_text'], linespacing=pu.DEFAULTS.linespacing_text)
        box_note = TextArea((f'Ratio measured / estimated power = {float(data["tp_ratio"]):.1%}'
                             f'\nThis takes a combined safety factor '
                             r'$f_{safe} = '
                             rf'{float(self.pc_output.settings["safety_combined"]):.2}$ into account.'
                             ), textprops=textprops)
        box = VPacker(children=[box_component, box_check, box_note],
                      pad=0, sep=pu.DEFAULTS.sep_minor)
        artist = pu.annotation_bbox(box, xy=pu.get_xy_below(artist, vsep=pu.DEFAULTS.sep_major))
        fig.add_artist(artist)

        # Bars plot
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_huge, bottom=0.45)
        ax = fig.add_axes(rect)

        bar_labels = [f'Average estimated power, '
                      r'with $f_{safe}$',
                      'Average power measured']
        bar_data = [data['tp_sp_estimated_safety'], data['tp_sp_measured']]
        bar_colors = [pu.COLORS.gray, pu.COLORS.red]
        data_tips = [f'{d:.1f} W/m²' for d in bar_data]
        ax.barh(bar_labels, bar_data, color=bar_colors, height=0.5, zorder=2, alpha=1)

        ax.set_ylim([-0.4, 1.4])
        ax.set_xlabel('Specific thermal power [W/m²]', ha='center')
        ax.grid(axis='x')
        ax.set_axisbelow('line')

        # Place y axis labels inside axes
        ax.set_yticks([])
        for y, label in enumerate(bar_labels):
            ab = AnnotationBbox(
                TextArea(label, textprops={'fontsize': params['font_size_text'], 'va': 'baseline'}),
                xy=(0, y), xycoords='data',
                xybox=(10, 0), boxcoords='offset points', box_alignment=(0, 0.5),
                pad=0, zorder=10)
            ab.patch.set_boxstyle('round,pad=0.5')
            ab.patch.set_edgecolor(pu.COLORS.almost_black)
            ab.patch.set_alpha(0.8)
            ax.add_artist(ab)

        # Add data-tip text at the right end of the bars
        txt = []
        for i, tip in enumerate(data_tips):
            txt.append(ax.text(bar_data[i] * 1.01, i, tip, ha='left', va='center',
                               size=plt.rcParams['axes.labelsize']))
        # Adjust xlims to accommodate for datatip texts
        plt.draw()  # Needed because matplotlib doesn't know how big the text is without drawing...
        bb = [t.get_window_extent() for t in txt]
        max_data = [ax.transData.inverted().transform(b.max) for b in bb]
        ax.set_xlim([0, max([md[0] for md in max_data])])
        # Include at least next minor tick
        minor_tick = pd.Series(ax.get_xticks(minor=True)).diff()[1]
        ax.set_xlim([0, np.ceil(ax.get_xlim()[1] / minor_tick) * minor_tick])

        # Text at bottom: Guarantee fulfilled statement
        # plant_name = '<anonymized>' if self.settings.anonymize else self.pc_output.plant.name
        tz = self.pc_output.plant.tz_data
        # array_names = [f'"{ao.array.name}"' for ao in self.pc_output.array_output]
        box_plant = TextArea((
            f'The minimum number of intervals ({self.pc_output.settings["min_intervals_in_output"]}, '
            f'defined in {pu.ASSETS.iso_string}) '
            f'has {"" if data["min_intervals_ok"] else "not "}been reached: '
            f'n={self.pc_output.plant_output.n_intervals} intervals found, each '
            f'{pendulum.duration(seconds=self.pc_output.settings["interval_length"].total_seconds()).in_words(locale="en")}'
            f' long.'
            f'\nData from {pu.utc_str(self.pc_output.datetime_eval_start, tz)} '
            f'to {pu.utc_str(self.pc_output.datetime_eval_end, tz)}.'
        ), textprops=textprops)
        box_details = TextArea((f'{METHOD_DESCRIPTION}\n'  # f'Power Check according to {pu.iso_string}.\n'
                                f'Algorithm details: {self.algorithm_details()}'
                                # f'Formula: {self.pc_output.formula}. '
                                # f'Wind: {"Used" if self.pc_output.wind_used else "Not used"}. '
                                # f'Mode: {self.pc_output.evaluation_mode}. '
                                ), textprops=textprops)

        box = VPacker(children=[pu.box_title('Notes', fontsize=params['font_size_text']),
                                box_plant,
                                box_details
                                ], pad=0, sep=pu.DEFAULTS.sep_minor)
        xy = pu.get_xy_below(ax, vsep=50)
        xy_title = pu.get_xy_below(title_artist)
        artist = pu.annotation_bbox(box, xy=(xy_title[0], xy[1]))
        # artist = pu.annotation_bbox(box, xy=pu.get_xy_below(ax, vsep=50))
        ax.add_artist(artist)

        return [fig]

    def plot_shadow_and_intervals(self
                                  ) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_shadow_and_intervals` function.
        """
        if self.no_output():
            return None

        # Data to plot
        p = self.pc_output.plant
        s = pd.Series(data=True, index=p.time_index)
        for ao in self.pc_output.array_output:
            s2 = ao.array.is_shadowed.data.astype(float)
            s = (s & s2.astype(bool)).where(~pd.isna(s2), np.nan)
        df = (1 - s.astype(float)).to_frame(name='not_shadowed')
        is_na = df['not_shadowed'].isna()

        df['no_data'] = is_na.astype(float)
        df['sun_above_horizon'] = (p.sun_apparent_elevation.data > 0).astype(float)
        df.loc[is_na, 'sun_above_horizon'] = np.nan

        df['no_pc_interval'] = 1.0
        po = self.pc_output.plant_output
        for i_start, i_end in zip(po.datetime_intervals_start, po.datetime_intervals_end):
            df.loc[i_start:i_end, 'no_pc_interval'] = 0.0

        # day_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq="1D").date
        # day_index = pd.Series(pd.date_range(start=df.index.min(), end=df.index.max(), freq="1D")).dt.date
        day_index = [ts.date() for ts in pd.date_range(start=df.index.min(), end=df.index.max(), freq="1D")]
        minute_of_day = 60 * df.index.hour + df.index.minute

        def pivoting(column):
            pivoted = pd.pivot_table(df, values=column, index=df.index.date, columns=minute_of_day)
            pivoted = pivoted.reindex(day_index)
            return pivoted.transpose().iloc[::-1]

        # Plot
        fig, params = pu.prepare_figure(settings=self.settings)

        # Text on top
        total_duration = pendulum.duration(seconds=self.pc_output.plant_output.n_intervals *
                                                   self.pc_output.settings["interval_length"].total_seconds())
        box_info = TextArea((
            f'n={self.pc_output.plant_output.n_intervals} intervals, each '
            f'{pendulum.duration(seconds=self.pc_output.settings["interval_length"].total_seconds()).in_words(locale="en")}'
            f' long. Total interval duration: '
            f'{total_duration.in_hours()} hours {total_duration.in_minutes() % 60} minutes.\n'
            f'Algorithm details: {self.algorithm_details()}'
        ), textprops=dict(size=params['font_size_text']))
        box = VPacker(children=[pu.box_title('Intervals used for Power Check'),
                                box_info,
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Shadow Plot
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_huge, bottom=pu.DEFAULTS.y_bottom)
        ax = fig.add_axes(rect)

        colors = dict(
            horizon=pu.COLORS.very_dark_gray.value,
            shadowed=pu.COLORS.dark_gray,
            white=pu.COLORS.white,
            pc=pu.COLORS.red,
            missing=pu.COLORS.missing_data,
        )
        ax.set_facecolor(pu.COLORS.missing_data)
        im_kwargs = dict(aspect='auto', interpolation='none',
                         extent=[mdates.date2num(day_index[0]), mdates.date2num(day_index[-1]), 0, 24])
        ax.imshow(pivoting('no_data'),
                  cmap=LinearSegmentedColormap.from_list('no_data',
                                                         [str(colors['white']), 'none']), **im_kwargs)
        ax.imshow(pivoting('not_shadowed'),
                  cmap=LinearSegmentedColormap.from_list('shadowed',
                                                         [str(colors['shadowed']), 'none']), **im_kwargs)
        ax.imshow(pivoting('sun_above_horizon'),
                  cmap=LinearSegmentedColormap.from_list('sun',
                                                         [str(colors['horizon']), 'none']), **im_kwargs)
        ax.imshow(pivoting('no_pc_interval'),
                  cmap=LinearSegmentedColormap.from_list('pc',
                                                         [str(colors['pc']), 'none']), **im_kwargs)

        ax.grid(True)
        ax.set_axisbelow('line')

        ax.legend(loc='upper right', handles=[
            mpatches.Patch(facecolor=str(colors['horizon']), label='Sun below horizon'),
            mpatches.Patch(facecolor=str(colors['shadowed']), label='Arrays shadowed'),
            mpatches.Patch(facecolor=str(colors['missing']), label='Missing data'),
            mpatches.Patch(facecolor=str(colors['pc']), label='Performance Check intervals'),
        ])

        # Axis formatting
        locator = mdates.AutoDateLocator(tz=p.tz_data)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        # ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator, show_offset=False, tz=p.tz_data))
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator, tz=p.tz_data))
        # tz = self.pc_output.plant.tz_data
        # ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(locator, tz=p.tz_data))

        ax.set_yticks([0, 6, 12, 18, 24])
        ax.set_yticklabels(["0:00", "6:00", "12:00", "18:00", "24:00"])
        utc_str = f'(UTC{int(df.index[0].utcoffset().total_seconds() / 3600):+0})'
        ax.set_ylabel(f'Time of day {utc_str}')

        return [fig]

    def plot_square(self,
                    square_axis_range: Optional[List] = None,
                    ) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_square` function.
        """
        if self.no_output():
            return None

        axis_range = square_axis_range or [0, 800]

        # Plant plot
        data = dict(
            tp_sp_measured=self.pc_output.plant_output.tp_sp_measured.magnitude,
            tp_sp_estimated_safety=self.pc_output.plant_output.tp_sp_estimated_safety.magnitude,
            tp_sp_estimated=self.pc_output.plant_output.tp_sp_estimated.magnitude,
        )

        # Text on top of axes
        _, params = pu.prepare_figure(settings=self.settings)
        textprops = dict(size=pu.DEFAULTS.fontsize_text, linespacing=pu.DEFAULTS.linespacing_text,
                         family=params['font_family'])
        txt_plant = OrderedDict([
            ('Plant', self.pc_output.plant.name),
            ('Included arrays', f'{", ".join([ao.array.name for ao in self.pc_output.array_output])}'),
        ])
        txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
        box_component = pu.dict_to_box(txt_plant, textprops=textprops)

        fig_list = [self._fig_square(data, box_component, axis_range, pu.COLORS.red)]

        if len(self.pc_output.array_output) == 1:
            return fig_list

        # Array plots
        for ao in self.pc_output.array_output:
            a = ao.array
            has_tp = a.tp is not None and not a.tp.data.isna().all()
            if not has_tp:
                continue

            data = dict(
                # Plot ratio against midpoint of intervals
                tp_sp_measured=ao.tp_sp_measured.magnitude,
                tp_sp_estimated_safety=ao.tp_sp_estimated_safety.magnitude,
                tp_sp_estimated=ao.tp_sp_estimated.magnitude,
            )

            # Text on top of axes
            _, params = pu.prepare_figure(settings=self.settings)
            textprops = dict(size=pu.DEFAULTS.fontsize_text, linespacing=pu.DEFAULTS.linespacing_text,
                             family=params['font_family'])
            txt_plant = OrderedDict([
                ('Plant', self.pc_output.plant.name),
                ('Included array', a.name),
            ])
            txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
            box_component = pu.dict_to_box(txt_plant, textprops=textprops)

            fig_list.append(self._fig_square(data, box_component, axis_range, pu.COLORS.blue))

        return fig_list

    def _fig_square(self,
                    data: dict,
                    box_top: matplotlib.offsetbox.OffsetBox,
                    axis_range: List,
                    color: str,
                    ) -> matplotlib.figure.Figure:
        """Create one square figure, given data for array or plant.
        """
        fig, params = pu.prepare_figure(settings=self.settings)

        # Title
        box = VPacker(children=[pu.box_title('Thermal Power Output: Measured vs. Estimated'),
                                box_top],
                      pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Plot
        def _plot_ax(ax_, y_estimated, x_label, title):
            """Plot one of the 2 square axes, either the left or right one.
            """
            ax_.scatter(
                y_estimated,
                data['tp_sp_measured'],
                s=pu.DEFAULTS.marker_size_scatter,
                alpha=pu.DEFAULTS.marker_alpha,
                facecolors=color,
                edgecolors=color,
                zorder=3,
            )
            # Bisection line
            ax_.plot(axis_range, axis_range, linestyle='-',
                     color=pu.COLORS.dark_gray, linewidth=pu.DEFAULTS.linewidth_thin, zorder=1)
            ax_.grid(True)
            ax_.set_axisbelow('line')
            ax_.set_aspect('equal')
            ax_.set_xlim(axis_range)
            ax_.set_ylim(axis_range)
            ax_.set_yticks(ax_.get_xticks())
            ax_.set_xlabel(x_label)
            ax_.set_ylabel('Measured power [W/m²]')
            ax_.set_title(title, loc='center', pad=pu.DEFAULTS.sep_axestitle)

        # Create the 2 axes and plot
        ax, ax_safe = fig.subplots(1, 2)
        x, y = pu.get_xy_below(artist, vsep=pu.DEFAULTS.sep_major)
        plt.subplots_adjust(left=x, top=y, bottom=0.22, right=pu.DEFAULTS.x_right, wspace=0.35)

        _plot_ax(ax, y_estimated=data['tp_sp_estimated'],
                 x_label='Estimated power [W/m²]',
                 title='Without safety factor')
        _plot_ax(ax_safe, y_estimated=data['tp_sp_estimated_safety'],
                 x_label=r'Estimated power [W/m²], with $f_{safe}$',
                 title=f'With safety factor '
                       r'$f_{safe} = '
                       rf'{float(self.pc_output.settings["safety_combined"]):.2}$')

        # Heading: Notes
        box_note = TextArea((f'Each dot in the plots is the average thermal power output of a '
                             f'{pendulum.duration(seconds=self.pc_output.settings["interval_length"].total_seconds()).in_words(locale="en")}'
                             f' interval.\n'
                             f'The left plot is based on estimated and measured data without safety factor. '
                             f'The right plot takes the combined safety factor '
                             r'$f_{safe} = '
                             rf'{float(self.pc_output.settings["safety_combined"]):.2}$'
                             f' into account.\n'
                             f'Algorithm details: {self.algorithm_details()}'
                             ), textprops=dict(weight='normal', size=params['font_size_text']))
        box = VPacker(children=[pu.box_title('Notes', fontsize=params['font_size_text']),
                                box_note,
                                ], pad=0, sep=pu.DEFAULTS.sep_minor)
        # artist = pu.annotation_bbox(box, xy=pu.get_xy_below(ax, vsep=pu.DEFAULTS.sep_huge))
        artist = pu.annotation_bbox(box, xy=pu.get_xy_below(ax, vsep=50))
        fig.add_artist(artist)

        return fig

    def plot_time(self,
                  y_ratio_limits: Optional[List] = None,
                  ) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_time` function.
        """
        if self.no_output():
            return None

        # Plot: Plant
        time_display = self.pc_output.plant_output.datetime_intervals_start + 0.5 * self.pc_output.settings[
            'interval_length']
        data = dict(
            # Plot ratio against midpoint of intervals
            tp_sp_measured=self.pc_output.plant_output.tp_sp_measured.magnitude,
            tp_sp_estimated_safety=self.pc_output.plant_output.tp_sp_estimated_safety.magnitude,
            tp_sp_estimated=self.pc_output.plant_output.tp_sp_estimated.magnitude,
        )

        # Text on top of axes
        _, params = pu.prepare_figure(settings=self.settings)
        textprops = dict(size=pu.DEFAULTS.fontsize_text, linespacing=pu.DEFAULTS.linespacing_text,
                         family=params['font_family'])
        txt_plant = OrderedDict([
            ('Plant', self.pc_output.plant.name),
            ('Included arrays', f'{", ".join([ao.array.name for ao in self.pc_output.array_output])}'),
            ('Algorithm details', self.algorithm_details()),
        ])
        txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
        box_component = pu.dict_to_box(txt_plant, textprops=textprops)

        fig_list = [self._fig_time(data, time_display, box_component, y_ratio_limits, pu.COLORS.red)]

        if len(self.pc_output.array_output) == 1:
            return fig_list

        # Array plots
        for ao in self.pc_output.array_output:
            a = ao.array
            has_tp = a.tp is not None and not a.tp.data.isna().all()
            if not has_tp:
                continue

            data = dict(
                # Plot ratio against midpoint of intervals
                tp_sp_measured=ao.tp_sp_measured.magnitude,
                tp_sp_estimated_safety=ao.tp_sp_estimated_safety.magnitude,
                tp_sp_estimated=ao.tp_sp_estimated.magnitude,
            )

            # Text on top of axes
            textprops = dict(size=pu.DEFAULTS.fontsize_text, linespacing=pu.DEFAULTS.linespacing_text)
            txt_plant = OrderedDict([
                ('Plant', self.pc_output.plant.name),
                ('Array', a.name),
            ])
            txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)
            box_component = pu.dict_to_box(txt_plant, textprops=textprops)

            fig_list.append(self._fig_time(data, time_display, box_component, y_ratio_limits, pu.COLORS.blue))

        return fig_list

    def _fig_time(self,
                  data: dict,
                  time_display,
                  box_top: matplotlib.offsetbox.OffsetBox,
                  y_limits: List,
                  color: str,
                  ) -> matplotlib.figure.Figure:
        # Determine y axis limits
        ratio = data['tp_sp_measured'] / data['tp_sp_estimated']
        ratio_safety = data['tp_sp_measured'] / data['tp_sp_estimated_safety']
        if y_limits is None:
            y_min = min(0.8, np.floor(min(ratio) * 10) / 10)
            y_max = max(1.2, np.ceil(max(ratio_safety) * 10) / 10)
            y_limits = [y_min, y_max]

        fig, params = pu.prepare_figure(settings=self.settings)

        # Title
        box = VPacker(children=[pu.box_title('Power Output over Time: Measured vs. Estimated'),
                                box_top],
                      pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Plot
        def _plot_ax(ax_, ratio, y_label, title):
            """Plot one of the 2 time axes, either the top or bottom one.
            """
            ax_.scatter(x=time_display, y=ratio,
                        s=pu.DEFAULTS.marker_size_scatter,
                        alpha=pu.DEFAULTS.marker_alpha,
                        facecolors=color,
                        edgecolors=color,
                        zorder=3,
                        )
            # Horizontal line at 100%
            ax_.axhline(y=1, linestyle='-',
                        linewidth=pu.DEFAULTS.linewidth_thin, color=pu.COLORS.dark_gray, zorder=1)
            # Trend line
            # Currently not being displayed correctly, see https://gitlab.com/sunpeek/sunpeek/-/issues/562
            # rm = pd.Series(data=ratio, index=time_display) \
            #     .rolling(dt.timedelta(days=45), min_periods=20, center=True, closed='both').median()
            # ax_.plot(rm.index, rm, color=pu.COLORS.gray, linestyle='-', linewidth=3)
            # Style
            ax_.grid(True)
            ax_.set_axisbelow('line')
            ax_.set_ylim(y_limits)
            ax_.set_ylabel(y_label)
            ax_.set_title(title, pad=pu.DEFAULTS.sep_axestitle)
            # X axis style
            tz = self.pc_output.plant.tz_data
            ax_.xaxis_date(tz)
            ax_.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
            ax_.set_xlim(pd.to_datetime(self.pc_output.datetime_eval_start).tz_convert(tz),
                         pd.to_datetime(self.pc_output.datetime_eval_end).tz_convert(tz), auto=None)
            ax_.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax_.xaxis.get_major_locator(), tz=tz))

        # Create the 2 axes and plot
        ax, ax_safe = fig.subplots(2, 1)
        x, y = pu.get_xy_below(artist, vsep=pu.DEFAULTS.sep_huge)
        plt.subplots_adjust(left=x, top=y, bottom=pu.DEFAULTS.y_bottom, right=pu.DEFAULTS.x_right,
                            hspace=0.4)

        _plot_ax(ax, ratio=ratio,
                 y_label=f'Ratio measured vs. estimated power\n',
                 title='Without safety factor')
        _plot_ax(ax_safe, ratio=ratio_safety,
                 y_label=f'Ratio measured vs. estimated power,\n'
                         r'with $f_{safe}$',
                 title=f'With safety factor '
                       r'$f_{safe} = '
                       rf'{float(self.pc_output.settings["safety_combined"]):.2}$')

        return fig

    def plot_plant_overview(self) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_plant_overview` function.
        """
        if self.no_output():
            return None

        # Data to plot: Plant info
        p = self.pc_output.plant
        txt_plant = OrderedDict([
            ('Plant name', p.name),
            ('Plant owner', p.owner),
            ('Plant location', p.location_name),
            ('Plant latitude', f'{p.latitude.m:.2f}°'),
            ('Plant longitude', f'{p.longitude.m:.2f}°'),
            ('Plant elevation', f'{p.elevation:.0f~P}'),
        ])
        txt_plant = pu.anonymize(txt_plant, do_anonymize=self.settings.anonymize)

        # Data to plot: Collector arrays
        format_arrays = {
            'Array name': pu.TableColumnFormat(width=2),
            'Collector name': pu.TableColumnFormat(width=1.5),
            'Manufacturer': pu.TableColumnFormat(width=1.6),
            'Gross area': pu.TableColumnFormat(unit_str=r'$m^2$', ha='right'),
            'Tilt': pu.TableColumnFormat(ha='right', width=0.9),
            'Azimuth': pu.TableColumnFormat(ha='right', width=0.9),
            'Row spacing': pu.TableColumnFormat(unit_str='m', ha='right', width=1.1),
        }
        tbl_rows = []
        for ao in self.pc_output.array_output:
            a = ao.array
            tbl_rows.append({
                'Array name': a.name,
                'Collector name': a.collector.product_name,
                'Manufacturer': a.collector.manufacturer_name,
                'Gross area': f'{a.area_gr.m:.0f}',
                'Tilt': f'{a.tilt.m:.1f}°',
                'Azimuth': f'{a.azim.m:.1f}°',
                'Row spacing': f'{a.row_spacing.m:.1f}',
            })
        df_arrays = pd.DataFrame(tbl_rows)

        # Plot Plant details
        fig, params = pu.prepare_figure(settings=self.settings)
        box_plant = pu.dict_to_box(txt_plant, textprops=dict(size=params['font_size_text'],
                                                             linespacing=pu.DEFAULTS.linespacing_text))
        box = VPacker(children=[pu.box_title('Plant Overview'),
                                box_plant,
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Plot Heading: Arrays
        box = VPacker(children=[pu.box_title('Collector Arrays', fontsize=params['font_size_text']),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.get_xy_below(artist, vsep=pu.DEFAULTS.sep_huge))
        fig.add_artist(artist)

        # Plot Table: Arrays
        # Note: This assumes that all arrays fit on one page. This is valid up to approx. 10 arrays in a plant.
        # For more arrays, see the approach taken e.g. in plot_data_overview()
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_minor,
                                      bottom=pu.DEFAULTS.y_bottom_extreme,
                                      right=pu.DEFAULTS.x_right)
        ax = fig.add_axes(rect)
        pu.add_table(ax, df_arrays, format_arrays, cell_vspace_header=2.2, vpad_header=4)

        return [fig]

    def plot_collector_overview(self) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_collector_overview` function.
        """
        if self.no_output():
            return None

        # Data to plot: unique Collectors
        p_width = 0.8
        d = pu.STR_DEFAULTS.dimensionless_unit
        format_collectors = {
            'Collector name': pu.TableColumnFormat(width=1.6),
            'Manufacturer': pu.TableColumnFormat(width=1.6),
            'License number': pu.TableColumnFormat(header_str='License\nnumber', width=1.2),
            'Date issued': pu.TableColumnFormat(header_str='Date\nissued', width=0.8),
            'Gross area': pu.TableColumnFormat(unit_str=r'$m^2$', ha='right', header_str='Gross\narea', width=p_width),
            'a1': pu.TableColumnFormat(ha='right', unit_str=r'$\dfrac{W}{m^2 K}$', header_str=r'$a_1$', width=p_width),
            'a2': pu.TableColumnFormat(ha='right', unit_str=r'$\dfrac{W}{m^2 K^2}$', header_str=r'$a_2$',
                                       width=p_width),
            'a5': pu.TableColumnFormat(ha='right', unit_str=r'$\dfrac{J}{m^2 K}$', header_str=r'$a_5$', width=p_width),
            'a8': pu.TableColumnFormat(ha='right', unit_str=r'$\dfrac{W}{m^2 K^4}$', header_str=r'$a_8$',
                                       width=p_width),
            'eta0b': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$\eta_b$', width=p_width),
            'eta0hem': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$\eta_{hem}$', width=p_width),
            'kd': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$K_d$', width=p_width),
            'f_prime': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$F\prime$', width=p_width),
            # 'f_prime_c': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$F\prime_c$', width=p_width),
            'C_R': pu.TableColumnFormat(ha='right', unit_str=d, header_str=r'$C_R$', width=p_width),
        }
        collectors = [ao.array.collector for ao in self.pc_output.array_output]
        unique_collectors = list({c.name: c for c in collectors}.values())
        tbl_rows = []
        for c in unique_collectors:
            tbl_rows.append({
                'Collector name': pu.str_or_na(c.product_name),
                'Manufacturer': pu.str_or_na(c.manufacturer_name),
                'License number': pu.str_or_na(c.licence_number),
                'Date issued': f'{c.certificate_date_issued:{pu.STR_DEFAULTS.format_date}}'
                if c.certificate_date_issued else pu.STR_DEFAULTS.na_str,
                'Gross area': f'{c.area_gr.to("m**2").m:.2f}',
                'a1': pu.str_or_na(c.a1, unit="W m**-2 K**-1", fmt='.2f'),
                'a2': pu.str_or_na(c.a2, unit="W m**-2 K**-2", fmt='.3f'),
                'a5': pu.str_or_na(c.a5, unit="J m**-2 K**-1", fmt='.0f'),
                'a8': pu.str_or_na(c.a8, unit="W m**-2 K**-4", fmt='.2e'),
                'eta0b': f'{c.eta0b.to("").m:.3f}',
                'eta0hem': f'{c.eta0hem.to("").m:.3f}',
                'kd': pu.str_or_na(c.kd, unit="", fmt='.2f'),
                'f_prime': pu.str_or_na(c.f_prime, unit="", fmt='.2f'),
                'C_R': pu.str_or_na(c.concentration_ratio, unit="", fmt='.1f'),
            })
        df_collectors = pd.DataFrame(tbl_rows)

        # Data to plot: IAMs of unique collectors
        angles = np.linspace(10, 90, 9)
        angle_names = {a: f'{a:.0f}°' for a in angles}
        f_iams = {k: pu.TableColumnFormat(header_str=v, ha='right', width=0.6) for k, v in angle_names.items()}
        f_iams['Collector name'] = pu.TableColumnFormat(width=2.2)
        f_iams['trans_long'] = pu.TableColumnFormat(header_str='IAM type', width=1.)
        f_iams['symbol'] = pu.TableColumnFormat(header_str='', width=0.7)

        tbl_rows = []
        for c in unique_collectors:
            for iam_type in ['Transversal', 'Longitudinal']:
                row = {'Collector name': c.product_name if iam_type == 'Transversal' else '',
                       'trans_long': iam_type,
                       'symbol': r'$K_b(\theta_T)$' if iam_type == 'Transversal' else r'$K_b(\theta_L)$'}
                row.update(
                    {a: f'{c.iam_method.get_iam(aoi=Q(a, "deg"), azimuth_diff=Q(0, "deg"))[0].m:.2f}' for a in angles})
                tbl_rows.append(row)
        df_iams = pd.DataFrame(tbl_rows)

        # Plot Title
        fig, params = pu.prepare_figure(settings=self.settings)
        box = VPacker(children=[pu.box_title('Collector Overview'),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Plot Heading: Collectors
        box = VPacker(children=[pu.box_title('Collectors', fontsize=params['font_size_text']),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.get_xy_below(artist))
        fig.add_artist(artist)

        # Plot Table: Collectors
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_minor,
                                      # bottom=pu.DEFAULTS.y_bottom,
                                      right=pu.DEFAULTS.x_right_extreme)
        ax = fig.add_axes(rect)
        pu.add_table(ax, df_collectors, format_collectors, cell_vspace_header=2.8, vpad_header=3)
        artist = ax

        # Plot Heading: IAMs
        box = VPacker(children=[pu.box_title('Incidence Angle Modifiers (IAM)', fontsize=params['font_size_text']),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.get_xy_below(artist, vsep=pu.DEFAULTS.sep_huge))
        fig.add_artist(artist)

        # Plot Table: IAMs
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_minor,
                                      bottom=pu.DEFAULTS.y_bottom_extreme,
                                      right=pu.DEFAULTS.x_right_extreme)
        ax = fig.add_axes(rect)
        pu.add_table(ax, df_iams, f_iams, vpad_header=5,
                     divider_lines=[n for n in range(2, 2 * len(unique_collectors)) if n % 2 == 0])

        return [fig]

    def plot_data_overview(self) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_data_overview` function.
        """
        if self.no_output():
            return None

        # Data to plot
        p_width = 0.8
        fontsize = pu.DEFAULTS.fontsize_table - 1
        # Using symbols used in ISO 24194.
        format_data = {
            'n': pu.TableColumnFormat(width=0.4, fontsize=fontsize),
            'Date': pu.TableColumnFormat(width=1.1, fontsize=fontsize),
            'Start': pu.TableColumnFormat(width=0.7, fontsize=fontsize),
            'End': pu.TableColumnFormat(width=0.5, fontsize=fontsize),
            'te_amb': pu.TableColumnFormat(header_str=r'$\vartheta_a$', unit_str=r'$°C$',
                                           fontsize=fontsize, ha='right', width=p_width),
            'te_in': pu.TableColumnFormat(header_str=r'$\vartheta_{in}$', unit_str=r'$°C$',
                                          fontsize=fontsize, ha='right', width=p_width),
            'te_out': pu.TableColumnFormat(header_str=r'$\vartheta_{out}$', unit_str=r'$°C$',
                                           fontsize=fontsize, ha='right', width=p_width),
            'te_op': pu.TableColumnFormat(header_str=r'$\vartheta_{op}$', unit_str=r'$°C$',
                                          fontsize=fontsize, ha='right', width=p_width),
            'te_op_deriv': pu.TableColumnFormat(header_str=r'$\vartheta\backprime_{op}$', unit_str=r'$K/h$',
                                                fontsize=fontsize, ha='right', width=p_width),
            'aoi': pu.TableColumnFormat(header_str=r'$\theta$', unit_str=r'°',
                                        fontsize=fontsize, ha='right', width=0.5),
            'iam_b': pu.TableColumnFormat(header_str=r'$K_b$', unit_str=pu.STR_DEFAULTS.dimensionless_unit,
                                          fontsize=fontsize, ha='right', width=p_width),
            'rd_gti': pu.TableColumnFormat(header_str=r'$G_{hem}$', unit_str=r'$\dfrac{W}{m^2}$',
                                           fontsize=fontsize, ha='right', width=p_width),
            'rd_bti': pu.TableColumnFormat(header_str=r'$G_{b}$', unit_str=r'$\dfrac{W}{m^2}$',
                                           fontsize=fontsize, ha='right', width=p_width),
            'rd_dti': pu.TableColumnFormat(header_str=r'$G_{d}$', unit_str=r'$\dfrac{W}{m^2}$',
                                           fontsize=fontsize, ha='right', width=p_width),
            've_wind': pu.TableColumnFormat(header_str=r'$u$', unit_str=r'$\dfrac{m}{s}$',
                                            fontsize=fontsize, ha='right', width=p_width),
            'tp_measured': pu.TableColumnFormat(header_str=r'$\.Q_{meas,sp}$', unit_str=r'$\dfrac{W}{m^2}$',
                                                fontsize=fontsize, ha='right', width=1),
            'tp_estimated_safety': pu.TableColumnFormat(header_str=r'$\.Q_{est,sp}*f_{safe}$',
                                                        unit_str=r'$\dfrac{W}{m^2}$',
                                                        fontsize=fontsize, ha='right', width=1),
            'tp_ratio': pu.TableColumnFormat(header_str=r'$\.Q$ ratio', unit_str='%',
                                             fontsize=fontsize, ha='right', width=p_width),
        }

        # Create data table for each array
        fig_list = []
        for ao in self.pc_output.array_output:
            a = ao.array
            has_tp = a.tp is not None and not a.tp.data.isna().all()
            tbl_rows = []
            for i in range(self.pc_output.plant_output.n_intervals):
                tbl_rows.append({
                    'n': i + 1,
                    'Date': f'{self.pc_output.plant_output.datetime_intervals_start[i]:{pu.STR_DEFAULTS.format_date}}',
                    'Start': f'{self.pc_output.plant_output.datetime_intervals_start[i]:{pu.STR_DEFAULTS.format_time}}',
                    'End': f'{self.pc_output.plant_output.datetime_intervals_end[i]:{pu.STR_DEFAULTS.format_time}}',
                    'te_amb': f'{ao.data.te_amb[i].to("degC").m:0.1f}',
                    'te_in': f'{ao.data.te_in[i].to("degC").m:0.1f}',
                    'te_out': f'{ao.data.te_out[i].to("degC").m:0.1f}',
                    'te_op': f'{ao.data.te_op[i].to("degC").m:0.1f}',
                    'te_op_deriv': f'{ao.data.te_op_deriv[i].to("K hour**-1").m:0.2f}',
                    'aoi': f'{ao.data.aoi[i].to("deg").m:0.0f}',
                    'iam_b': f'{ao.data.iam_b[i].to("").m:0.2f}',
                    'rd_gti': pu.str_or_na(ao.data.rd_gti, idx=i, unit="W m**-2", fmt='0.0f'),
                    'rd_bti': pu.str_or_na(ao.data.rd_bti, idx=i, unit="W m**-2", fmt='0.0f'),
                    'rd_dti': pu.str_or_na(ao.data.rd_dti, idx=i, unit="W m**-2", fmt='0.0f'),
                    've_wind': pu.str_or_na(ao.data.ve_wind, idx=i, unit="m s**-1", fmt='0.1f'),
                    'tp_measured': f'{ao.tp_sp_measured[i].to("W m**-2").m:0.0f}' if has_tp else pu.STR_DEFAULTS.na_str,
                    'tp_estimated_safety': f'{ao.tp_sp_estimated_safety[i].to("W m**-2").m:0.0f}',
                    'tp_ratio': f'{(ao.tp_sp_measured[i] / ao.tp_sp_estimated_safety[i]).to("percent").m:0.1f}' \
                    if has_tp else pu.STR_DEFAULTS.na_str,
                })
            df = pd.DataFrame(tbl_rows)

            # Plot Title
            fig, params = pu.prepare_figure(settings=self.settings)
            box_note = TextArea((f'Array: {ao.array.name}\n'
                                 f'Each table row shows the average values of a '
                                 f'{pendulum.duration(seconds=self.pc_output.settings["interval_length"].total_seconds()).in_words(locale="en")}'
                                 f' interval. The rightmost column takes a combined safety factor '
                                 r'$f_{safe} = '
                                 rf'{float(self.pc_output.settings["safety_combined"]):.2}$ into account.'
                                 ), textprops=dict(weight='normal', size=params['font_size_text']))
            box = VPacker(children=[pu.box_title('Data Points Considered'),
                                    box_note,
                                    ], pad=0, sep=pu.DEFAULTS.sep_major)
            artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
            fig.add_artist(artist)

            # Plot Data Table, potentially over multiple pages
            y_bottom = pu.DEFAULTS.y_bottom_extreme
            x_right = pu.DEFAULTS.x_right_extreme
            n_rows_plotted = [0]
            while np.sum(n_rows_plotted) < len(df):
                if len(n_rows_plotted) == 1:  # 1st page
                    rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_minor,
                                                  bottom=y_bottom, right=x_right)
                else:  # subsequent pages
                    xy = pu.DEFAULTS.xy_topleft
                    rect = (xy[0], y_bottom, x_right - xy[0], xy[1] - y_bottom)
                    fig, _ = pu.prepare_figure(settings=self.settings)
                fig_list.append(fig)
                ax = fig.add_axes(rect)
                df_ = df.loc[np.sum(n_rows_plotted):]
                n_rows_plotted.append(
                    pu.add_table(ax, df_, format_data, cell_vspace=1.9, cell_vspace_header=2.5, vpad_header=3,
                                 divider_lines=range(1, len(df_)))
                )

        return fig_list

    def plot_symbols_overview(self) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_symbols_overview` function.
        """
        if self.no_output():
            return None

        # Data to plot
        fontsize = pu.DEFAULTS.fontsize_table - 1
        format_symbols = {
            'Symbol': pu.TableColumnFormat(width=0.25, fontsize=fontsize),
            'Description': pu.TableColumnFormat(width=1.2, fontsize=fontsize),
            'Typical unit': pu.TableColumnFormat(width=0.3, fontsize=fontsize),
        }
        du = pu.STR_DEFAULTS.dimensionless_unit
        symbols = [
            # Latin
            [r'$a_1$', 'Linear heat loss coefficient', r'$\dfrac{W}{m^2 K}$'],
            [r'$a_2$', 'Quadratic heat loss coefficient', r'$\dfrac{W}{m^2 K^2}$'],
            [r'$a_5$', 'Effective thermal heat capacity', r'$\dfrac{J}{m^2 K}$'],
            [r'$a_8$', 'Radiative heat loss coefficient', r'$\dfrac{W}{m^2 K^4}$'],
            [r'$C_R$', 'Geometric concentration ratio', du],
            [r'$F\prime$',
             'Collector efficiency factor (ratio of heat transfer of fluid to absorber vs. fluid to ambient)', du],
            [r'$F\prime_c$',
             r'Constant collector efficiency factor (like $F\prime$, but neglecting $u_2$)', du],
            [r'$G_{hem}$', 'Hemispherical solar irradiance on the collector plane', r'$\dfrac{W}{m^2}$'],
            [r'$G_{b}$', 'Direct solar irradiance (beam irradiance) on the collector plane', r'$\dfrac{W}{m^2}$'],
            [r'$G_{d}$', 'Diffuse solar irradiance on the collector plane', r'$\dfrac{W}{m^2}$'],
            [r'$K_b$', 'Incidence angle for direct solar radiation', du],
            [r'$K_d$', 'Incidence angle modifier for diffuse solar radiation', du],
            [r'$\.Q_{meas,sp}$', r'Measured specific power output (per $m^2$ gross collector array area)',
             r'$\dfrac{W}{m^2}$'],
            [r'$\.Q_{est,sp}$', r'Estimated specific power output (per $m^2$ gross collector array area)',
             r'$\dfrac{W}{m^2}$'],
            [r'$u$', 'Surround air speed (wind velocity)', r'$\dfrac{m}{s}$'],
            # Greek
            [r'$\eta_b$', r'Collector efficiency based on beam irradiance $G_b$', du],
            [r'$\eta_{hem}$', r'Collector efficiency based on hemispherical irradiance $G_{hem}$', du],
            [r'$\theta$', 'Angle of incidence between the normal vector of the collector plane and the sun-beam vector',
             r'°'],
            [r'$\vartheta_a$', 'Ambient air temperature', r'$°C$'],
            [r'$\vartheta_{in}$', 'Collector array inlet temperature', r'$°C$'],
            [r'$\vartheta_{out}$', 'Collector array outlet temperature', r'$°C$'],
            [r'$\vartheta_{op}$', (f'Collector array operating temperature '
                                   r'$\vartheta_{op}=mean(\vartheta_{in}, \vartheta_{out})$'), r'$°C$'],
            [r'$\vartheta\backprime_{op}$', f'Derivative of the collector array operating temperature ', r'$K/h$'],
        ]
        tbl_rows = [{k: v for k, v in zip(format_symbols.keys(), s)} for s in symbols]
        df = pd.DataFrame(tbl_rows)

        # Plot Title
        fig, params = pu.prepare_figure(settings=self.settings)
        box = VPacker(children=[pu.box_title('Symbols'),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Plot Symbols Table
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_minor,
                                      # bottom=pu.DEFAULTS.y_bottom,
                                      right=0.8)
        ax = fig.add_axes(rect)
        pu.add_table(ax, df, format_symbols, cell_vspace=2.5, vpad_header=4,
                     divider_lines=range(1, len(tbl_rows)))

        return [fig]

    def plot_intervals(self,
                       axes_limits_interval_plots: dict = None,
                       ) -> Optional[List[matplotlib.figure.Figure]]:
        """See `plot_intervals` function.
        """
        if self.no_output():
            return None

        fig_list = []
        for i in range(self.pc_output.plant_output.n_intervals):
            for ao in self.pc_output.array_output:
                fig_list.append(
                    self._plot_single_interval(array_output=ao,
                                               interval_idx=i,
                                               axes_limits=axes_limits_interval_plots)
                )

        return fig_list

    def _plot_single_interval(self,
                              array_output: results.PCMethodOutputArray,
                              interval_idx: int,
                              axes_limits: dict = None,
                              ) -> matplotlib.figure.Figure:
        # Data to plot
        def _data(sensor, unit_str: str) -> pd.Series:
            return sensor.data.pint.to(unit_str).loc[interval_start:interval_end]

        a = array_output.array
        p = a.plant
        has_tp = a.tp is not None and not a.tp.data.isna().all()
        has_vf = a.vf is not None and not a.vf.data.isna().all()
        interval_start = self.pc_output.plant_output.datetime_intervals_start[interval_idx]
        interval_end = self.pc_output.plant_output.datetime_intervals_end[interval_idx]

        # Plot
        fig, params = pu.prepare_figure(settings=self.settings)
        ax_te, ax_tp, ax_rd, ax_vf = fig.subplots(4, sharex='all', height_ratios=[5, 4, 4, 2])

        # Text at top
        utc_str = lambda \
                d: f'{d:%Y-%m-%d %H:%M} (UTC{int(d.utcoffset().total_seconds() / 3600):+0})'
        array_text = f'Plant: {p.name}. Array: {a.name}. '
        interval_text = f'Interval #{interval_idx + 1}: {utc_str(interval_start)} to {utc_str(interval_end)}'

        textprops = dict(size=params['font_size_text'])
        box = VPacker(children=[pu.box_title('Measurement Data in Interval'),
                                HPacker(children=[TextArea(array_text, textprops=textprops),
                                                  TextArea(interval_text, textprops=textprops)])
                                ], pad=0, sep=pu.DEFAULTS.sep_minor)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        fig.subplots_adjust(left=pu.DEFAULTS.x_left, bottom=pu.DEFAULTS.y_bottom_extreme,
                            right=pu.DEFAULTS.x_right_extreme, top=pu.get_xy_below(artist)[1])
        # Temperatures
        ax_te.plot(_data(a.te_out, 'degC'), "-", label="Outlet temperature", color=pu.COLORS.red, zorder=2)
        ax_te.plot(_data(a.te_in, 'degC'), "-", label="Inlet temperature", color=pu.COLORS.blue, zorder=1.9)
        ax_te.plot(_data(p.te_amb, 'degC'), "-", label="Ambient temperature", color=pu.COLORS.yellow, zorder=1.8)

        # Thermal power(specific): measured and simulated
        # Averages: Horizontal Lines
        tp_sp_est = array_output.tp_sp_estimated[interval_idx].magnitude
        tp_sp_est_safety = array_output.tp_sp_estimated_safety[interval_idx].magnitude
        if has_tp:
            tp_sp_measured = _data(a.tp, 'W') / a.area_gr
            ax_tp.plot(tp_sp_measured, label="Measured power", color=pu.COLORS.almost_black, zorder=2)
            tp_sp_meas = array_output.tp_sp_measured[interval_idx].magnitude
            ax_tp.axhline(y=tp_sp_meas, label='Average measured power',
                          linewidth=0.75, color=pu.COLORS.red, zorder=1.5, linestyle=(5, (10, 3)))
            ax_tp.fill_between(tp_sp_measured.index, tp_sp_est_safety, tp_sp_est,
                               label=r'Estimated power, range with $f_{safe}$', zorder=1,
                               color=pu.COLORS.dark_gray, linewidth=plt.rcParams['grid.linewidth'], alpha=0.4)

        # Irradiance
        if a.rd_gti is not None:
            rd_g = _data(a.rd_gti, 'W m**-2')
            ax_rd.fill_between(rd_g.index, 0, rd_g, label="Global tilted irradiance", zorder=1,
                               color=pu.COLORS.yellow,
                               alpha=0.4,
                               )
        if a.rd_bti is not None:
            ax_rd.plot(_data(a.rd_bti, 'W m**-2'), label="Beam tilted irradiance", color=pu.COLORS.red, zorder=3)
        if a.rd_dti is not None:
            ax_rd.plot(_data(a.rd_dti, 'W m**-2'), label="Diffuse tilted irradiance", color=pu.COLORS.dark_gray,
                       zorder=2)

        # Specific volume flow
        vf_sp = None
        if has_vf:
            vf_sp = _data(a.vf, 'l hour**-1') / a.area_gr
            ax_vf.fill_between(vf_sp.index, 0, vf_sp, label="Specific volume flow",
                               color=pu.COLORS.gray, linewidth=plt.rcParams['grid.linewidth'], alpha=0.4)

        # Axes formatting (labels)
        ax_te.set_ylabel("Temperature [°C]")
        ax_tp.set_ylabel("Specific thermal\npower [W/m²]")
        ax_rd.set_ylabel("Irradiance\n[W/m²]")
        ax_vf.set_ylabel("Specific volume\nflow [l/m²h]")

        # Axes formatting (limits)
        axes_limits = {} if axes_limits is None else axes_limits
        te_max = axes_limits.get('te_max', max(100, np.ceil(_data(a.te_out, 'degC').astype(float).max())))
        rd_max = axes_limits.get('rd_max', 1250)
        tp_max = axes_limits.get('tp_max', 1000)
        vf_sp_max = axes_limits.get('vf_sp_max', max(20, np.ceil(vf_sp.astype(float).max())) if has_vf else 20)

        ax_te.set_ylim(0, te_max)
        ax_tp.set_ylim(0, tp_max)
        ax_rd.set_ylim(0, rd_max)
        ax_vf.set_ylim(0, vf_sp_max)

        # Axes formatting
        ax_names = ['(a) Temperatures',  # '(a) Temperatures collector array and ambient',
                    '(b) Thermal power',
                    '(c) Irradiance',
                    '(d) Volume flow']
        for ax_, ax_title in zip([ax_te, ax_tp, ax_rd, ax_vf], ax_names):
            leg = ax_.legend(loc="upper right")
            leg.set_zorder(3)
            ax_.set_title(ax_title, loc='center', pad=3)
            ax_.grid()
            ax_.set_axisbelow('line')

        # Layout
        ax_vf.set_xlim(interval_start, interval_end, auto=None)
        tz = p.tz_data
        ax_vf.xaxis_date(tz)
        ax_vf.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
        ax_vf.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        ax_vf.xaxis.set_major_formatter(mdates.DateFormatter("%#H:%M", tz=tz))
        ax_vf.tick_params(axis='x', pad=5)

        return fig

    def no_output(self) -> bool:
        msg = 'Nothing to plot, no Performance Check intervals found.'

        if self.pc_output is None:
            sp_logger.info(msg)
            return True

        if self.pc_output.plant_output.n_intervals == 0:  # type: ignore[union-attr]
            sp_logger.info(msg)
            return True

        return False

    def algorithm_details(self):
        mode = self.pc_output.evaluation_mode
        mode = mode if mode.isupper() else mode.capitalize()
        return (f'Formula: {self.pc_output.formula}. '
                f'Wind: {"Used" if self.pc_output.wind_used else "Not used"}. '
                f'Averaging mode: {mode}. ')
