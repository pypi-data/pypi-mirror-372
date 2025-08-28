"""Module implementing virtual sensor calculations, in terms of CoreAlgorithm and CoreStrategy classes.

To add an implementation, subclass CoreAlgorithm (see ThermalPower class for instance).
- allowed_components(): specify to which component the algorithm applies
- define_strategies(): add specific ways to calculate the algorithm output, in terms of CoreStrategy classes

For each such CoreStrategy or VirtualSensorStrategy, implement
- _calc(): The calculation itself. Output must be a dict containing unit-aware pd.Series (with dtype pint[unit]).
- _get_feedback(): Add checks for all inputs required by _calc(). This is used by config_virtuals(plant).

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
.. codeauthor:: Peter Zauner <p.zauner@aee.at>
"""
import pandas as pd
import numpy as np
import scipy.signal
import pvlib
# from sympy import symbols, Eq, solve
# from sympy import cos, tan, sin
# from metpy.calc import dewpoint_from_relative_humidity

import sunpeek.common.unit_uncertainty as uu
from sunpeek.common.unit_uncertainty import Q
from sunpeek.components import Plant, Array
from sunpeek.core_methods.common.shading import calc_BanyAppelbaum_shading, calc_sloped_shading
from sunpeek.serializable_models import CoreMethodFeedback
from sunpeek.core_methods.common.main import CoreAlgorithm, VirtualSensorStrategy, is_valid_fluid, is_valid_collector
from sunpeek.common.errors import CalculationError
import sunpeek.core_methods.virtuals.radiation as rd


# ----------------------------------------------------------------------------------------------------------------------
# Thermal Power

class ThermalPower(CoreAlgorithm):
    """Thermal power for Plant and Arrays.
    """

    def allowed_components(self):
        return Plant, Array

    def define_strategies(self):
        return [
            StrategyPowerFromSensor(self.component),
            # If needed, add strategy to calculate plant power from arrays
            # StrategyPowerFromArrays(self.component),
            StrategyPowerFromVolumeFlow(self.component),
        ]


# noinspection PyArgumentList
class StrategyPowerFromSensor(VirtualSensorStrategy):
    """Feedthrough strategy, taking power from a Plant or Array `tp` real sensor.
    """
    name = 'Calculate thermal power from real sensor'
    feedthrough_real_sensor = True

    def _calc(self):
        return {'tp': None}

    def _get_feedback(self, check_mode):
        """Make sure real sensor 'tp' exists in Plant or Array.
        """
        fb = CoreMethodFeedback()
        slot = 'tp'
        if self.component.is_real_sensor_missing(slot, check_mode):
            fb.add_missing_real_sensor(self.component, slot)
        return fb


# noinspection PyArgumentList
class StrategyPowerFromVolumeFlow(VirtualSensorStrategy):
    """For Plant and Arrays, calculate thermal power from fluid, volume flow and inlet & outlet temperatures.
    """
    name = 'Calculate thermal power from volume flow'

    def _get_feedback(self, check_mode):
        fb = CoreMethodFeedback()
        if not is_valid_fluid(self.component.fluid_solar, check_mode):
            fb.add_missing_fluid(self.component, 'fluid_solar')

        for slot in ['vf', 'te_in', 'te_out']:
            if self.component.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(self.component, slot, check_mode)

        slot, info_name = 'vf', 'position'
        if not self.component.is_sensor_missing('vf', check_mode):
            if self.component.vf.is_info_missing(info_name):
                fb.add_missing_sensor_info(self.component, slot, info_name)
        return fb

    def _calc(self):
        """
        Notes
        -----
        Position of volume flow sensor decides which temperature (inlet or outlet or a weighted average) is used for
        density / mass flow calculation.
        """

        fluid = self.component.fluid_solar
        vf = self.component.vf.data
        te_in = self.component.te_in.data
        te_out = self.component.te_out.data
        pos = self.component.vf.info['position'].m_as('')

        rho = fluid.get_density(te=_get_weighted_temperature(te_in, te_out, 1 - pos, pos))
        cp = fluid.get_heat_capacity(te=_get_weighted_temperature(te_in, te_out))
        mf = vf * rho * cp
        tp = mf * (te_out - te_in)

        return {'tp': tp}


# ----------------------------------------------------------------------------------------------------------------------
# Mass Flow

class MassFlow(CoreAlgorithm):
    """Mass flow for Plants and Arrays."""

    def allowed_components(self):
        return Plant, Array

    def define_strategies(self):
        return [
            StrategyMassFlowFromPower(self.component),
            StrategyMassFlowFromVolumeFlow(self.component),
        ]


# noinspection PyArgumentList
class StrategyMassFlowFromPower(VirtualSensorStrategy):
    """For Plants and Arrays, calculate mass flow from fluid, thermal power and inlet & outlet temperatures.
    """
    name = 'Calculate mass flow from thermal power'

    def _get_feedback(self, check_mode):
        fb = CoreMethodFeedback()
        if not is_valid_fluid(self.component.fluid_solar, check_mode):
            fb.add_missing_fluid(self.component, 'fluid_solar')

        for slot in ['tp', 'te_in', 'te_out']:
            if self.component.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(self.component, slot, check_mode)

        return fb

    def _calc(self):
        """
        Returns
        -------
        tp : pd.Series
            Calculated mass flow.
        """
        fluid = self.component.fluid_solar
        tp = self.component.tp.data
        te_in = self.component.te_in.data
        te_out = self.component.te_out.data

        cp = fluid.get_heat_capacity(te=_get_weighted_temperature(te_in, te_out))
        mf = tp / (cp * (te_out - te_in))

        return {'mf': mf.pint.to('kg s**-1')}


# noinspection PyArgumentList
class StrategyMassFlowFromVolumeFlow(VirtualSensorStrategy):
    """For Plants and Arrays, calculate mass flow from fluid, thermal power and inlet & outlet temperatures.
    """
    name = 'Calculate mass flow from volume flow'

    def _get_feedback(self, check_mode):
        fb = CoreMethodFeedback()
        if not is_valid_fluid(self.component.fluid_solar, check_mode):
            fb.add_missing_fluid(self.component, 'fluid_solar')

        for slot in ['tp', 'te_in', 'te_out']:
            if self.component.is_sensor_missing(slot, check_mode):
                fb.add_missing_sensor(self.component, slot, check_mode)

        slot, info_name = 'vf', 'position'
        if not self.component.is_sensor_missing('vf', check_mode):
            if self.component.vf.is_info_missing(info_name):
                fb.add_missing_sensor_info(self.component, slot, info_name)

        return fb

    def _calc(self):
        """
        Returns
        -------
        Dict with key 'mf' : pd.Series
            Calculated mass flow.
        """
        fluid = self.component.fluid_solar
        vf = self.component.vf.data
        te_in = self.component.te_in.data
        te_out = self.component.te_out.data
        pos = self.component.vf.info['position'].m_as('')

        rho = fluid.get_density(te=_get_weighted_temperature(te_in, te_out, 1 - pos, pos))
        mf = vf * rho

        return {'mf': mf.pint.to('kg s**-1')}


# ----------------------------------------------------------------------------------------------------------------------
# Solar Position

class SolarPosition(CoreAlgorithm):
    """For Plant: Calculates solar angles (azimuth, elevation, zenith).
    """

    def define_strategies(self):
        return [
            StrategySolarPosition_pvlib(self.component),
        ]


# noinspection PyArgumentList
class StrategySolarPosition_pvlib(VirtualSensorStrategy):
    name = 'Calculate solar position using pvlib'

    def _get_feedback(self, check_mode):
        fb = CoreMethodFeedback()
        for attrib in ['latitude', 'longitude']:
            if self.component.is_attrib_missing(attrib):
                fb.add_missing_attrib(self.component, attrib)
        return fb

    def _calc(self):
        """Calculates solar angles (azimuth, elevation, zenith), based on pvlib.
        https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.solarposition.get_solarposition.html

        Returns
        -------
        azimuth, zenitz, apparenzt_zenith, elevation, apparent_elevation : pd.Series
            Angles defining the solar position.
        """
        p = self.plant
        longitude = p.longitude.m_as('deg')
        latitude = p.latitude.m_as('deg')
        elevation = None if (p.elevation is None) else p.elevation.m_as('m')
        te_amb = p.te_amb
        if te_amb is None:
            # returns pd.DataFrame
            sol_pos = pvlib.solarposition.get_solarposition(time=p.time_index,
                                                            latitude=latitude,
                                                            longitude=longitude,
                                                            altitude=elevation)
        else:
            te_amb = te_amb.data.pint.to('degC')
            # 12 degC is the pvlib default in case no ambient temperature is known
            te_amb = te_amb.fillna(12).astype('float64').to_numpy()
            sol_pos = pvlib.solarposition.get_solarposition(time=p.time_index,
                                                            latitude=latitude,
                                                            longitude=longitude,
                                                            altitude=elevation,
                                                            temperature=te_amb)

        return {'azimuth': uu.to_s(sol_pos['azimuth'], 'deg'),
                'zenith': uu.to_s(sol_pos['zenith'], 'deg'),
                'apparent_zenith': uu.to_s(sol_pos['apparent_zenith'], 'deg'),
                'elevation': uu.to_s(sol_pos['elevation'], 'deg'),
                'apparent_elevation': uu.to_s(sol_pos['apparent_elevation'], 'deg'),
                }


# ----------------------------------------------------------------------------------------------------------------------
# Dew Point Temperature

# class DewPointTemperature(CoreAlgorithm):
#     """Ambient dew point temperature for Plant.
#     """
#
#     def define_strategies(self):
#         return [
#             StrategyDewPointFromSensor(self.component),
#             StrategyDewPointFromTemperatureHumidty(self.component),
#         ]
#
#
# class StrategyDewPointFromSensor(VirtualSensorStrategy):
#     """Feedthrough strategy, taking dew point from a Plant `te_dew_amb` real sensor.
#     """
#     name = 'Calculate dew point from real sensor'
#     use_real_sensor = True
#
#     def _calc(self):
#         return {'te_dew_amb': None}
#
#     def _get_feedback(self, check_mode):
#         """Make sure real sensor 'te_dew' exists in Plant.
#         """
#         r = CoreMethodFeedback()
#         if self.component.is_real_slot_missing('te_dew_amb', check_mode):
#             r.add_own(AlgoProblem(ProblemType.component_slot,
#                                   self.component, 'te_dew_amb', 'Sensor is None or virtual.'))
#         return r
#
#
# class StrategyDewPointFromTemperatureHumidty(VirtualSensorStrategy):
#     """Calculates ambient dew point temperature based on ambient temperature and ambient relative humidity of component.
#     """
#     name = 'Calculate dew point temperature from air temperature and relative humidity'
#
#     def _get_feedback(self, check_mode):
#         r = CoreMethodFeedback()
#         for slot in ['te_amb', 'rh_amb']:
#             if self.component.is_slot_missing(slot, check_mode):
#                 r.add_own(AlgoProblem(ProblemType.component_slot,
#                                       self.component, slot, 'Sensor missing.'))
#         return r
#
#     def _calc(self):
#         """Calculates ambient dew point temperature based on ambient temperature and ambient relative humidity of component.
#
#         Returns
#         -------
#         te_dew : pd.Series
#             Calculated ambient dew point temperature as pd.Series with dtype pint.
#         """
#         p = self.component
#         te_amb = p.te_amb.q_as('degC')
#         rh_amb = p.rh_amb.q_as('')
#
#         te_dew = dewpoint_from_relative_humidity(te_amb, rh_amb)
#
#         return {'te_dew_amb': uu.to_s(te_dew, 'degC')}


# ----------------------------------------------------------------------------------------------------------------------
# DNI extraterrestrial

# class DNIExtra(CoreAlgorithm):
#     """Calculate extraterrestrial solar radiation.
#     """
#
#     def define_strategies(self):
#         return [
#             StrategyDNIExtra_pvlib(self.component),
#         ]
#
#
# class StrategyDNIExtra_pvlib(VirtualSensorStrategy):
#     name = 'Calculate extraterrestrial solar radiation using pvlib'
#
#     def _get_feedback(self, check_mode):
#         # Only depends on plant time_index, which we assume here is always available.
#         return CoreMethodFeedback()
#
#     def _calc(self):
#         """Calculates extraterrestrial solar radiation using pvlib function.
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.get_extra_radiation.html
#
#         Returns
#         -------
#         dni_extra : pd.Series
#             Extraterrestrial solar radiation in W/m².
#         """
#         dni_extra = pvlib.irradiance.get_extra_radiation(self.plant.time_index)
#
#         return {'dni_extra': to_rd(dni_extra)}


# ----------------------------------------------------------------------------------------------------------------------
# Airmass

# class Airmass(CoreAlgorithm):
#     """Calculates relative and absolute airmass for Plant.
#     """
#
#     def define_strategies(self):
#         return [
#             StrategyAirmass_pvlib(self.component),
#         ]
#
#
# class StrategyAirmass_pvlib(VirtualSensorStrategy):
#     name = 'Calculate airmass using pvlib'
#
#     def _get_feedback(self, check_mode):
#         r = CoreMethodFeedback()
#         if self.component.is_slot_missing('sun_apparent_zenith', check_mode):
#             r.add_own(AlgoProblem(ProblemType.component_attrib, 'sun_apparent_zenith'))
#
#         return r
#
#     def _calc(self):
#         """Calculate absolute airmass using pvlib function.
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.atmosphere.get_absolute_airmass.html
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.atmosphere.get_relative_airmass.html
#
#         Returns
#         -------
#         rel_airmass : pd.Series
#             Relative airmass (numeric value).
#         abs_airmass : pd.Series
#             Absolute, pressure-corrected airmass (numeric value).
#         """
#         p = self.plant
#         rel_airmass = pvlib.atmosphere.get_relative_airmass(zenith=p.sun_apparent_zenith.s_as('deg'))
#         abs_airmass = pvlib.atmosphere.get_absolute_airmass(airmass_relative=rel_airmass)
#
#         return {'rel_airmass': rel_airmass.astype('pint[dimensionless]'),
#                 'abs_airmass': abs_airmass.astype('pint[dimensionless]')}


# ----------------------------------------------------------------------------------------------------------------------
# Linke Turbidity

# class LinkeTurbidity(CoreAlgorithm):
#     def define_strategies(self):
#         return [
#             StrategyLinkeTurbidity_pvlib(self.component),
#         ]
#
#
# class StrategyLinkeTurbidity_pvlib(VirtualSensorStrategy):
#     """For Plant, calculate Linke turbidity.
#     """
#     name = 'Calculate Linke turbidity from pvlib'
#
#     def _get_feedback(self, check_mode):
#         r = CoreMethodFeedback()
#         for attrib in ['latitude', 'longitude']:
#             if self.component.is_attrib_missing(attrib):
#                 r.add_own(AlgoProblem(ProblemType.component_attrib, self.component, attrib))
#         return r
#
#     def _calc(self):
#         """Calculate Linke turbidity using pvlib, required for clearsky irradiance calculation.
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.lookup_linke_turbidity.html#pvlib.clearsky.lookup_linke_turbidity
#
#         Returns
#         -------
#         linke_turbidity : pd.Series, Linke turbidity
#         """
#         p = self.plant
# Catch "divide by zero" warning that occurs naturally at very low sun angles, not caught in pvlib
#  with warnings.filterwarnings("ignore", category=RuntimeWarning):
#
#         linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(p.time_index,
#                                                              p.latitude.m_as('deg'),
#                                                              p.longitude.m_as('deg'))
#         return {'linke_turbidity': uu.to_s(linke_turbidity, 'dimensionless')}


# ----------------------------------------------------------------------------------------------------------------------
# Clearsky Radiation

# class ClearskyRadiation(CoreAlgorithm):
#     """Clearsky global horizontal irradiance and DNI.
#     """
#
#     def define_strategies(self):
#         return [
#             StrategyClearskyRadiation_pvlib(self.component),
#         ]
#
#
# class StrategyClearskyRadiation_pvlib(VirtualSensorStrategy):
#     """For Plants and Arrays, calculate clearsky global horizontal irradiance and DNI using pvlib.
#     """
#     name = 'Calculate clearsky radiation from pvlib'
#
#     def _get_feedback(self, check_mode):
#         r = CoreMethodFeedback()
#         for slot in ['sun_apparent_zenith', 'abs_airmass', 'linke_turbidity', 'rd_dni_extra']:
#             if self.component.is_slot_missing(slot, check_mode):
#                 r.add_own(AlgoProblem(ProblemType.component_slot,
#                                       self.component, slot, 'Sensor missing.'))
#         return r
#
#     def _calc(self):
#         """Calculate clearsky global horizontal irradiance and DNI using pvlib.
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.ineichen.html#pvlib.clearsky.ineichen
#         Alternative models:
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.haurwitz.html
#         https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.clearsky.simplified_solis.html
#
#         Returns
#         -------
#         rd_ghi_clearsky : pd.Series
#             Global horizontal clearsky radiation
#         rd_dni_clearsky : pd.Series
#             Clearsky DNI radiation
#         """
#         p = self.plant
#         elevation = 0 if p.elevation is None else p.elevation.m_as('m')
#         clearsky = pvlib.clearsky.ineichen(p.sun_apparent_zenith.m_as('deg'),
#                                         p.abs_airmass.m_as(''),
#                                         p.linke_turbidity.m_as('dimensionless'),
#                                         altitude,
#                                         p.rd_dni_extra.m_as('W m**-2'))
#
#         return {'ghi_clearsky': to_rd(clearsky['ghi']),
#                 'dni_clearsky': to_rd(clearsky['dni'])}


# ----------------------------------------------------------------------------------------------------------------------
# Horizontal / Plant Radiation

class HorizontalIrradiances(CoreAlgorithm):
    """For a Plant, calculate horizontal irradiance components from its radiation input slots.
    """

    def define_strategies(self):
        # Refactor like TiltedIrradiances, if needed
        raise NotImplementedError()
        # return [
        # ]

    # def _core(self):
    #     """Calculate component horizontal irradiance components.
    # 
    #     Returns
    #     -------
    #     rd_ghi : pd.Series
    #         Global horizontal irradiance
    #     rd_bhi : pd.Series
    #         Beam horizontal irradiance
    #     rd_dhi : pd.Series
    #         Diffuse horizontal irradiance
    #     rd_dni : pd.Series
    #         DNI irradiance
    #     """
    #     p = self.component
    #     rc = RadiationConversionHorizontal(plant=p,
    #                                        in_global=p.in_global,
    #                                        in_beam=p.in_beam,
    #                                        in_diffuse=p.in_diffuse,
    #                                        in_dni=p.in_dni)
    #     rd_ghi, rd_bhi, rd_dhi, rd_dni = rc.get_irradiance_components()
    #     return rd_ghi, rd_bhi, rd_dhi, rd_dni
    # 
    # def _do_assert(self, check_mode):
    #     assert validate_radiation_inputs(self.component)[0]


# ----------------------------------------------------------------------------------------------------------------------
# Tilted / Array Radiation

class TiltedIrradiances(CoreAlgorithm):
    """Calculate Array tilted irradiance components from its radiation input slots (in_XX).

    Calculated outputs (sensor slots of Array):
    rd_gti : pd.Series
        Global tilted irradiance
    rd_bti : pd.Series
        Beam tilted irradiance
    rd_dti : pd.Series
        Diffuse tilted irradiance
    """

    def allowed_components(self):
        return Array,

    def define_strategies(self):
        return [
            StrategyTiltedIrradiance_feedthrough(self.component),
        ]
        # Add more strategies if needed:
        # poa:  Return plane of array irradiance components.
        #     return to_rd(*self._get_poa_irradiances())
        # detailed: Return all irradiance components using radiation modeling.
        #     return to_rd(*self._get_array_irradiances_detailed())


# noinspection PyArgumentList
class StrategyTiltedIrradiance_feedthrough(VirtualSensorStrategy):
    """Array tilted irradiance components using only available real sensors, no radiation modeling.
    """

    name = 'Tilted irradiance as feedthrough of real sensors'
    feedthrough_real_sensor = True

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        a = self.component

        input_pattern = rd.get_radiation_pattern(a)
        # global only
        if input_pattern == '1000':
            r.add_generic_slot_problem(a, f'Only global irradiance given, cannot calculate '
                                          f'beam and diffuse irradiances.')
            r.problem_slots.extend(['rd_bti', 'rd_dti'])
            r.success = True

        # beam + diffuse
        elif input_pattern == '0110':
            pass  # all good

        # beam + diffuse + DNI
        elif input_pattern == '0111':
            pass  # all good

        # global + beam + diffuse
        elif input_pattern in ['1110', '1111']:
            pass  # all good, nothing missing

        else:
            r.add_generic_slot_problem(a, f'Invalid radiation input pattern {input_pattern}')

        if not rd.same_orientation(a, a.in_global, a.in_beam, a.in_diffuse):
            r.add_missing_sensor_info(a, description='Array irradiances '
                                                     '"in_global", "in_beam", "in_diffuse" must have same '
                                                     'orientation as the array and among themselves')
        return r

    def _calc(self):
        """Returns global, beam, diffuse irradiances on array, only if input sensor and array orientations match.
        Does not do any further calculations like applying radiation models.
        Returns
        -------
        gti, bti, dti : numeric array
            Global, beam and diffuse tilted radiation components in W/m².
        """
        a = self.component
        glob, beam, diff, dni = rd.unpack_radiations(a)
        input_pattern = rd.get_radiation_pattern(a)
        gti, bti, dti = None, None, None

        # global only
        if input_pattern == '1000':
            gti = glob

        # beam + diffuse
        elif input_pattern == '0110':
            bti, dti = beam, diff
            gti = beam + diff

        # beam + diffuse + DNI
        elif input_pattern == '0111':
            bti, dti = beam, diff
            gti = beam + diff

        # global + beam + diffuse
        elif input_pattern in ['1110', '1111']:
            gti, bti, dti = glob, beam, diff

        else:
            raise CalculationError(
                f'Array irradiance calculation "{self}" only accepts input slots "global", or "beam + diffuse", '
                f'or "global + beam + diffuse". Got input pattern {input_pattern}. This should have caught by '
                f'self._get_feedback().')

        return {'rd_gti': rd.to_rd(gti),
                'rd_bti': rd.to_rd(bti),
                'rd_dti': rd.to_rd(dti)}

    # def get_poa_irradiances(component, **kwargs):
    #     rc = RadiationConversionTilted(component=component, strategy='poa',
    #                                    in_global=component.in_global, in_beam=component.in_beam,
    #                                    in_diffuse=component.in_diffuse, in_dni=component.in_dni,
    #                                    **kwargs)
    #     dni, poa_diff_iso, poa_diff_circumsolar, poa_diff_horizon = rc.get_irradiance_components()
    #     return dni, poa_diff_iso, poa_diff_circumsolar, poa_diff_horizon

    # rd_bti_iam not needed? Currently using AlgoIAM instead.
    # class CalcIAMRadiation(CoreAlgorithm):
    #     """Calculate incidence angle modifier (IAM) and IAM-corrected beam radiation for component.
    #     """
    #
    #     def __init__(self, component):
    #         self.component = component
    #         self._n_results = 2
    #
    #     def _core(self):
    #         """Calculate IAM and IAM-corrected beam radiation.
    #
    #         Returns
    #         -------
    #         iam : pd.Series
    #             Incidence Angle Modifier
    #         rd_bti_iam : pd.Series
    #             IAM-corrected (reduced) beam irradiance on component
    #         """
    #         ar = self.component
    #         iam = ar.collector.iam_method.get_iam(aoi=ar.aoi.data,
    #                                                    azimuth_diff=ar.component.sun_azimuth.data - ar.azim)
    #
    #         try:
    #             self.component.assert_verify_validate(AlgoCheckMode.config_and_data, 'rd_bti')
    #             rd_bti_iam = uu.to_numpy(iam) * self.component.rd_bti.data
    #         except AssertionError:
    #             rd_bti_iam = None
    #
    #         return iam, rd_bti_iam
    #
    #     def _do_assert(self, check_mode):
    #         assert not isinstance(self.component.collector, UninitialisedCollector)
    #         self.component.assert_verify_validate(check_mode, 'aoi', 'azim')
    #         self.component.component.assert_verify_validate(check_mode, 'sun_azimuth')


# ----------------------------------------------------------------------------------------------------------------------
# IAM Incidence Angle Modifier

class AlgoIAM(CoreAlgorithm):
    """Incidence angle modifier (IAM) for array's collector.
    """

    def allowed_components(self):
        return Array,

    def define_strategies(self):
        return [
            StrategyIAMFromCollector(self.component),
        ]


# noinspection PyArgumentList
class StrategyIAMFromCollector(VirtualSensorStrategy):
    """Calculate incidence angle modifier (IAM) based on IAM method defined in array's collector.
    """
    name = 'Calculate incidence angle modifier (IAM) from collector'

    def _calc(self):
        """Calculate IAM.

        Returns
        -------
        iam : pd.Series
            Incidence Angle Modifier
        """
        a = self.component
        p = self.plant
        iam = a.collector.iam_method.get_iam(aoi=a.aoi.data,
                                             azimuth_diff=p.sun_azimuth.data - a.azim)
        return {'iam': iam}

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        if not is_valid_collector(self.component.collector, check_mode):
            r.add_missing_collector(self.component, 'collector')

        slot = 'aoi'
        if self.component.is_sensor_missing(slot, check_mode):
            r.add_missing_sensor(self.component, slot, check_mode)

        attrib = 'azim'
        if self.component.is_attrib_missing(attrib):
            r.add_missing_attrib(self.component, attrib)

        slot = 'sun_azimuth'
        if self.plant.is_sensor_missing(slot, check_mode):
            r.add_missing_sensor(self.plant, slot, check_mode)

        return r


# ----------------------------------------------------------------------------------------------------------------------
# Angle of Incidence

class AngleOfIncidence(CoreAlgorithm):
    """Calculate the angle of incidence of sun on plane of component using pvlib function.
    """

    def allowed_components(self):
        return Array,

    def define_strategies(self):
        return [
            StrategyAOI_pvlib(self.component),
        ]


# noinspection PyArgumentList
class StrategyAOI_pvlib(VirtualSensorStrategy):
    name = 'Calculate angle of incidence (aoi) from pvlib'

    def _calc(self):
        """https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.aoi.html

        Returns
        -------
        aoi : pd.Series
            Angle of incidence
        """
        a = self.component
        p = self.plant
        aoi = pvlib.irradiance.aoi(surface_tilt=a.tilt.m_as('deg'),
                                   surface_azimuth=a.azim.m_as('deg'),
                                   solar_zenith=p.sun_zenith.m_as('deg'),
                                   solar_azimuth=p.sun_azimuth.m_as('deg'))
        return {'aoi': uu.to_s(aoi, 'deg')}

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        for slot in ['sun_zenith', 'sun_azimuth']:
            if self.plant.is_sensor_missing(slot, check_mode):
                r.add_missing_sensor(self.plant, slot, check_mode)

        for attrib in ['tilt', 'azim']:
            if self.component.is_attrib_missing(attrib):
                r.add_missing_attrib(self.component, attrib)

        return r


# ----------------------------------------------------------------------------------------------------------------------
# Internal Shading


class InternalShading(CoreAlgorithm):
    """Calculates internal shading (row-to-row shading) related virtual sensors of a collector component.
    """

    def allowed_components(self):
        return Array,

    def define_strategies(self):
        return [
            StrategyInternalShading_BanyAppelbaum(self.component),
            StrategyInternalShading_SlopedGround(self.component),
        ]


class StrategyInternalShading_BanyAppelbaum(VirtualSensorStrategy):
    name = 'Calculate internal shading based on Bany Appelbaum 1987 paper'

    def _calc(self):
        """Calculate internal shading (row-to-row shading) and several related quantities of a collector array.

        Returns
        -------
        Dict with str keys and pint-pandas Series as values.
        See :func:`calc_shading_BanyAppelbaum` for details.
        """
        a = self.component
        p = self.plant

        return calc_BanyAppelbaum_shading(
            collector_tilt=a.tilt,
            collector_azimuth=a.azim,
            collector_gross_length=a.collector.gross_length,
            collector_row_spacing=a.row_spacing,
            sun_azimuth=p.sun_azimuth.data,
            sun_apparent_elevation=p.sun_apparent_elevation.data,
            ground_tilt=a.ground_tilt,
            aoi=a.aoi.data,
            max_aoi_shadow=a.max_aoi_shadow,
            min_elevation_shadow=a.min_elevation_shadow,
        )

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        a = self.component

        for slot in ['sun_azimuth', 'sun_apparent_elevation']:
            if self.plant.is_sensor_missing(slot, check_mode):
                r.add_missing_sensor(self.plant, slot, check_mode)

        slot = 'aoi'
        if a.is_sensor_missing(slot, check_mode):
            r.add_missing_sensor(a, slot, check_mode)

        for attrib in ['tilt', 'azim', 'ground_tilt', 'ground_azim', 'row_spacing']:
            if a.is_attrib_missing(attrib):
                r.add_missing_attrib(a, attrib)

        if a.azim != a.ground_azim:
            r.add_generic_slot_problem(a, '''Skipping Bany Appelbaum shading algorithm because 
            ground and collector azimuth are not the same, so a more complex shading algorithm 
            such as the Sloped Ground algorithm must be used.''')

        if not is_valid_collector(a.collector, check_mode):
            r.add_missing_collector(a, 'collector')
        else:
            attrib = 'gross_length'
            if a.collector.is_attrib_missing(attrib):
                r.add_missing_attrib(a.collector, attrib)

        return r


class StrategyInternalShading_SlopedGround(VirtualSensorStrategy):
    name = '''Calculate internal shading based on the Sloped Ground algorithm, 
        an extension of the Bany Appelbaum 1987 paper. This algorithm supports collectors mounted on sloped ground, 
        allowing different ground and collector azimuth.'''

    def _calc(self):
        """Calculate internal shading for sloped ground, and several related virtual sensors.

        Returns
        -------
        Dict with str keys and pint-pandas Series as values.
        See :func:`calc_sloped_shading` for details.
        """
        a = self.component
        p = self.plant

        return calc_sloped_shading(
            collector_tilt=a.tilt,
            collector_azimuth=a.azim,
            collector_gross_length=a.collector.gross_length,
            collector_row_spacing=a.row_spacing,
            ground_tilt=a.ground_tilt,
            ground_azimuth=a.ground_azim,
            sun_azimuth=p.sun_azimuth.data,
            sun_apparent_elevation=p.sun_apparent_elevation.data,
            aoi=a.aoi.data,
            max_aoi_shadow=a.max_aoi_shadow,
            min_elevation_shadow=a.min_elevation_shadow,
        )

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        for slot in ['sun_zenith', 'sun_azimuth', 'sun_apparent_elevation']:
            if self.plant.is_sensor_missing(slot, check_mode):
                r.add_missing_sensor(self.plant, slot, check_mode)

        slot = 'aoi'
        if self.component.is_sensor_missing(slot, check_mode):
            r.add_missing_sensor(self.component, slot, check_mode)

        for attrib in ['tilt', 'azim', 'row_spacing', 'ground_tilt', 'ground_azim']:
            if self.component.is_attrib_missing(attrib):
                r.add_missing_attrib(self.component, attrib)

        if not is_valid_collector(self.component.collector, check_mode):
            r.add_missing_collector(self.component, 'collector')
        else:
            attrib = 'gross_length'
            if self.component.collector.is_attrib_missing(attrib):
                r.add_missing_attrib(self.component.collector, attrib)

        a = self.component
        try:
            gamma = a.azim - a.ground_azim
            epsilon = np.arctan(np.sin(gamma.m_as('rad')) * np.tan(a.ground_tilt.m_as('rad')))
            if np.cos(epsilon) < np.sin(a.tilt.m_as('rad')):
                r.add_generic_slot_problem(a,
                                           f'The tilt angle along the collectors ({Q(epsilon, "rad").m_as("deg"):.1f}°) '
                                           f'is less than the complementary collector tilt angle ({a.tilt.m_as("deg"):.1f}°):'
                                           'This geometry configuration is invalid and is not supported by the sloped ground shading algorithm.')
        except:
            r.add_generic_slot_problem(a, '''Unexpected error 
            while evaluating geometry constraint of sloped shading algorithm.''')

        return r


# noinspection PyArgumentList

# ----------------------------------------------------------------------------------------------------------------------
# Array Temperatures and Temperature Derivatives

class ArrayTemperatures(CoreAlgorithm):
    """Calculate mean operating temperature of collector component and its temperature derivative.
    """

    def allowed_components(self):
        return Array,

    def define_strategies(self):
        return [
            StrategyArrayTemperatures_savgol(self.component),
        ]


# noinspection PyArgumentList
class StrategyArrayTemperatures_savgol(VirtualSensorStrategy):
    name = 'Calculate array operating temperature and temperature derivative'

    def _calc(self):
        """Calculate mean operating temperature of collector component and its temperature derivative.

        Returns
        -------
        Dict with these keys and values:
        te_op : pd.Series
            Mean operating temperature
        te_op_deriv : pd.Series
            Derivative of mean operating temperature

        Notes
        -----
        Implementation explanation:
        `te_op` is smoothened with a Savitzky-Golay for more robust differentiation. Bad / noisy: te_op.diff()
        Mathematically, we just have (te(t_N) - t(t_0))/dt, for regularly spaced data.
        Using 'te_op_deriv' is preferred over this because instantaneous changes in `te_in` and `te_out`
        make `te_op` a bad predictor for real mean temperature.
        Integrating over a smoothened `te_op_deriv` is probably a better option, as the calculation then depends
        not only on 2 single measurements, avoiding negative effects like meas. uncertainty of single measurements,
        measurement delay and transport effects etc. So smoothing over all data should improve results.
        More research on this should be done, especially on non-regularly spaced data.
        """
        # Mean operating temperature
        a = self.component
        te_op = _get_weighted_temperature(a.te_in.data, a.te_out.data)
        te_op = pd.Series(uu.to_numpy(te_op, 'K'), index=a.plant.time_index)

        # Derivative of mean operating temperature
        mean_sampling_rate = a.plant.time_index.to_series().diff().min()
        # Filling NaNs, otherwise savgol fails. Downstream methods need to filter intervals with too many NaNs out.
        te_op.fillna(method='pad', inplace=True)
        te_op_deriv = scipy.signal.savgol_filter(te_op, mode='mirror', window_length=15, polyorder=3, deriv=1)
        te_op_deriv_final = te_op_deriv / mean_sampling_rate.total_seconds()  # now in K / s

        return {'te_op': uu.to_s(te_op, 'K'),
                'te_op_deriv': uu.to_s(te_op_deriv_final, 'K s**-1'),
                }

    def _get_feedback(self, check_mode):
        r = CoreMethodFeedback()
        for slot in ['te_in', 'te_out']:
            if self.component.is_sensor_missing(slot, check_mode):
                r.add_missing_sensor(self.component, slot, check_mode)

        return r


def _get_weighted_temperature(te1, te2, w1=0.5, w2=0.5):
    """Return weighted average between temperature pd.Series te1 and te2.
    Takes care of converting things to K before doing the weighting. Result will be unit-aware pd.Series in degC.
    """
    # te_weighted = w1 * te1.pint.to('K') + w2 * te2.pint.to('K')
    # return uu.to_s(te_weighted, 'degC')
    # This greatly improves speed, especially in presence of many NaNs in data
    te_weighted = w1 * te1.pint.to('K').astype('float64') + w2 * te2.pint.to('K').astype('float64')
    return uu.to_s(te_weighted, 'K')
