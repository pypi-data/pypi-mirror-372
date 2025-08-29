"""
Implements Performance Check (PC) Method according to technical standard ISO 24194:2022.

HowTo
=====

To create instances, use
- ISO mode: PCMethod.from_method('ISO')
- Extended mode: PCMethod.from_method('Extended')

The entry-point method by the classes in this module is :method:`pc_method.run()`.
This is called by :fun:`run_performance_check` in the wrapper / the PC strategies.
Results: pc_method.get_results() returns a components.results.PCMethodOutput object.

See docstring in __init__ for more details.

Implementations
===============
PCMethodISO
-----------

The implementation variant that aligns as closely as possible to the ISO 24194 standard is in class PCMethodISO.
Create an analysis with PCMethod.from_method('ISO', **kwargs).

PCMethodExtended
----------------

Reasoning: Some of the data analysis recommendations described in the ISO standard apparently assume the use of Excel
or other spreadsheet based software. For instance, analysis is based on fixed 1-hourly that start at full hours. This
does not necessarily lead to the best / most useful results.

This software package implements an extended variant of the Performance Check method that overcomes some limitations of
the strictly fixed-hour variant described in ISO 24194.
This 'extended' implementation has a few slight but significant improvements in data analysis,
while sticking as closely as possible to the intentions and purpose of the ISO 24194 standard:
It tends to produce more and less noisy intervals in a Performance Check analysis. Numerically, comparable in range to
PCMethodISO in terms of measured vs expected power. The extended version tends to include more intervals that are
limit cases compared to the requirements stated in the ISO 24194, hence its results have somewhat higher generality.
By default, the extended implementation uses a 1-hour averaging, as described in ISO 24194. It can be set to a
different value. All other PCMethodExtended settings are the same as PCMethodISO.

First analysis validations on real-plant data confirmed that the PCMethodExtended variant reduces
noise in the analysis output and improves the regression between measured and estimated power, the main KPI of the PC
method.

Differences of PCMethodExtended over PCMethodISO in detail:
- Uses rolling resampling instead of fixed-hour resampling in PCMethodISO. Consequently, data intervals used for the
analysis (performance equations) are not restricted to start at full hours.
- Uses a minimum-noise (minimum relative standard deviation) criterion to select among overlapping interval candidates.
- Allows different interval lengths, not restricted to 1 hour.
- Minimum number of non-NaN data records per interval not restricted to 20.

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Lukas Feierl <l.feierl@solid.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

from abc import ABC, abstractmethod
import warnings
import datetime as dt
import pandas as pd
import numpy as np
from typing import Union, Optional
from statsmodels.formula import api as smf

from sunpeek.common.utils import sp_logger
from sunpeek.common.unit_uncertainty import Q
from sunpeek.components import Plant
import sunpeek.components.outputs_pc_method as results
from sunpeek.common.errors import PCMethodError
from sunpeek.components.helpers import AlgoCheckMode
from sunpeek.core_methods.pc_method import PCMethods, PCFormulae, PCAccuracyClasses, OutputUnits
from sunpeek.core_methods.pc_method.formula import Formula
from sunpeek.serializable_models import CoreMethodFeedback

# ------------------------------------------------------------------------------------
# PC Method parameters

METHOD_DESCRIPTION = 'Power Check according to ISO 24194:2022'

# Default values that appear in ISO 24194:
INTERVAL_LENGTH_ISO = dt.timedelta(hours=1)  # 1 hour = specified in ISO standard
MIN_INTERVALS_IN_OUTPUT = 20


# Safety factors, as discussed in https://gitlab.com/sunpeek/sunpeek/-/issues/323#note_1607602081:
F_PIPES = 0.99
F_UNCERTAINTY = 0.93
F_OTHERS = 0.98

# This version is closer to ISO 24194:2022:
# F_PIPES = 0.99
# F_UNCERTAINTY = {PCAccuracyClasses.one: 0.95,
#                  PCAccuracyClasses.two: 0.9,
#                  PCAccuracyClasses.three: 0.9}
# F_OTHERS = {PCFormulae.one: 0.98,
#             PCFormulae.two: 0.99,
#             PCFormulae.three: 0.99}

# Data
MIN_DATA_IN_INTERVAL = 10
LOWER_BOUND__MIN_DATA_IN_INTERVAL = 5
MAX_NAN_DENSITY = 0.10

# Intervals & gaps
MAX_INTERVAL_LENGTH = dt.timedelta(hours=6)
MAX_GAP_IN_INTERVAL = dt.timedelta(minutes=10)
DEFAULT_RATIO__MAX_GAP__TO__INTERVAL_LENGTH = 0.17
MIN_INTERVAL_LENGTH_EXTENDED = dt.timedelta(minutes=15)


# ------------------------------------------------------------------------------------
#
class PCSettings:
    """PC Method settings: Holds defaults, parses and validates a PC method settings dictionary, replacing None or
    missing settings with defaults.

    safety_pipes : float (optional)
        Safety factor considering heat losses from pipes etc. in the collector loop. To be estimated based on an
        evaluation of the pipe losses - normally only a few %.
        Default: None (0.98)
    safety_uncertainty : float (optional)
        Safety factor considering measurement uncertainty. To be estimated - with the requirements given in 6.1,
        a factor of 0.9 - 0.95 could be recommended depending on accuracy level.
        Default: None (will be set according to plant_measurement_accuracy)
    safety_others: float (optional)
        Safety factor for other uncertainties e.g. related to non-ideal conditions such as: • non-ideal flow
        distribution. To be estimated - should be close to one. • unforeseen heat losses. To be estimated - should
        be close to one. • uncertainties in the model/procedure itself. To be estimated - should be close to one.
        Note - it is recommended to put fO ≤ 1 when eq. (1) is used, as eq. (1) does not consider the influence of
        incidence angle modifiers.
        Default: None (will be set according to used formula)

    accuracy_level : {"I", "II", "III"} (optional)
        Level of accuracy of sensor as specified in ISO chapter 6. Will only be used for reporting and does not
        influence the output of the pc method.
    interval_length : dt.datetime (optional)
        Length of the interval over which single data records are averaged.
        This is set to 1 hour in the ISO 24194 standard, but can be changed for PCMethodExtended.

    max_nan_density : float (optional)
        maximum percentage of missing data allowed per interval. Intervals which have higher nan density will be
        discarded. 0 = no NaNs allowed, 1 = all NaNs is ok.
    min_data_in_interval : int (optional)
        Minimum non-NaN values per interval (defined by self.settings.interval_length).
        The default value of 20 is stated in ISO 24194 chapter 6.2.
        Explanation: Independently of NaNs, the situation could arise where there are only a few values in an
        interval, and it doesn't make much sense to include such intervals.
    max_gap_in_interval : dt.timedelta
        Even if an interval has a minimum number of intervals (at least min_data_in_interval), those records might be
        clustered e.g. at the beginning or end of the interval, with large gaps without data records in between.

    Notes
    -----
    Some settings for the Performance Check calculations depend on the chosen method (ISO | extended) and formula.
    That is why method and formula must be known at __init__ time.
    """
    safety_pipes: Optional[float]
    safety_uncertainty: Optional[float]
    safety_others: Optional[float]
    interval_length: Optional[dt.timedelta]
    max_gap_in_interval: Optional[dt.timedelta]
    min_data_in_interval: Optional[int]
    max_nan_density: Optional[float]
    min_intervals_in_output: Optional[int]
    accuracy_level: Optional[str]

    default_settings = dict(
        safety_pipes=F_PIPES,
        safety_uncertainty=None,  # Has no single default, depends on accuracy class
        safety_others=None,  # Has no single default, depends on formula
        interval_length=INTERVAL_LENGTH_ISO,
        min_data_in_interval=MIN_DATA_IN_INTERVAL,
        max_gap_in_interval=None,  # Default: fixed ratio of interval_length
        max_nan_density=MAX_NAN_DENSITY,
        min_intervals_in_output=MIN_INTERVALS_IN_OUTPUT,
        accuracy_level=PCAccuracyClasses.none,
    )

    @property
    def safety_combined(self):
        # Round to 2 digits, as required by ISO 24194
        f_safe = self.safety_uncertainty * self.safety_pipes * self.safety_others
        return np.round(f_safe, 2)

    @property
    def names(self):
        return self.default_settings.keys()

    def __init__(self,
                 method: Union[PCMethods, str],
                 formula: Union[PCFormulae, int],
                 **kwargs):

        settings = kwargs.copy()
        defaults = self.default_settings

        for k in settings:
            if k not in self.names:
                raise PCMethodError(f'Invalid Performance Check method setting: {k}. '
                                    f'Valid settings: {", ".join(self.names)}.')

        # Replace None / missing with default
        settings = {k: v for k, v in settings.items() if v is not None}
        for key in self.names:
            self.__setattr__(key, settings.get(key, defaults[key]))

        # Accuracy level
        try:
            self.accuracy_level = PCAccuracyClasses(self.accuracy_level)
        except ValueError as e:
            raise PCMethodError(
                f'{e}. Performance Check accuracy_level must be one of {", ".join(PCAccuracyClasses)}. ')

        # Safety factors
        # Safety factor uncertainty: depends on accuracy level
        if self.safety_uncertainty is None:
            self.safety_uncertainty = F_UNCERTAINTY
        # Safety factor others: depends on formula
        if self.safety_others is None:
            self.safety_others = F_OTHERS
        safety_ok = lambda x: (x is None) or ((x > 0) and (x <= 1))
        for f in ['safety_pipes', 'safety_uncertainty', 'safety_others']:
            if not safety_ok(getattr(self, f)):
                raise PCMethodError(
                    f'All Performance Check safety factors (for pipes, uncertainty and others) '
                    f'must be either None or floats between 0 and 1. '
                    f'Got "{f}" = {str(f)}.')

        # Interval length
        if self.interval_length > MAX_INTERVAL_LENGTH:
            raise PCMethodError(
                f'Performance Check maximum allowed interval length is {str(MAX_INTERVAL_LENGTH)}.')

        if method == PCMethods.iso:
            if self.interval_length != INTERVAL_LENGTH_ISO:
                raise PCMethodError(
                    f'For a Performance Check evaluation following the fixed-hour ("ISO") scheme, '
                    f'the "interval_length" is fixed to 1 hour, as defined in the ISO 24194.')

        if method == PCMethods.extended:
            if self.interval_length < MIN_INTERVAL_LENGTH_EXTENDED:
                raise PCMethodError(
                    f'For a Performance Check evaluation following the rolling-hour ("extended") scheme, '
                    f'"interval_length" should not be lower than {str(MIN_INTERVAL_LENGTH_EXTENDED)}.')

        # max_gap_in_interval
        if self.max_gap_in_interval is None:
            self.max_gap_in_interval = self.interval_length * DEFAULT_RATIO__MAX_GAP__TO__INTERVAL_LENGTH
        if self.max_gap_in_interval > self.interval_length:
            warnings.warn(f'Performance Check "max_gap_in_interval" cannot be longer than "interval_length". '
                          f'Setting "max_gap_in_interval" to {self.interval_length}.')
            self.max_gap_in_interval = self.interval_length

        # min_data_in_interval
        if self.min_data_in_interval < LOWER_BOUND__MIN_DATA_IN_INTERVAL:
            raise PCMethodError(
                f'Performance Check method option "min_data_in_interval" too low ({settings["min_data_in_interval"]}): '
                f'Setting "min_data_in_interval" to less than '
                f'{LOWER_BOUND__MIN_DATA_IN_INTERVAL} most likely yields poor results.')

        # max_nan_density
        if self.max_nan_density > 1 or self.max_nan_density < 0:
            raise PCMethodError(
                f'Performance Check option "max_nan_density" must be None or a float between 0 and 1. evaluation '
                f'Got {str(self.max_nan_density)}.')

        # min_intervals_in_output
        if self.min_intervals_in_output <= 0:
            raise PCMethodError(
                f'Performance Check option "min_intervals_in_output" must be None or greater than 0. '
                f'Got {str(self.min_intervals_in_output)}.')
        if method == PCMethods.iso:
            if self.min_intervals_in_output != MIN_INTERVALS_IN_OUTPUT:
                raise PCMethodError(
                    f'For a Performance Check evaluation following the fixed-hour ("ISO") scheme, '
                    f'"min_intervals_in_output" is fixed to {MIN_INTERVALS_IN_OUTPUT}, as defined in the ISO 24194.')

        # Now all settings should have been set / no None left
        none_settings = [s for s in self.names if getattr(self, s) is None]
        if none_settings:
            raise PCMethodError(f'Some settings are None after initializing PCSettings. This is an internal error. '
                                f'Settings being None: {", ".join(none_settings)}')


# ------------------------------------------------------------------------------------
# PC Method

# noinspection PyArgumentList
class PCMethod(ABC):
    """Superclass for various variants of the Performance Check Method.

    Parameters
    ----------
    plant : Plant
        Fully-configured plant with at least one array, and with virtual sensors calculated.
    formula : Formula
        Formula / equation to be used for the PC method. See ISO 24194 chapter 5.2.1.
    kwargs : passed to PCSettings
    """

    method_name = ""
    mode = ""

    @classmethod
    def create(cls,
               plant: Plant,
               method: PCMethods | str,
               formula: PCFormulae | int,
               use_wind: bool = True,
               **kwargs):

        method = PCMethods(method)
        if method == PCMethods.iso:
            return PCMethodISO(plant, formula, use_wind, **kwargs)
        elif method == PCMethods.extended:
            return PCMethodExtended(plant, formula, use_wind, **kwargs)
        else:
            raise PCMethodError(f'Cannot create PC method, invalid method "{method}".')

    def __init__(self,
                 plant: Plant,
                 formula: PCFormulae | int,
                 use_wind: bool = True,
                 **kwargs):
        self.plant = plant
        self.formula = Formula.create(formula, use_wind)
        self.settings = PCSettings(method=self.mode, formula=formula, **kwargs)

        self._mask = None
        self._bins = None
        self._output = {}
        return

    def run(self) -> results.PCMethodOutput:
        """ Applies the Performance Check on the plant and returns the estimated and calculated power.
        """
        if self._filter_intervals():
            self._calc_output()

        pc_method_output = self._create_output_object()
        return pc_method_output

    def get_feedback(self, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        r = CoreMethodFeedback()

        if not self.plant.arrays:
            r.add_missing_component(self.plant, 'arrays',
                                    'Plant has no arrays. To run a Performance Check analysis, '
                                    'the plant needs one or more arrays.')

        for slot in ['te_amb', 'tp']:
            if self.plant.is_sensor_missing(slot, check_mode):
                r.add_missing_sensor(self.plant, slot, check_mode)

        for array in self.plant.arrays:
            r = self.formula.get_feedback(r, array, check_mode)

        return r

    @abstractmethod
    def _aggregate_candidates(self, s: pd.Series, agg_fun: str):
        """Implements the aggregation of sensor data records, e.g. hourly mean (ISO) or rolling mean (extended),
        into candidate intervals that may be selected as the final PC method intervals.

        Parameters
        ----------
        s : pd. Series
        agg_fun : str, passed to pandas aggregate

        Returns
        -------
        pd.Series : resampled data
        """
        raise NotImplementedError

    @abstractmethod
    def _select_best_intervals(self):
        """Among all possible intervals, select the best non-overlapping intervals to be evaluated with the PC method.
        Returns pd.Series (with index self.plant.time_index) which is True at the starting points of the intervals.
        """
        raise NotImplementedError

    def _filter_intervals(self):
        """Constructs a DataFrame with a bool column ("mask") for each criteria the data in each interval must meet.
        This bool mask is stored in self._mask

        Returns
        -------
        bool : True if at least 1 interval has been found as a result of the filtering.

        Notes
        -----
        The resulting DataFrame is stored in self._mask
        One criterion is meeting the restrictions of PC method according to ISO 24194 Tabe 1.
        Criteria that are data quality related:
        - min_data_in_interval
        - max_gap_in_interval
        - max_nan_density
        - DataFrame index is self.plant.time_index.
        """
        self._mask = pd.DataFrame()

        # min_data_in_interval
        value_count = self._aggregate_candidates(self.plant.time_index.to_series(), 'count')
        self._mask['min_data_ok'] = (value_count >= self.settings.min_data_in_interval)

        # max_nan_density
        # nan_mask: True where _any_ of the sensors used in the PC method is NaN. Those records are rejected.
        nan_mask = self.formula.get_nan_mask(self.plant)
        nan_density = self._aggregate_candidates(nan_mask, 'sum') / value_count
        self._mask['nan_density_ok'] = (nan_density <= self.settings.max_nan_density)

        # max_gap_in_interval
        # Define gap of an index as average between backward and forward gap.
        bwd = self.plant.time_index.to_series().diff().dt.total_seconds()
        fwd = bwd.shift(-1)
        gaps = pd.concat([bwd, fwd], axis=1).mean(axis=1)
        max_gap = self._aggregate_candidates(gaps, 'max')
        self._mask['max_gap_ok'] = (max_gap <= self.settings.max_gap_in_interval.total_seconds())

        # Restrictions to interval filtering described in ISO 24194 Table 1, chapter 5.4.
        self._mask['pc_restrictions'] = \
            self.formula.calc_pc_restrictions(plant=self.plant,
                                              resampler=lambda s, fun='mean': self._aggregate_candidates(s, fun))

        self._mask['best_intervals'] = self._select_best_intervals()
        n_intervals = self._mask['best_intervals'].sum()
        self._output['n_intervals'] = n_intervals

        if (n_intervals < self.settings.min_intervals_in_output) and (self.mode == PCMethods.iso):
            sp_logger.warn(
                f'Performance check analysis found {n_intervals} intervals. For checking the collector performance, '
                f'the ISO 24194 recommends to have at least {MIN_INTERVALS_IN_OUTPUT} intervals.')
        if n_intervals == 0:
            return False

        # Out of the marked best intervals, create bins for groupby
        self._bins = pd.Series(data=np.nan, index=self.plant.time_index)
        for i, end in enumerate(self._mask.index[self._mask['best_intervals']]):
            mask = (self._bins.index > end - self.settings.interval_length) & (self._bins.index <= end)
            self._bins.loc[mask] = i

        return True

    def _calc_output(self):
        """Calculates estimated power for plant and all arrays, saves results in self attributes.

        Returns
        -------
        Nothing. Sets self._output_plant, self._slopes and self._output_arrays
        """
        tp_estimated = 0
        te_op_mean_area = 0
        self._output['arrays'] = {}
        self._output['data'] = {}

        # Aggregation of sensor data records for the final intervals selected among the candidates.
        #  - The final intervals meet data quality requirements and the restrictions of PC method Table 1.
        #  - The number of intervals is usually much smaller than the number of candidates. Thus groupby should be
        #    faster than resampling / rolling again and then filtering on self._mask['best_intervals']
        #  - The same aggregation is used for PCMethodISO and PCMethodExtended.
        aggregator = lambda s: s.groupby(self._bins).mean()

        for array in self.plant.arrays:
            df = self.formula.calc_estimated_power(array, aggregator)
            df['tp_sp_estimated_safety'] = df['tp_sp_estimated'] * self.settings.safety_combined
            df['tp_estimated'] = df['tp_sp_estimated'] * array.area_gr
            if (not array.tp.is_virtual) or (array.tp.is_virtual and array.tp.can_calculate):
                df['tp_sp_measured'] = aggregator(array.tp.data) / array.area_gr

            # Additional data, for current array, if not returned by calc_estimated_power()
            df['te_in'] = aggregator(array.te_in.data)
            df['te_out'] = aggregator(array.te_out.data)
            df['aoi'] = aggregator(array.aoi.data)
            if self.formula.use_wind:
                df['ve_wind'] = aggregator(self.plant.ve_wind.data)

            # Array results for current array is the DataFrame
            self._output['arrays'][array] = df
            tp_estimated += df['tp_estimated']
            te_op_mean_area += aggregator(array.te_op.data) * array.area_gr

        df = aggregator(self.plant.tp.data.astype('pint[kW]')).to_frame(name='tp_measured')
        df['tp_sp_measured'] = df['tp_measured'].astype('pint[W]') / self.plant.area_gr
        df['tp_sp_estimated'] = tp_estimated / self.plant.area_gr
        df['tp_estimated'] = tp_estimated.astype('pint[kW]')
        df['tp_sp_estimated_safety'] = df['tp_sp_estimated'] * self.settings.safety_combined
        # area-weighted mean operating temperature over all arrays
        te_op_mean = te_op_mean_area / self.plant.area_gr
        df['te_op_mean'] = te_op_mean.astype('pint[degC]')
        self._output['plant'] = df

        # Slope between measured and estimated power, for plant
        df_slopes = self._output['plant'].loc[:, ['tp_sp_measured', 'tp_sp_estimated', 'tp_sp_estimated_safety']]
        df_slopes = df_slopes.astype('float64')

        self._output['slopes'] = {}
        fit = smf.ols('tp_sp_measured ~ tp_sp_estimated -1', data=df_slopes).fit()
        self._output['slopes']['target_actual'] = Q(fit.params.to_numpy()[0], '')

        fit = smf.ols('tp_sp_measured ~ tp_sp_estimated_safety -1', data=df_slopes).fit()
        self._output['slopes']['target_actual_safety'] = Q(fit.params.to_numpy()[0], '')

    def _create_output_object(self) -> results.PCMethodOutput:
        """Gather all PC method calculation outputs required for ISO 24194 Annex A1, and a few more.

        Returns
        -------
        PCMethodOutput object
        """
        out = results.PCMethodOutput()

        out.plant = self.plant

        out.datetime_eval_start = self.plant.context.eval_start
        out.datetime_eval_end = self.plant.context.eval_end

        # Algorithm / Strategy
        out.pc_method_name = self.method_name
        out.evaluation_mode = PCMethods.iso.value if self.mode.value == PCMethods.iso else PCMethods.extended.value
        out.formula = self.formula.id
        out.wind_used = self.formula.use_wind

        # Strategy PCSettings
        settings = {k: v for k, v in vars(self.settings).items() if not k.startswith('_')}
        settings['safety_combined'] = self.settings.safety_combined
        out.settings = settings

        # Plant results
        plant_out = results.PCMethodOutputPlant()
        plant_out.plant = self.plant
        plant_out.n_intervals = self._output['n_intervals']
        plant_out.total_interval_length = plant_out.n_intervals * self.settings.interval_length
        intervals_end = self._mask.index[self._mask['best_intervals']].to_pydatetime()
        plant_out.datetime_intervals_start = intervals_end - self.settings.interval_length
        plant_out.datetime_intervals_end = intervals_end

        has_intervals = (self._output['n_intervals'] > 0)
        if has_intervals:
            df = self._output['plant']

            # This is necessary to prevent unneeded calls of config_virtuals -> PCMethodOutputPlant is AttrSetterMixin
            try:
                plant_out.defer_post_config_changed_actions = True
                plant_out.tp_measured = df['tp_measured'].astype(OutputUnits.tp)
                plant_out.tp_sp_measured = df['tp_sp_measured'].astype(OutputUnits.tp_sp)
                plant_out.tp_sp_estimated = df['tp_sp_estimated'].astype(OutputUnits.tp_sp)
                plant_out.tp_sp_estimated_safety = df['tp_sp_estimated_safety'].astype(OutputUnits.tp_sp)
                plant_out.mean_tp_sp_measured = plant_out.tp_sp_measured.mean()
                plant_out.mean_tp_sp_estimated = plant_out.tp_sp_estimated.mean()
                plant_out.mean_tp_sp_estimated_safety = plant_out.tp_sp_estimated_safety.mean()
                plant_out.target_actual_slope = self._output['slopes']['target_actual']
                plant_out.target_actual_slope_safety = self._output['slopes']['target_actual_safety']

                te = self._output['plant']['te_op_mean'].mean().to('degC')
                plant_out.mean_temperature = te
                te_s = pd.Series(data=te.to('K').magnitude).astype('pint[K]')

                plant_out.fluid_solar = self.plant.fluid_solar
                no_fluid = (self.plant.fluid_solar is None)
                plant_out.mean_fluid_density = None if no_fluid else self.plant.fluid_solar.get_density(te_s)[0]
                plant_out.mean_fluid_heat_capacity = None if no_fluid else \
                    self.plant.fluid_solar.get_heat_capacity(te_s)[0]
            finally:
                plant_out.defer_post_config_changed_actions = False

        out.plant_output = plant_out

        # Array results
        array_results = []
        for array in self.plant.arrays:
            arr_out = results.PCMethodOutputArray()
            arr_out.array = array

            if has_intervals:
                df = self._output['arrays'][array]
                try:
                    # Necessary to prevent unneeded calls of config_virtuals -> PCMethodOutputArray is AttrSetterMixin
                    plant_out.defer_post_config_changed_actions = True
                    if 'tp_sp_measured' in df.columns:
                        arr_out.tp_sp_measured = df['tp_sp_measured'].astype(OutputUnits.tp_sp)
                        arr_out.mean_tp_sp_measured = arr_out.tp_sp_measured.mean()
                    else:
                        arr_out.tp_sp_measured = None
                        arr_out.mean_tp_sp_measured = None

                    arr_out.tp_sp_estimated = df['tp_sp_estimated'].astype(OutputUnits.tp_sp)
                    arr_out.tp_sp_estimated_safety = df['tp_sp_estimated_safety'].astype(OutputUnits.tp_sp)
                    arr_out.mean_tp_sp_estimated = arr_out.tp_sp_estimated.mean()
                    arr_out.mean_tp_sp_estimated_safety = arr_out.tp_sp_estimated_safety.mean()

                    data = results.PCMethodOutputData()
                    # Data columns that are always returned by Formula
                    for col in ['te_amb', 'te_in', 'te_out', 'te_op', 'te_op_deriv', 'aoi', 'iam_b']:
                        data.__setattr__(col, df[col])
                    # Data columns that might be None
                    for col in ['rd_gti', 'rd_bti', 'rd_dti', 've_wind']:
                        data.__setattr__(col, df[col] if col in df.columns else None)
                    arr_out.data = data

                finally:
                    plant_out.defer_post_config_changed_actions = False

            array_results.append(arr_out)

        out.array_output = array_results

        return out


class PCMethodISO(PCMethod):
    """This PC method implementation aligns as strictly as possible to the method as defined in the technical
    standard ISO 24194.
    """

    method_name = "PC Method 'ISO 24194'"
    mode = PCMethods.iso

    def _aggregate_candidates(self, s, agg_fun):
        s = s.resample(self.settings.interval_length, closed='right', label='right').aggregate(agg_fun)
        return s

    def _select_best_intervals(self):
        """Due to the fixed-hour resampling pattern used in the PCMethodISO data aggregation, we have no overlapping
        intervals, so all intervals that fulfill all constraints (self._mask) are ok.
        """
        return self._mask.all(axis='columns')


class PCMethodExtended(PCMethod):
    """This class implements the "extended" variant of the Performance Check method, with improvements in data
    analysis. See class docstring for more info.
    """

    method_name = "PC Method 'ISO 24194' extended"
    mode = PCMethods.extended

    def _aggregate_candidates(self, s, agg_fun='mean'):
        s_out = s.rolling(window=self.settings.interval_length, closed='right').aggregate(agg_fun)
        # For some reason, the "rolling" operation drops the pint dtype.
        if agg_fun not in ['sum', 'count']:
            s_out = s_out.astype(s.dtype)
        return s_out

    def _select_best_intervals(self):
        """Due to the rolling averaging used in the PCMethodExtended data aggregation, we might have overlapping
        intervals that fulfill all ISO 24194 requirements.
        This algorithm ranks intervals according to a score, which is relative standard deviation of thermal power,
        evaluated over the interval.
        This algorithm chooses the best interval, then excludes all overlapping intervals, goes on with the
        remaining intervals etc. until no intervals are left.
        """
        # Intervals that fulfill all constraints so far:
        is_candidate = self._mask.all(axis='columns')

        # Criterion to find "best" interval among overlapping: smallest relative standard deviation of plant power.
        tp = self.plant.tp.data
        variation = (self._aggregate_candidates(tp, 'std') / self._aggregate_candidates(tp, 'mean')).astype(
            'float64')
        score = 1 / variation
        score[~is_candidate] = 0

        # Iteratively add the best interval and remove overlapping intervals from candidates.
        idx = self.plant.time_index
        best_intervals_mask = pd.Series(index=idx, data=False)
        while any(is_candidate):
            # Mark best-scoring interval. Exit if score is NaN in all remaining candidates:
            if score.where(is_candidate).isna().all():
                break
            # If idxmax is not unique --> returns first occurrence of maximum
            best_idx = score.where(is_candidate).idxmax()
            best_intervals_mask.loc[best_idx] = True
            # Remove overlapping intervals (past and future) from candidates
            is_candidate.loc[
                (idx > best_idx - self.settings.interval_length) & (
                        idx < best_idx + self.settings.interval_length)] = False

        return best_intervals_mask
