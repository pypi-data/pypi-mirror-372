from typing import Optional
from sunpeek.core_methods.virtuals import calculations as algos
from sunpeek.common.errors import CalculationError


def config_virtuals_ambient(array):
    """Virtual sensors for sun- and shadow-related stuff in array.
    """
    # Angle of incidence
    feedback = algos.AngleOfIncidence(array).get_config_feedback()
    array.map_vsensor('aoi', feedback)

    # Internal shading
    feedback = algos.InternalShading(array).get_config_feedback()
    array.map_vsensor('is_shadowed', feedback)
    array.map_vsensor('internal_shading_fraction', feedback)


def calculate_virtuals_ambient(array):
    # Angle of incidence
    result = algos.AngleOfIncidence(array).run()
    array.aoi.update('aoi', result)

    # Internal shading
    result = algos.InternalShading(array).run()
    # Cannot take is_shadowed from a "feedthrough" strategy because that would not calculate the other outputs
    if array.is_shadowed.is_virtual:
        array.is_shadowed.update('is_shadowed', result)
    array.internal_shading_fraction.update('internal_shading_fraction', result)


def config_virtuals_power(array):
    # Thermal power
    array.map_vsensor('tp', algos.ThermalPower(array).get_config_feedback())
    # Mass flow
    array.map_vsensor('mf', algos.MassFlow(array).get_config_feedback())


def calculate_virtuals_power(array):
    # Thermal power
    array.tp.update('tp', algos.ThermalPower(array).run())
    # Mass flow
    array.mf.update('mf', algos.MassFlow(array).run())


def config_virtuals_temperature(array):
    """Virtual sensors for mean operating temperature, temperature derivative etc.
    """
    feedback = algos.ArrayTemperatures(array).get_config_feedback()
    array.map_vsensor('te_op', feedback)
    array.map_vsensor('te_op_deriv', feedback)


def calculate_virtuals_temperature(array):
    feedback = algos.ArrayTemperatures(array).run()
    array.te_op.update('te_op', feedback)
    array.te_op_deriv.update('te_op_deriv', feedback)


def config_virtuals_radiation(array):
    """Array plane-of-array irradiance (global, beam, diffuse) including masking, shading etc.
    """
    problems = algos.TiltedIrradiances(array).get_config_feedback()
    array.map_vsensor('rd_gti', problems)
    array.map_vsensor('rd_bti', problems)
    array.map_vsensor('rd_dti', problems)

    # Incidence angle modifier
    array.map_vsensor('iam', algos.AlgoIAM(array).get_config_feedback())


def calculate_virtuals_radiation(array, strategy: Optional[str] = None):
    """Array irradiance components, including beam shading and diffuse masking.
    """
    if strategy is None:
        algo = algos.TiltedIrradiances(array)
    elif strategy == 'feedthrough':
        strategy = algos.StrategyTiltedIrradiance_feedthrough(array)
        algo = algos.TiltedIrradiances(array, strategies=[strategy])
    else:
        raise CalculationError(f'Unknown strategy string: "{strategy}".')

    result = algo.run()
    array.rd_gti.update('rd_gti', result)
    array.rd_bti.update('rd_bti', result)
    array.rd_dti.update('rd_dti', result)

    # Incidence angle modifier
    result = algos.AlgoIAM(array).run()
    array.iam.update('iam', result)
