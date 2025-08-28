from abc import ABC, abstractmethod
import numpy as np
import enum

import pvlib
from sunpeek.common.errors import VirtualSensorConfigurationError, CalculationError
from sunpeek.common.unit_uncertainty import to_s


## Utility functions

def get_radiation_inputs(component):
    """Return list with the 4 standard input slots of an Array of Plant.
    """
    return [component.in_global, component.in_beam, component.in_diffuse, component.in_dni]


def unpack_radiations(component):
    """Tries to read radiation as numeric value from self attributes (Sensor) in unit W/m**2.
    Useful to prepare input sensors for radiation converters.
    Returns
    -------
    tuple : pd.Series
        For each Sensor, returns pd.Series of Sensor.data, converted to W/m², None if Sensor is None.
    """
    return (None if elem is None else elem.m_as('W m**-2') for elem in get_radiation_inputs(component))


def to_rd(*args):
    """Converts numeric inputs to pd.Series with pint dtype W/m².
    Useful to return radiation converter results.
    """
    out = *(None if elem is None else to_s(elem, unit_str='W m**-2') for elem in args),
    out = out[0] if len(out) == 1 else out
    return out


def get_radiation_pattern(component):
    """Returns input pattern as string, where 1 if input is not None, else 0.
    Example: beam and diffuse radiation given, while global and DNI are None: pattern=='0110'.
    """
    is_given = [x is not None for x in get_radiation_inputs(component)]
    return f'{sum([x * np.power(10, 3 - i) for i, x in enumerate(is_given)]):04d}'


# def _get_radiation_input_pattern(*args):
#     """Returns input pattern as string, where 1 if input is not None, else 0.
#     Example: beam and diffuse radiation given, while global and DNI are None: pattern=='0110'.
#     """
#     is_given = [x is not None for x in args]
#     return f'{sum([x * np.power(10, 3 - i) for i, x in enumerate(is_given)]):04d}'


def _get_orientation(c_in):
    """Returns tilt and orientation of a cmp.Array or a cmp.Sensor, assuming a radiation sensor for global, beam or diffuse (not for dni)

    Parameters
    ----------
    c_in : Sensor or Array

    Returns
    -------
    tilt: tilt angle in degrees, or None if input is None.
    azim: azim angle in degrees, or None if input is None.
    """
    if c_in is None:
        return None
    return c_in.orientation['tilt'], c_in.orientation['azim']


def is_horizontal(*args):
    """Returns tuple with bool for each arg.
    True if arg is horizontal (sensor.info.tilt==0 or array.tilt==0), False otherwise.
    """
    # return *(None if elem is None else (_get_orientation(elem) == 0) for elem in args),
    return [None if elem is None else (_get_orientation(elem) == 0) for elem in args]


def same_orientation(*args):
    """Checks whether two radiation sensors or arrays have same tilt & orientation.

    Parameters
    ----------
    args : Sensor or Array

    Returns
    -------
    True if either all args are horizontal (tilt==0) or tilt and orientation are all the same.
    """
    args = [x for x in args if x is not None]

    orientations_available = [x.has_orientation() for x in args]
    if not all(orientations_available):
        return False

    # if all(_is_horizontal(*args)):
    #     return True
    #
    # tilts = {_get_orientation(x)[0] for x in args}
    # azims = {_get_orientation(x)[1] for x in args}

    tilts = {_get_orientation(x)[0] for x in args if x is not None}
    azims = {_get_orientation(x)[1] for x in args if x is not None}

    return len(tilts) == 1 and len(azims) == 1


## Elementary functions for radiation converter

def _get_aoi(plant, tilt, azim):
    # TODO add docstring
    # tilt, azim : array-likes in degrees
    # Returns: angle of incidence in degrees
    # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.aoi.html
    aoi = pvlib.irradiance.aoi(surface_tilt=tilt,
                               surface_azimuth=azim,
                               solar_zenith=plant.sun_zenith.m_as('deg'),
                               solar_azimuth=plant.sun_azimuth.m_as('deg'))
    return aoi

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_dni_from_ghi(plant, ghi):
#     # TODO add docstring
#
#     # ghi : array-like in W/m²
#     # Decomposition
#     # DNI from global horitzonal (ghi) using dirindex model
#     # Returns: DNI in W/m²
#     # case [b] in design https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#     # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.dirindex.html
#     # TODO Philip Note that dirindex needs timeseries data! (vector of at least length 2), may not be case for all vs calculations
#     #  https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.irradiance.dirindex.html
#     # TODO Philip I think we should have a parameter for radiation decompositon model to allow for other models in the future, e.g. https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.irradiance.erbs.html
#     #  decomposition models are usually very easy to implement (e.g. Engerer)
#     dni = pvlib.irradiance.dirindex(ghi=ghi,
#                                  ghi_clearsky=plant.rd_ghi_clearsky.m_as('W m**-2'),
#                                  dni_clearsky=plant.rd_dni_clearsky.m_as('W m**-2'),
#                                  zenith=plant.sun_zenith.m_as('deg'),
#                                  times=plant.time_index)
#     return dni


# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_beam_from_dni(plant, dni, tilt=0, azim=180):
#     # TODO add docstring
#     # Calculates beam irradiance on arbitrary surface (tilt, azim) from DNI
#     # Returns: beam irradiane (bhi or bti, depending on tilt) in W/m²
#
#     bti = pvlib.irradiance.beam_component(surface_tilt=tilt,
#                                        surface_azimuth=azim,
#                                        solar_zenith=plant.sun_zenith.m_as('deg'),
#                                        solar_azimuth=plant.sun_azimuth.m_as('deg'),
#                                        dni=dni)
#     return bti

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_horizontal_from_ghi(plant, ghi, dni=None):
#     # TODO Philip - add a function _get_horizontal_from_ghi_dni (confusing if we have _get_horizontal_from_ghi_bhi)
#     # TODO add docstring
#
#     # ghi : array-like in W/m²
#     # Returns: ghi, bhi, dhi, DNI in W/m²
#     # Decomposition
#
#     if dni is None:
#         dni = _get_dni_from_ghi(plant, ghi)
#     bhi = _get_beam_from_dni(plant, dni)
#     # bhi = pvlib.irradiance.beam_component(0, 180, plant.sun_zenith.to('deg'), plant.sun_azimuth.to('deg'), dni)
#     dhi = ghi - bhi
#     return ghi, bhi, dhi, dni


# def _get_horizontal_from_gti(plant, gti, tilt, azim):
#     """Inverse decomposition. Returns horizontal components from global tilted irradiance with given tilt and azimuth.
#
#     Parameters
#     ----------
#     gti : numeric array
#         Global titled irradiance in W/m².
#     tilt : float
#     azim : float
#         Tilt and azimuth angle at which the global tilted irradiance is given.
#
#     Returns
#     -------
#     global, beam, diffuse and DNI irradiances
#     """
#     # TODO add docstring
#     # TODO Philip: "Model performance is poor for AOI greater than approximately 80 degrees and plane of array irradiance greater than approximately 200 W/m^2."
#     #   (https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.irradiance.gti_dirint.html) - do we need a virtual sensors which tells us if conversion is ok? and also some
#     #   basic quality checks (don't know if gti_dirint does this?)
#     # gti : array-like in W/m²
#     # tilt, azim : in degrees
#     # albedo: currently fixed to pvlib default of 0.25
#     # Returns: ghi, bhi, dhi, DNI in W/m²
#     # Case [a] in design https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#     # Inverse decomposition
#     # Horizontal components (ghi, dhi, DNI) from global tilted (gti) using gti_dirint model
#     # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.gti_dirint.html
#
#     # TODO calculate_gt_90 should be True, but then gti_dirint throws IndexError
#     # gti[gti<0]=0
#
#     # TODO use plant dew point if available
#     horiz = pvlib.irradiance.gti_dirint(poa_global=gti,
#                                      aoi=_get_aoi(plant, tilt, azim),
#                                      solar_zenith=plant.sun_zenith.m_as('deg'),
#                                      solar_azimuth=plant.sun_azimuth.m_as('deg'),
#                                      times=plant.time_index,
#                                      surface_tilt=tilt,
#                                      surface_azimuth=azim,
#                                      calculate_gt_90=False,
#                                      use_delta_kt_prime=False,
#                                      model='perez',
#                                      model_perez='allsitescomposite1990',
#                                      temp_dew=None,
#                                      albedo=.25,
#                                      max_iterations=50)
#
#     horiz.index = plant.time_index
#     horiz = horiz.assign(gti=gti)
#     # horiz.plot()
#
#     bhi = horiz['ghi'] - horiz['dhi']
#     return horiz['ghi'], bhi, horiz['dhi'], horiz['dni']
#
#
# def _get_horizontal_from_ghi_dhi(plant, ghi, dhi):
#     # TODO add docstring
#     # ghi, dhi : array-like in W/m²
#     # Returns: ghi, bhi, dhi, DNI in W/m²
#
#     dni = _get_dni_from_ghi_dhi(plant, ghi, dhi)
#     bhi = _get_beam_from_dni(plant, dni)
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_dhi_dni(plant, dhi, dni):
#     # TODO add docstring
#     # Calculates global irradiance components from diffuse horizontal and DNI
#
#     bhi = _get_beam_from_dni(plant, dni)
#     ghi = bhi + dhi
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_dti_dni(plant, dti, dni):
#     # TODO add docstring
#     # Calculates global irradiance components from diffuse tilted and DNI
#     # by calculating global tilted irradiance in plane of dti sensor, then converting that gti to horizontal.
#
#     tilt, azim = _get_orientation(plant.in_diffuse)
#     bti = _get_beam_from_dni(plant, dni, tilt, azim)
#     gti = bti + dti
#     ghi, bhi, dhi, dni = _get_horizontal_from_gti(plant, gti, tilt, azim)
#
#     return ghi, bhi, dhi, dni


# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_dni_from_ghi_dhi(plant, ghi, dhi):
#     # TODO add docstring
#
#     # ghi, dhi : array-like in W/m²
#     # Returns: DNI in W/m²
#     # Case [c] in design https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#     # uses pvlib dni: https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.dni.html
#
#     dni = pvlib.irradiance.dni(ghi=ghi,
#                             dhi=dhi,
#                             zenith=plant.sun_zenith.m_as('deg'),
#                             clearsky_dni=plant.rd_dni_clearsky.m_as('W m**-2'))
#     return dni


# def _get_horizontal_from_ghi_bhi(plant, ghi, bhi):
#     # TODO add docstring
#     # Calculates horizontal irradiance components from ghi and bhi
#     # ghi, bhi : array-like in W/m²
#     # Returns: ghi, bhi, dhi, DNI in W/m²
#     dhi = ghi - bhi
#     dni = _get_dni_from_ghi_dhi(plant, ghi, dhi)
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_ghi_bti(plant, ghi, bti, tilt, azim):
#     # TODO add docstring
#     # Calculates horizontal irradiance components from ghi and bti
#     # ghi, bhi : array-like in W/m²
#     # Returns: ghi, bhi, dhi, DNI in W/m²
#     dni = _get_dni_from_beam(plant, bti, tilt, azim)
#     bhi = _get_beam_from_dni(plant, dni)
#     dhi = ghi - bhi
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_bti_dti(plant, bti, dti):
#     # TODO add docstring
#     # Calculate hotizontal irradiance components from beam and diffuse tilted radiations.
#     # This works also if bti and dti do not have the same tile & orientation.
#
#     tilt_d, azim_d = _get_orientation(plant.in_diffuse)
#     if same_orientation(plant.in_beam, plant.in_diffuse):
#         gti = bti + dti
#     else:
#         # Convert bti to the plane where dti is given
#         tilt_b, azim_b = _get_orientation(plant.in_beam)
#         dni = _get_dni_from_beam(plant, bti, tilt_b, azim_b)
#         bti_d = _get_beam_from_dni(plant, dni, tilt_d, azim_d)
#         gti = bti_d + dti
#
#     ghi, bhi, dhi, dni = _get_horizontal_from_gti(plant, gti, tilt_d, azim_d)
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_bti_dhi(plant, bti, dhi):
#     # TODO add docstring
#     # Calculates horizontal irradiance components from beam tilted and diffuse horizontal measurements.
#
#     tilt, azim = _get_orientation(plant.in_beam)
#     dni = _get_dni_from_beam(plant, bti, tilt, azim)
#     bhi = _get_beam_from_dni(plant, dni)
#     ghi = bhi + dhi
#
#     return ghi, bhi, dhi, dni
#
#
# def _get_horizontal_from_bhi_dti(plant, bhi, dti):
#     # TODO add docstring
#     # Calcualtes horizontal irradiance components from beam horizontal and diffuse tilted
#
#     dni = _get_dni_from_beam(plant, bhi)
#     tilt, azim = _get_orientation(plant.in_diffuse)
#     bti = _get_beam_from_dni(plant, dni, tilt, azim)
#     gti = dti + bti
#     ghi, bhi, dhi, dni = _get_horizontal_from_gti(plant, gti, tilt, azim)
#     return ghi, bhi, dhi, dni


# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_dni_from_beam(plant, bti, tilt=0, azim=180, max_zenith=87):
#     # TODO add docstring
#     # Calculates DNI from beam horizontal or beam tilted irradiance
#     # ghi, bhi : array-like in W/m²
#     # tilt, azim
#     # Returns: DNI in W/m²
#     # max_zenith follows recommendation in
#     # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.dirindex.html
#     aoi = _get_aoi(plant, tilt, azim)
#     aoi_ok = (aoi <= max_zenith)
#     dni = np.zeros_like(bti)
#     dni[aoi_ok] = bti[aoi_ok] / np.cos(aoi[aoi_ok])
#     return dni


# def _get_horizontal_from_bhi_dhi(plant, bhi, dhi):
#     # TODO add docstring
#     ghi = dhi - bhi
#     dni = _get_dni_from_ghi_dhi(plant, ghi, dhi)
#     return ghi, bhi, dhi, dni


## Radiation conversion classes

# class RadiationConversion(ABC):
#     def __init__(self, in_global, in_beam, in_diffuse, in_dni):
#         self.in_global = in_global
#         self.in_beam = in_beam
#         self.in_diffuse = in_diffuse
#         self.in_dni = in_dni
#         self.input_pattern = self.get_radiation_pattern()
#
#     @abstractmethod
#     def get_irradiance_components(self):
#         pass

# @staticmethod
# def unpack_radiations(*args):
#     """Tries to read radiation as numeric value from Sensor.data (of 1 or several cmp.Sensors) in unit W/m**2.
#     Useful to prepare component sensors for radiation converter.
#     Parameters
#     ----------
#     args : cmp.Sensor
#     Returns
#     -------
#     tuple : pd.Series
#         For each Sensor, returns pd.Series of Sensor.data, converted to W/m², None if Sensor is None.
#     """
#     return (None if elem is None else elem.m_as('W m**-2') for elem in args)

# def _is_horizontal(self):
#     """Returns tuple with bool for each of the radiation Sensors self.in_global, .in_beam, .in_diffuse.
#     """
#     return is_horizontal(self.in_global, self.in_beam, self.in_diffuse)


# class RadiationConversionHorizontal(RadiationConversion):
#     """Calculates horizontal irradiance components (global, beam, diffuse, DNI) for the plant.
#     """
#
#     def __init__(self, plant, *args, **kwargs):
#         self.plant = plant
#         super().__init__(*args, **kwargs)
#         return
#
#     def get_irradiance_components(self):
#         return self.get_horizontal_irradiances()
#
#     def get_horizontal_irradiances(self):
#         """Calculates horizontal irradiance components (global, beam, diffuse, DNI) for the plant.
#         radiation input sensors
#         TODO correct docstring, state the selection pattern for the different cases
#         Returns horizontal irradiance components for global, beam / direct, diffuse and DNI.
#         Returns: horizontal ghi, bhi, dhi, dni
#         Logic is described in detail in https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#         """
#
#         glob, beam, diff, dni = self.unpack_radiations()
#         is_glob_horizontal, is_beam_horizontal, is_diff_horizontal = self._is_horizontal()
#
#         # self.input_pattern:
#         # 1 input:
#         #  1000 ok, global only
#         #  0100, 0010, 0001: not ok, not enough inputs
#         # 2 inputs:
#         #  1100 ok, global + beam
#         #  1010 ok, global + diffuse
#         #  1001 ok, global + DNI
#         #  0110 ok, beam + diffuse
#         #  0011 ok, diffuse + DNI
#         # 3 inputs: not yet implemented (
#         #  1110 ok, global + beam + diffuse -> same as 0110 (ignore global)
#         #  1101 ok, global + beam + dni     -> same as 1001 (ignore beam)
#         #  1011 ok, global + diffuse + dni  -> same as 0101 (ignore global)
#         #  0111 ok, beam + diffuse + dni    -> same as 0011 (ignore beam)
#         # 4 inputs: not yet implemented
#         #  1111 ok, global + beam + diffuse + dni -> same as 0101 (ignore global and beam)
#
#         # raise NotImplementedError
#
#         # no radiation inputs
#         if self.input_pattern == '0000':
#             ghi, bhi, dhi, dni = None, None, None, None
#         # TODO Philip - I suggest to change to selection order for the overdetermined case,
#         #  see https://gitlab.com/sunpeek/sunpeek/-/issues/128
#         # global only
#         elif self.input_pattern == '1000':
#             if is_glob_horizontal:
#                 # Input glob is ghi: decomposition
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi(self.plant, glob)
#             else:
#                 # Input glob is some gti: inverse decomposition
#                 tilt, azim = _get_orientation(self.in_global)
#                 ghi, bhi, dhi, dni = _get_horizontal_from_gti(self.plant, glob, tilt, azim)
#
#         # global + beam
#         elif self.input_pattern == '1100':
#             if is_glob_horizontal and is_beam_horizontal:
#                 # Inputs are ghi and bhi
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi_bhi(self.plant, glob, beam)
#             elif is_glob_horizontal:
#                 # Inputs are ghi and bti
#                 tilt, azim = _get_orientation(self.in_beam)
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi_bti(self.plant, glob, beam, tilt, azim)
#             else:
#                 # TODO Philip - To ignore beam is not intuitive to me here
#                 #  1) calcuate ghi, use bhi as measured? or 2) use other model with gti, bti inputs?
#                 # Inputs are gti and (bhi or bti): beam input is ignored
#                 tilt, azim = _get_orientation(self.in_global)
#                 ghi, bhi, dhi, dni = _get_horizontal_from_gti(self.plant, glob, tilt, azim)
#
#         # global + diffuse
#         elif self.input_pattern == '1010':
#             if is_glob_horizontal and is_diff_horizontal:
#                 # Inputs are ghi and dhi
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi_dhi(self.plant, glob, diff)
#             elif is_glob_horizontal:
#                 # Inputs are ghi and dti: diffuse input is ignored
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi(self.plant, glob)
#             else:
#                 # TODO Philip - same problem as with ignoring beam:
#                 #  if gti and dti are in SAME plane --> calcuate + use beam
#                 # Inputs are gti and (dhi or dti): diffuse input is ignored
#                 tilt, azim = _get_orientation(self.in_global)
#                 ghi, bhi, dhi, dni = _get_horizontal_from_gti(self.plant, glob, tilt, azim)
#
#         # global + DNI
#         elif self.input_pattern == '1001':
#             if is_glob_horizontal:
#                 # Inputs are ghi and DNI
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi(self.plant, glob, dni)
#             else:
#                 # Inputs are gti and DNI
#                 tilt, azim = _get_orientation(self.in_global)
#                 ghi, bhi, dhi, dni = _get_horizontal_from_gti(self.plant, glob, tilt, azim)
#
#         # diffuse + DNI
#         elif self.input_pattern == '0011':
#             if is_diff_horizontal:
#                 # Inputs are dhi and DNI
#                 ghi, bhi, dhi, dni = _get_horizontal_from_dhi_dni(self.plant, diff, dni)
#             else:
#                 # Inputs are dti and DNI
#                 ghi, bhi, dhi, dni = _get_horizontal_from_dti_dni(self.plant, diff, dni)
#
#         # beam + diffuse (and other subsumed cases that include beam + diffuse)
#         elif self.input_pattern in ['0110', '1110', '0111', '1111']:
#             if is_beam_horizontal and is_diff_horizontal:
#                 # Inputs are bhi and dhi
#                 ghi, bhi, dhi, dni = _get_horizontal_from_ghi_bhi(self.plant, beam, diff)
#             elif ~is_beam_horizontal and ~is_diff_horizontal:
#                 # Inputs are bti and dti
#                 ghi, bhi, dhi, dni = _get_horizontal_from_bti_dti(self.plant, beam, diff)
#             elif is_diff_horizontal:
#                 # Inputs are bti and dhi
#                 ghi, bhi, dhi, dni = _get_horizontal_from_bti_dhi(self.plant, beam, diff)
#             else:
#                 # Inputs are bhi and dti
#                 ghi, bhi, dhi, dni = _get_horizontal_from_bhi_dti(self.plant, beam, diff)
#
#         elif self.input_pattern in ['0100', '0010', '0001', '0101']:
#             # Not permitted, cannot calculate horizontal radiation components with these inputs
#             # These cases should have been caught by assert_enough_radiation_inputs().
#             raise VirtualSensorConfigurationError(
#                 'Cannot calculate horizontal radiation components with the given radiation inputs.')
#         else:
#             raise NotImplementedError()
#
#         return to_rd(ghi, bhi, dhi, dni)


# TODO delete
# class TiltedStrategy(enum.Enum):
#     poa = 0  # Return plane of array irradiance components.
#     feedthrough = 1  # Return only input sensor values, if orientation matches; no radiation modeling.
#     detailed = 2  # Return all irradiance components using radiation modeling.


# class RadiationConversionTilted(RadiationConversion):
#     """
#     TODO update docstring
#     """
#
#     def __init__(self, array, strategy='feedthrough',
#                  use_diffuse_masking=True,
#                  use_beam_shading=True,
#                  ground_diffuse_strategy='ghi',
#                  ground_albedo=0.25,
#                  treat_circumsolar_as_diffuse=True,
#                  horizon_brightness_strategy='ignore',
#                  *args, **kwargs):
#         self.array = array
#         self.tilt = array.tilt.m_as('deg')
#         self.azim = array.azim.m_as('deg')
#         self.plant = array.plant
#         self.strategy = strategy
#         self.use_diffuse_masking = use_diffuse_masking
#         self.use_beam_shading = use_beam_shading
#         self.ground_diffuse_strategy = ground_diffuse_strategy
#         self.ground_albedo = ground_albedo
#         self.treat_circumsolar_as_diffuse = treat_circumsolar_as_diffuse
#         self.horizon_brightness_strategy = horizon_brightness_strategy
#         super().__init__(*args, **kwargs)
#         return
#
#     @property
#     def strategy(self):
#         return self._strategy
#
#     @strategy.setter
#     def strategy(self, val):
#         if val is not None:
#             self._strategy = TiltedStrategy[val]
#
#     def get_irradiance_components(self):
#         if self._strategy is TiltedStrategy.feedthrough:
#             return to_rd(*self._get_array_irradiances_feedthrough())
#         elif self.strategy is TiltedStrategy.poa:
#             return to_rd(*self._get_poa_irradiances())
#         elif self.strategy is TiltedStrategy.detailed:
#             return to_rd(*self._get_array_irradiances_detailed())
#         else:
#             return AttributeError(f'Invalid tilted strategy {self.strategy}.')

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_array_irradiances_detailed(self):
#     """Returns global, beam, diffuse irradiances on array, applying detailed modeling with plane-of-array irradiances.
#     Returns
#     -------
#     gti : numeric array
#       Global irradiance on array in W/m².
#     bti : numeric array
#       Beam / direct irradiance on array in W/m².
#     dti : numeric array
#       Diffuse irradiance on array in W/m².
#
#     Notes
#     -----
#     Calculates array irradiance components global, beam / direct and diffuse.
#     Components of poa diffuse (e.g. horizon brightness) can be combined specifically.
#     Calls _get_poa_irradiances() to yield DNI and poa diffuse components (diffuse sky, diffuse horizon etc.)
#     For diffuse masking, uses shadow_angle_midpoint, i.e. the angle at half of the collector's slant height.
#     """
#     # TODO Daniel would be good to get your ideas about details on how to calculate dti
#     # TODO Make sure array virtual sensors exist: shadow_angle_midpoint, internal_shading_fraction, plant.ghi
#     # TODO Philip - conversion strategies should be 'consistent', i.e. if we apply inverse, then forward direction for a sensor, this should return the sensor value
#     #   - step 1:
#     #   - a) using gti (in same plane as array) --> apply dirint --> keep gti, calculate bti based on DNI, "normalize" shares for iffuse_iso + diffuse_circ + diffuse_horz
#     #   - b) using gti (in different plane than array) --> apply dirint --> use perez model
#     #   - step 2:
#     #   - calcuate reduction (masking, horizon) RELATIVE to measurement at the top of the collector --> we need to define the default settings here
#     #   - later:
#     #   - alternatively, we could think of implementing our own radiation conversion model to make this consistent, e.g. like https://www.sciencedirect.com/science/article/pii/S0038092X21000633,
#     #     for the solar community it would be help to have a very general radiation conversion algorithm for all possible measurement setups
#
#     # Plane-of-array irradiance components
#     dni, poa_diffuse_iso, poa_diffuse_circ, poa_diffuse_horiz = self._get_poa_irradiances()
#     bti = _get_beam_from_dni(self.plant, dni, self.tilt, self.azim)
#
#     # Diffuse masking
#     if self.use_diffuse_masking:
#         # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.shading.sky_diffuse_passias.html
#         iso_blocked = pvlib.shading.sky_diffuse_passias(masking_angle=self.array.shadow_angle_midpoint.m_as('deg'))
#         poa_diffuse_iso *= np.ones_like(poa_diffuse_iso) - iso_blocked
#         # TODO Philip - This calculation is NOT correct, it does not take the tilt angle of the array into account!
#     dti = poa_diffuse_iso
#
#     # Circumsolar diffuse
#     if self.treat_circumsolar_as_diffuse:
#         dti += poa_diffuse_circ
#     else:  # treat circumsolar as beam
#         bti += poa_diffuse_circ
#
#     # Beam shading
#     if self.use_beam_shading:
#         bti *= np.ones_like(bti) - self.array.internal_shading_fraction.m_as('dimensionless')
#
#     # Horizon brightness
#     if self.horizon_brightness_strategy == 'ignore':
#         pass
#     else:
#         dti += poa_diffuse_horiz
#
#     # Ground diffuse
#     # TODO Philip - these models need to be consistent with the transposition model - I would include the options
#     #  - a) ground reflection as in Perez
#     #  - b) ignore ground reflection (substract this from the diffuse irradiance?)
#     #  - b) correct ground reflection (with view factor from sensors versus towards ground)
#     if self.ground_diffuse_strategy == 'ignore':
#         pass
#     elif self.ground_diffuse_strategy == 'ghi':
#         if self.plant.ghi is None:
#             raise VirtualSensorCalculationError(
#                 'Calculating array irradiances with strategy "ghi" requires plant.ghi to be not None.')
#             # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.get_ground_diffuse.html
#         dti += pvlib.irradiance.get_ground_diffuse(surface_tilt=self.tilt,
#                                                 ghi=self.plant.ghi.m_as('W m**-2'),
#                                                 albedo=self.ground_albedo)
#     else:
#         raise NotImplementedError
#
#     gti = bti + dti
#     return gti, bti, dti

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_poa_irradiances(self):
#     """Calculates in-plane radiation components from array radiation input sensors in_global, in_beam, in_diffuse,
#     in_dni. Returns tilted in-plane (poa, plane-of-array) irradiance components for DNI, sky and ground diffuse.
#     Returns
#     -------
#     rd_dni : numeric array
#       DNI (Direct Normal Irradiance) in W/m².
#     rd_poa_diffuse_sky : numeric array
#       Plane-of-array (poa) in-plane diffuse irradiance from the sky in W/m².
#     rd_poa_diffuse_ground : numeric array
#       Plane-of-array (poa) in-plane diffuse irradiance from the ground in W/m².
#
#     Note:
#     -----
#     Does not take beam shading and diffuse masking of the array into account.
#     Logic is described in https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#     """
#
#     glob, beam, diff, dni = self.unpack_radiations()
#     is_glob_horizontal, is_beam_horizontal, is_diff_horizontal = self.is_horizontal()
#
#     # no radiation inputs
#     if self.input_pattern == '0000':
#         dni, poa_diff_iso, poa_diff_circ, poa_diff_horiz = None, None, None, None
#     # global only
#     elif self.input_pattern == '1000':
#         if is_glob_horizontal:
#             # Input glob is ghi
#             dni, poa_diff_iso, poa_diff_circ, poa_diff_horiz = self._get_poa_from_ghi(glob)
#         else:
#             # Input glob is some gti: inverse decomposition
#             raise NotImplementedError
#             # tilt, azim = _get_sensor_orientation(array._in_glob)
#             # dni, poa_diff_iso, poa_diff_circ, poa_diff_horiz = _get_poa_from_gti(plant, glob, tilt, azim)
#     else:
#         # TODO implement more tilted radiation strategies here
#         raise NotImplementedError
#
#     return dni, poa_diff_iso, poa_diff_circ, poa_diff_horiz

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_poa_from_ghi(self, ghi):
#     # TODO add docstring
#     # Calculates plane-of-array radiation components from global horizontal irradiance / measurement.
#     # Combines decomposition (dirindex) and transposition (Perez)
#     # Returns plane-of-array irradiance, i.e. does not take beam shading and diffuse masking into account.
#     # Returns: DNI, isotropic diffuse, circumsolar diffuse, horizon brightness radiations, all in W/m²
#
#     dni = _get_dni_from_ghi(self.plant, ghi)
#     bhi = _get_beam_from_dni(self.plant, dni)
#     dhi = ghi - bhi
#     poa_diff_iso, poa_diff_circ, poa_diff_horiz = self._get_poadiffuse_from_dhi(dhi, dni)
#     return dni, poa_diff_iso, poa_diff_circ, poa_diff_horiz

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_poa_from_gti(self, gti):
#     # TODO add docstring
#     # Calculates plane-of-array radiation components from global tilted irradiance / measurement.
#     raise NotImplementedError
#     # tilt, azim = _get_sensor_orientation(array.in_global)
#     # gti_dirint

# To be uncommented, once radiation conversion for Arrays is implemented.
# def _get_poadiffuse_from_dhi(self, dhi, dni):
#     # TODO add docstring
#     # dhi, dni : array-like in W/m²
#     # Returns:
#     # --------
#     # poa_diff_iso : numeric
#     #   Tilted / poa isotropic diffuse radiation, in W/m²
#     # poa_diff_circ : numeric
#     #   Tilted / poa circumsolar radiation, in W/m²
#     # poa_diff_horiz : numeric
#     #   Tilted /poa horizon brightness radiation, in W/m²
#     # Transposition: Calculates sky diffuse irradiance in plane of array from global and diffuse horizontal.
#     # This implementation uses the Perez method:
#     # https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.irradiance.perez.html
#     # case [f] in design https://gitlab.com/sunpeek/sunpeek/-/issues/128/
#     # TODO Make sure the necessary sensors like plant.sun_apparent_zenit, plant.rel_airmass exist / not None
#
#     diffuse = pvlib.irradiance.perez(surface_tilt=self.tilt,
#                                   surface_azimuth=self.azim,
#                                   dhi=dhi,
#                                   dni=dni,
#                                   dni_extra=self.plant.rd_dni_extra.m_as('W m**-2'),
#                                   solar_zenith=self.plant.sun_apparent_zenith.m_as('deg'),
#                                   solar_azimuth=self.plant.sun_azimuth.m_as('deg'),
#                                   airmass=self.plant.rel_airmass.m_as(''),
#                                   return_components=True)
#     return diffuse['isotropic'], diffuse['circumsolar'], diffuse['horizon']

## old stuff
# pvlib surfaces (for Array definition)
# https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/irradiance.html?highlight=surface_albedos
# SURFACE_ALBEDOS = {'urban': 0.18,
#                    'grass': 0.20,
#                    'fresh grass': 0.26,
#                    'soil': 0.17,
#                    'sand': 0.40,
#                    'snow': 0.65,
#                    'fresh snow': 0.75,
#                    'asphalt': 0.12,
#                    'concrete': 0.30,
#                    'aluminum': 0.85,
#                    'copper': 0.74,
#                    'fresh steel': 0.35,
#                    'dirty steel': 0.08,
#                    'sea': 0.06}
