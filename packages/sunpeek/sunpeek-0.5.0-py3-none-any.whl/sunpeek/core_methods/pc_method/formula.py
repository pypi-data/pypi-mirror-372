from abc import ABC, abstractmethod
from typing import Callable
import pandas as pd

from sunpeek.common.unit_uncertainty import Q
from sunpeek.components.helpers import AlgoCheckMode
from sunpeek.core_methods.common.main import is_valid_collector
from sunpeek.components import Plant, Array, CollectorTypes
from sunpeek.core_methods.pc_method import PCFormulae, OutputUnits
from sunpeek.serializable_models import CoreMethodFeedback

# Common to all formulae
MAX_DELTA_T_COLLECTOR = Q(5.0, 'K hour**-1')
MIN_TE_AMB = Q(5.0, 'degC')
MAX_WIND_SPEED = Q(10, 'm s**-1')

# Deliberately set maximum incidence angle (not defined in ISO 24194).
# This maximum incidence angle is used to avoid outliers that may happen at intervals with very large incidence angles.
# This also helps to avoid numerical problems and problems with calculated Kd values at high incidence angles.
# The value of 80 degrees is the value recommended by BSRN, https://bsrn.awi.de/.
MAX_AOI = Q(80, 'deg')

# Formula 1: minimum global tilted irradiance
MIN_RD_GTI = Q(800, 'W m**-2')

# Formula 2 and 3: minimum beam tilted irradiance
MIN_RD_BTI = Q(600, 'W m**-2')


# noinspection PyArgumentList
class Formula(ABC):
    """Template class for the equations / formulae for calculating power output, as defined in the ISO 24194:

    The formulae are defined in ISO 24194 chapter 5.2.1. The formulae specify
    1. how power output is calculated / estimated
    2. and what restrictions are applied to data: the criteria in ISO 24194 Table 1 depend on the formula choice.

    "
    # 5.1 Stating an estimate for the thermal power output of a collector field
    The estimated power output of the collector array is given as an equation depending on the collector parameters
    according to ISO 9806 and operation conditions. The measured power shall comply with the corresponding calculated
    power according to this equation. Measured and calculated power are only compared under some specific conditions
    to avoid too large uncertainties - see section 5.4

    The estimate is given by stating the equation to be used for calculating the power output, including specific
    values for the parameters in equation. The three possible equations are given in the next three subsections.
    The collector module efficiency parameters eta0_hem, eta0_b, Kb(theta) Kd, a1, a2, a5 [1] and a8 should be based on
    certified test results. When an estimate is given it shall always be stated which equation shall be used for
    checking the performance:

    a) Simple check, using total radiation on the collector plane when checking the power output (ISO this standard,
    eq 1).
    b) Advanced check, using direct and diffuse radiation on collector plane when checking the power output
    (ISO this standard, eq 2).
    c) Advanced check, using only direct radiation on collector plane when checking the power output
    (ISO this standard, eq3)

    [1] in the older Solar Keymark data sheets a5 is denoted c_eff
    "
    """

    id = None

    # Restrictions on operating conditions based on Table 1 of ISO 24194.
    # Only data that pass these restrictions (as averages over given time range) are used for calculation of estimated
    # array power.
    # Restrictions common to formulae 1, 2 & 3
    max_deltat_collector = MAX_DELTA_T_COLLECTOR
    min_te_amb = MIN_TE_AMB
    max_wind_speed = MAX_WIND_SPEED
    max_aoi = MAX_AOI

    @classmethod
    def create(cls, formula: PCFormulae | int,
               use_wind: bool) -> 'Formula':
        formula = PCFormulae(formula)
        match formula:
            case PCFormulae.one:
                return Formula1(use_wind)
            case PCFormulae.two:
                return Formula2(use_wind)
            case PCFormulae.three:
                return Formula3(use_wind)
            case _:
                raise ValueError(f'{formula} is not a valid PCFormulae. '
                                 f'Valid formulae: {", ".join(map(str, PCFormulae))}.')

    def __init__(self, use_wind: bool):
        """
        Parameters
        ----------
        use_wind : bool
            if False, the wind speed sensor is ignored as a restriction to finding valid intervals
            in the data filtering process for meeting the ISO 24194 requirements.
        """
        self.use_wind = use_wind
        return

    def get_feedback(self, fb: CoreMethodFeedback, array: Array, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        for attrib in ['area_gr']:
            if array.is_attrib_missing(attrib):
                fb.add_missing_attrib(array, attrib)

        if not is_valid_collector(array.collector, check_mode):
            fb.add_missing_collector(array, 'collector')
        else:
            for attrib in ['a5', 'eta0b']:
                if array.collector.is_zero(attrib):
                    fb.add_zero_collector_param(array.collector, attrib)

        for slot in ['te_op', 'te_op_deriv', 'is_shadowed', 'iam']:
            if array.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(array, slot, check_mode)

        if self.use_wind:
            slot = 've_wind'
            if array.plant.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(array.plant, slot, check_mode)

        return fb

    @abstractmethod
    def get_nan_mask(self, plant: Plant):
        """Check if all sensors required to apply a specific formula are available.

        Returns
        -------
        bool : True where any of the sensors required to calculate the formula are NaN.

        Notes
        -----
        In this PC Method implementation, only data records are used where none of the needed sensor records is NaN.
        """
        raise NotImplementedError

    def _get_nan_mask_common(self, plant):
        """Check sensors common to formulae 1, 2 and 3.
        """

        # Plant
        mask = plant.te_amb.data.isna()
        mask = mask | plant.tp.data.isna()
        mask = mask | plant.sun_apparent_elevation.data.isna()
        if self.use_wind:
            mask = mask | plant.ve_wind.data.isna()

        # Arrays
        for array in plant.arrays:
            mask = mask | array.te_op.data.isna()
            mask = mask | array.te_op_deriv.data.isna()
            mask = mask | array.is_shadowed.data.isna()
            mask = mask | array.iam.data.isna()

        return mask

    @abstractmethod
    def calc_pc_restrictions(self, plant: Plant, resampler: Callable) -> pd.Series:
        """Check the operating condition restrictions of ISO 24194. Implement Table 1, chapter 5.4.

        Parameters
        ----------
        plant : Plant
        resampler : Callable
            Aggregates single records into an aggregated value, e.g. hourly mean.

        Returns
        -------
        pd.Series : bool mask, True where any of the sensors required to calculate the formulae are NaN.

        Notes
        -----
        From the ISO 24194:
            # 6.2 Valid data records
            Only data records (hourly average values) fulfilling the requirements in section 5.4 are valid.
            For checking the collector performance, the measuring period shall have at least 20 datapoints.
            [...]
            All valid datapoints should be used unless it is obvious that errors in the data or very atypical
            operating conditions occur (omitting valid data points shall be reported and justified).
        """
        raise NotImplementedError

    def _calc_pc_restrictions_common(self, plant, resampler) -> pd.Series:
        """Check the operating condition restrictions that are common to PC Formula 1, 2 and 3.

        Returns
        -------
        pd.Series : bool mask
        """
        # Minimum ambient temperature
        is_valid = resampler(plant.te_amb.data) >= self.min_te_amb
        # Maximum wind speed
        if self.use_wind:
            is_valid = is_valid & (resampler(plant.ve_wind.data) <= self.max_wind_speed)

        for array in plant.arrays:
            # No shadows
            is_valid = is_valid & (resampler(array.is_shadowed.data, 'sum') == 0)
            # Maximum temperature change
            is_valid = is_valid & (resampler(array.te_op_deriv.data).abs() <= self.max_deltat_collector)
            # Maximum incidence angle
            is_valid = is_valid & (resampler(array.aoi.data, 'max') <= self.max_aoi)

        return is_valid

    @abstractmethod
    def calc_estimated_power(self, array: Array, aggregator: Callable) -> pd.DataFrame:
        """Calculate the estimated specific power output of the collector based on the specific formula.

        Parameters
        ----------
        array : Array
        aggregator : Callable
            Aggregates single records into an aggregated value, e.g. hourly mean.

        Returns
        -------
        pd.DataFrame : Estimated power output of the collector, unit-aware series compatible to unit [W m**-2]
            Other columns are the measurement values of input data used in the calculations, all in unit-aware series.
        """
        raise NotImplementedError


# noinspection PyArgumentList
class Formula1(Formula):
    """ Implement formula 1 of the ISO 24194. See :class:`Formula` base class for more info.
    """
    id = 1

    # Restrictions specific to formula 1
    min_rd_gti = MIN_RD_GTI

    def get_feedback(self, fb: CoreMethodFeedback, array: Array, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        fb = super().get_feedback(fb, array, check_mode)

        if is_valid_collector(array.collector, check_mode):
            expected_type = CollectorTypes.flat_plate
            if array.collector.collector_type != expected_type:
                fb.add_wrong_collector_type(array.collector,
                                            expected=expected_type,
                                            received=array.collector.collector_type)
            # Note: eta0hem needed for calculation of khem, see calc_estimated_power()
            for attrib in ['eta0hem', 'kd', 'a1', 'a2']:
                if array.collector.is_zero(attrib):
                    fb.add_zero_collector_param(array.collector, attrib)
            for attrib in ['a8']:
                if array.collector.is_nonzero(attrib):
                    fb.add_nonzero_collector_param(array.collector, attrib)

        for slot in ['rd_gti', 'aoi']:
            if array.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(array, slot, check_mode)

        return fb

    def get_nan_mask(self, plant: Plant):
        # Common sensors
        mask = self._get_nan_mask_common(plant)

        # Specific to formula 1
        for array in plant.arrays:
            mask = mask | array.rd_gti.data.isna()
            mask = mask | array.aoi.data.isna()

        return mask

    def calc_pc_restrictions(self, plant, resampler) -> pd.Series:
        is_valid = self._calc_pc_restrictions_common(plant, resampler)

        for array in plant.arrays:
            # Minimum diffuse radiation
            is_valid = is_valid & (resampler(array.rd_gti.data) >= self.min_rd_gti)

        return is_valid

    def calc_estimated_power(self, array, aggregator) -> pd.DataFrame:
        """Calculate the estimated power output of a collector array based on formula 1 in ISO 24194.
        """
        # Collector coefficients
        a1 = array.collector.a1
        a2 = array.collector.a2
        a5 = array.collector.a5
        eta0b = array.collector.eta0b
        eta0hem = array.collector.eta0hem
        kd = array.collector.kd

        # Measurements
        rd_gti = aggregator(array.rd_gti.data)
        te_amb = aggregator(array.plant.te_amb.data)
        te_op = aggregator(array.te_op.data)
        te_op_deriv = aggregator(array.te_op_deriv.data)

        # Calculation of hemispheric incidence angle modifier for global tilted radiation:
        # Calculation is based on ISO 9806:2017 annex B, with variable name iam_xx used here instead of K_xx
        # G * iam_hem * eta0hem = G * eta0b * (0.85 * iam_b + 0.15 * iam_d)
        kb = aggregator(array.iam.data)
        khem = (eta0b / eta0hem) * (0.85 * kb + 0.15 * kd)

        tp_estimated_specific = eta0hem * khem * rd_gti \
                                - a1 * (te_op - te_amb) \
                                - a2 * (te_op - te_amb) ** 2 \
                                - a5 * te_op_deriv

        df = pd.DataFrame({
            'tp_sp_estimated': tp_estimated_specific.astype(OutputUnits.tp_sp),
            'rd_gti': rd_gti.astype(OutputUnits.rd),
            'iam_b': kb.astype(OutputUnits.iam),
            'te_amb': te_amb.astype(OutputUnits.te),
            'te_op': te_op.astype(OutputUnits.te),
            'te_op_deriv': te_op_deriv.astype(OutputUnits.te_deriv),
        })

        return df


# noinspection PyArgumentList
class Formula2(Formula):
    """ Implement formula 2 of the ISO 24194. See :class:`Formula` base class for more info.
    """
    id = 2

    # Restrictions specific to formula 2
    min_rd_bti = MIN_RD_BTI

    def get_feedback(self, fb: CoreMethodFeedback, array: Array, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        fb = super().get_feedback(fb, array, check_mode)

        if is_valid_collector(array.collector, check_mode):
            expected_types = [CollectorTypes.flat_plate, CollectorTypes.concentrating]
            if array.collector.collector_type not in expected_types:
                fb.add_wrong_collector_type(array.collector,
                                            expected=expected_types,
                                            received=array.collector.collector_type)
            for attrib in ['kd', 'a1', 'a2']:
                if array.collector.is_zero(attrib):
                    fb.add_zero_collector_param(array.collector, attrib)
            for attrib in ['a8']:
                if array.collector.is_nonzero(attrib):
                    fb.add_nonzero_collector_param(array.collector, attrib)
            if array.collector.concentration_ratio is not None and array.collector.concentration_ratio >= Q(20):
                fb.add_generic_slot_problem(array.collector, f'Performance Check formula 2 is only applicable to '
                                                             f'concentrating collectors with a concentration_ratio < 20. '
                                                             f'This collector has a concentration_ratio of '
                                                             f'{array.collector.concentration_ratio.m:.2f}.')

        for slot in ['rd_bti', 'rd_dti']:
            if array.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(array, slot, check_mode)

        return fb

    def get_nan_mask(self, plant: Plant):
        # Common sensors
        mask = self._get_nan_mask_common(plant)

        # Specific to formula 2
        for array in plant.arrays:
            mask = mask | array.rd_bti.data.isna()
            mask = mask | array.rd_dti.data.isna()

        return mask

    def calc_pc_restrictions(self, plant, resampler) -> pd.Series:
        is_valid = self._calc_pc_restrictions_common(plant, resampler)

        for array in plant.arrays:
            # Minimum beam radiation
            is_valid = is_valid & (resampler(array.rd_bti.data) >= self.min_rd_bti)

        return is_valid

    def calc_estimated_power(self, array, aggregator) -> pd.DataFrame:
        """Calculate the estimated specific power output of a collector array based on formula 2 in ISO 24194.
        """
        # Collector coefficients
        a1 = array.collector.a1
        a2 = array.collector.a2
        a5 = array.collector.a5
        eta0b = array.collector.eta0b
        kd = array.collector.kd

        # Measurements
        rd_bti = aggregator(array.rd_bti.data)
        rd_dti = aggregator(array.rd_dti.data)
        iam_b = aggregator(array.iam.data)
        te_amb = aggregator(array.plant.te_amb.data)
        te_op = aggregator(array.te_op.data)
        te_op_deriv = aggregator(array.te_op_deriv.data)

        tp_estimated_specific = eta0b * iam_b * rd_bti + eta0b * kd * rd_dti \
                                - a1 * (te_op - te_amb) \
                                - a2 * (te_op - te_amb) ** 2 \
                                - a5 * te_op_deriv

        df = pd.DataFrame({
            'tp_sp_estimated': tp_estimated_specific.astype(OutputUnits.tp_sp),
            'rd_bti': rd_bti.astype(OutputUnits.rd),
            'rd_dti': rd_dti.astype(OutputUnits.rd),
            'iam_b': iam_b.astype(OutputUnits.iam),
            'te_amb': te_amb.astype(OutputUnits.te),
            'te_op': te_op.astype(OutputUnits.te),
            'te_op_deriv': te_op_deriv.astype(OutputUnits.te_deriv),
        })

        return df


# noinspection PyArgumentList
class Formula3(Formula):
    """ Implement formula 3 of the ISO 24194. See :class:`Formula` base class for more info.
    """
    id = 3

    # Restrictions specific to formula 3
    min_rd_bti = MIN_RD_BTI

    def get_feedback(self, fb: CoreMethodFeedback, array: Array, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        fb = super().get_feedback(fb, array, check_mode)

        if is_valid_collector(array.collector, check_mode):
            expected_type = CollectorTypes.concentrating
            if array.collector.collector_type != expected_type:
                fb.add_wrong_collector_type(array.collector,
                                            expected=expected_type,
                                            received=array.collector.collector_type)
            for attrib in ['a8']:
                if array.collector.is_zero(attrib):
                    fb.add_zero_collector_param(array.collector, attrib)
            if array.collector.concentration_ratio is not None and array.collector.concentration_ratio < Q(20):
                fb.add_generic_slot_problem(array.collector, f'Performance Check formula 3 is only applicable to '
                                                             f'concentrating collectors with a concentration_ratio >= 20. '
                                                             f'This collector has a concentration_ratio of '
                                                             f'{array.collector.concentration_ratio.m:.2f}.')

        for slot in ['rd_bti']:
            if array.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(array, slot, check_mode)

        return fb

    def get_nan_mask(self, plant: Plant):
        # Common sensors
        mask = self._get_nan_mask_common(plant)

        # Specific to formula 3
        for array in plant.arrays:
            mask = mask | array.rd_bti.data.isna()

        return mask

    def calc_pc_restrictions(self, plant, resampler) -> pd.Series:
        is_valid = self._calc_pc_restrictions_common(plant, resampler)

        for array in plant.arrays:
            # Minimum beam radiation
            is_valid = is_valid & (resampler(array.rd_bti.data) >= self.min_rd_bti)

        return is_valid

    def calc_estimated_power(self, array, aggregator) -> pd.DataFrame:
        """Calculate the estimated specific power output of a collector array based on formula 3 in ISO 24194.
        """
        # Collector coefficients
        a1 = array.collector.a1
        a5 = array.collector.a5
        a8 = array.collector.a8
        eta0b = array.collector.eta0b

        # Measurements
        rd_bti = aggregator(array.rd_bti.data)
        iam_b = aggregator(array.iam.data)
        te_amb = aggregator(array.plant.te_amb.data)
        te_op = aggregator(array.te_op.data)
        te_op_deriv = aggregator(array.te_op_deriv.data)

        tp_estimated_specific = eta0b * iam_b * rd_bti \
                                - a1 * (te_op - te_amb) \
                                - a5 * te_op_deriv \
                                - a8 * (te_op - te_amb) ** 4

        df = pd.DataFrame({
            'tp_sp_estimated': tp_estimated_specific.astype(OutputUnits.tp_sp),
            'rd_bti': rd_bti.astype(OutputUnits.rd),
            'iam_b': iam_b.astype(OutputUnits.iam),
            'te_amb': te_amb.astype(OutputUnits.te),
            'te_op': te_op.astype(OutputUnits.te),
            'te_op_deriv': te_op_deriv.astype(OutputUnits.te_deriv),
        })

        return df
