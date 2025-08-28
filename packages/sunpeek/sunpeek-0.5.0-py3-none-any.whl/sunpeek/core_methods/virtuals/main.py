"""
This module implements functionality for calculation and verification of virtual sensors.

It contains two entry-point functions for doing virtual sensor stuff.
- config_virtuals():
   - Is fast to run, only depends on plant config, no calculations.
   - Attaches a CoreMethodFeedback to all virtual sensors, stating if it _can_ be calculated / why not
- calculate_virtuals():
   - Actually calculates virtual sensors for all components.
   - Calculation logic is hard coded.

## Details

- Implements functions that calculate groups of virtual sensors
  (one calculation call returns data for multiple virtual sensors).
- Calculations generally return unit-aware pd.Series objects, `pd.Series with dtype pint[unit]`.
- Internal functions (underscore functions) may also accept and return arguments as numeric values in appropriate units
(as opposed to the main calculations which work with pint Quantities). See local docstrings for details.
- The module also implements functions to verify / assert calculation inputs.

## Note for developers:
- Virtual sensors may use data and parameters of various objects in their calculations (e.g. plant latitude,
array irradiance, array area etc.). Therefore, virtual sensors are associated to one and only one component. They
may not be linked / associated with more than one component, like real sensors which
can be "shared" by multiple components.

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
"""

import pendulum

from sunpeek.common.utils import sp_logger
import sunpeek.core_methods.virtuals.virtuals_plant as vp
import sunpeek.core_methods.virtuals.virtuals_array as va
from sunpeek.components.base import Component


def config_virtuals(plant) -> None:
    """Creates & maps virtual sensors for all components.

    Raises
    ------
    VirtualSensorConfigurationError
    """
    start_time = pendulum.now()

    vp.config_virtuals_ambient(plant)
    vp.config_virtuals_power(plant)
    # Uncomment if plant horizontal radiations are needed e.g. for KPIs.
    # vp.config_virtuals_radiation_conversion(plant)

    for array in plant.arrays:
        va.config_virtuals_ambient(array)
        va.config_virtuals_power(array)
        va.config_virtuals_temperature(array)
        va.config_virtuals_radiation(array)
        # Uncomment if vsensor array.te_out (averaged over row outlet temperatures) is required.
        # va.config_virtuals_te_out(array)

    plant.virtuals_calculation_uptodate = False

    sp_logger.debug(f"  [config_virtuals] --- Done in {(pendulum.now() - start_time).total_seconds():.1f} seconds ---")


def calculate_virtuals(plant) -> None:
    """Implements all the logic of the virtual sensor calculation. Typically called by data upload.

    Raises
    ------
    CalculationError

    Notes
    -----
    At the end of calculate_virtuals, there might be virtual sensors that have not been calculated, for a variety of
    possible reasons. Such an uncalculated virtual sensor, when queried for data (vsensor.data), it returns an
    all-NaN series with the correct physical unit (pint dtype) attached.
    """
    config_virtuals(plant)
    start_time = pendulum.now()

    sp_logger.debug(f"[calculate_virtuals] Calculating virtual sensors data.")
    plant.context.verify_time_index()

    vp.calculate_virtuals_ambient(plant)
    vp.calculate_virtuals_power(plant)
    # Uncomment if horizontal radiations needed
    # vp.calculate_virtuals_radiation_conversion(plant)

    # Arrays
    for array in plant.arrays:
        va.calculate_virtuals_ambient(array)
        va.calculate_virtuals_power(array)
        va.calculate_virtuals_temperature(array)
        va.calculate_virtuals_radiation(array)
        # Uncomment if vsensor array.te_out (averaged over row outlet temperatures) is required.
        # va.calculate_virtuals_te_out(array)

    plant.virtuals_calculation_uptodate = True

    sp_logger.debug(f"[calculate_virtuals] --- Done in {(pendulum.now() - start_time).total_seconds():.1f} seconds ---")


Component.register_callback('post_config_changed_callbacks', config_virtuals)
