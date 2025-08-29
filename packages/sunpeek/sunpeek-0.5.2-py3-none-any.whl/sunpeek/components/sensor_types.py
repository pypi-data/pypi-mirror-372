"""
This module contains a the definitions of all SensorTypes which are used to provide unit compatibility and data sanity
checks, depending on what a sensor does. Normally Sensors inherit their SensorType from any SensorSlots they are mapped
into on a component, but sensors can also be created with a type explicitly.
"""

import sys
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common import common_units
from sunpeek.components.types import SensorType

# Some arguments to SensorType() are commented since uncertainty propagation is not implemented right now. Left
# commented for later, just in case.


fluid_temperature = SensorType(name='fluid_temperature',
                               description='Fluid temperature',
                               compatible_unit_str='°C',
                               lower_replace_min=Q(-20.0, 'degC'),
                               upper_replace_max=Q(200.0, 'degC'),
                               info_checks=None,
                               common_units=list(common_units.temperature),
                               )

ambient_temperature = SensorType(name='ambient_temperature',
                                 description='Ambient temperature',
                                 compatible_unit_str='°C',
                                 lower_replace_min=Q(-30.0, 'degC'),
                                 upper_replace_max=Q(60.0, 'degC'),
                                 info_checks=None,
                                 common_units=list(common_units.temperature),
                                 )

global_radiation = SensorType(name='global_radiation',
                              description='Global irradiance',
                              compatible_unit_str='W/m²',
                              lower_replace_min=Q(-10.0, 'watt / meter**2'),
                              lower_replace_max=Q(0.0, 'watt / meter**2'),
                              lower_replace_value=Q(0.0, 'watt / meter**2'),
                              upper_replace_max=Q(1700.0, 'watt / meter**2'),
                              info_checks={'tilt': {'unit': '°', 'minimum': 0, 'maximum': 90,
                                                    'description': 'Radiation sensor tilt angle.'},
                                           'azim': {'unit': '°', 'minimum': 0, 'maximum': 360,
                                                    'description': 'Radiation sensor azimuth angle.'}},
                              common_units=list(common_units.power / common_units.area),
                              )

direct_radiation = SensorType(name='direct_radiation',
                              description='Direct / beam irradiance',
                              compatible_unit_str='W/m²',
                              lower_replace_min=Q(-10.0, 'watt / meter**2'),
                              lower_replace_max=Q(0.0, 'watt / meter**2'),
                              lower_replace_value=Q(0.0, 'watt / meter**2'),
                              upper_replace_max=Q(1400.0, 'watt / meter**2'),
                              info_checks={'tilt': {'unit': '°', 'minimum': 0, 'maximum': 90,
                                                    'description': 'Radiation sensor tilt angle.'},
                                           'azim': {'unit': '°', 'minimum': 0, 'maximum': 360,
                                                    'description': 'Radiation sensor azimuth angle.'}},
                              common_units=list(common_units.power / common_units.area),
                              )

diffuse_radiation = SensorType(name='diffuse_radiation',
                               description='Diffuse irradiance',
                               compatible_unit_str='W/m²',
                               lower_replace_min=Q(-10.0, 'watt / meter**2'),
                               lower_replace_max=Q(0.0, 'watt / meter**2'),
                               lower_replace_value=Q(0.0, 'watt / meter**2'),
                               upper_replace_max=Q(1100.0, 'watt / meter**2'),
                               info_checks={'tilt': {'unit': '°', 'minimum': 0, 'maximum': 90,
                                                     'description': 'Radiation sensor tilt angle.'},
                                            'azim': {'unit': '°', 'minimum': 0, 'maximum': 360,
                                                     'description': 'Radiation sensor azimuth angle.'}},
                               common_units=list(common_units.power / common_units.area),
                               )

dni_radiation = SensorType(name='dni_radiation',
                           description='DNI (direct normal) irradiance',
                           compatible_unit_str='W/m²',
                           lower_replace_min=Q(-10.0, 'watt / meter**2'),
                           lower_replace_max=Q(0.0, 'watt / meter**2'),
                           lower_replace_value=Q(0.0, 'watt / meter**2'),
                           upper_replace_max=Q(1400.0, 'watt / meter**2'),
                           info_checks=None,
                           common_units=list(common_units.power / common_units.area),
                           )

thermal_power = SensorType(name='thermal_power',
                           description='Thermal power',
                           compatible_unit_str='W',
                           lower_replace_min=Q(-10.0, 'watt'),
                           lower_replace_max=Q(0.0, 'watt'),
                           lower_replace_value=Q(0.0, 'watt'),
                           info_checks=None,
                           common_units=list(common_units.power)
                           )

mass_flow = SensorType(name='mass_flow',
                       description='Mass flow',
                       compatible_unit_str='kg/s',
                       lower_replace_min=Q(-100.0, 'kilogram / second'),
                       lower_replace_max=Q(0.0, 'kilogram / second'),
                       lower_replace_value=Q(0.0, 'kilogram / second'),
                       info_checks=None,
                       common_units=list(common_units.mass / common_units.time),
                       )

volume_flow = SensorType(name='volume_flow',
                         description='Volume flow',
                         compatible_unit_str='m³/s',
                         lower_replace_min=Q(-0.1, 'meter ** 3 / second'),
                         lower_replace_max=Q(0.0, 'meter ** 3 / second'),
                         lower_replace_value=Q(0.0, 'meter ** 3 / second'),
                         info_checks={'position': {'unit': '', 'minimum': 0, 'maximum': 1,
                                                   'description': 'Position of the volume flow sensor, near te_in '
                                                                  '(0), near te_out (1) or in between (0..1).'}},
                         common_units=list(common_units.volume / common_units.time),
                         )

wind_speed = SensorType(name='wind_speed',
                        description='Wind speed',
                        compatible_unit_str='m/s',
                        lower_replace_min=Q(-1.0, 'meter / second'),
                        lower_replace_max=Q(0.0, 'meter / second'),
                        lower_replace_value=Q(0.0, 'meter / second'),
                        info_checks=None,
                        common_units=list(common_units.length / common_units.time),
                        )

temperature_derivative = SensorType(name='temperature_derivative',
                                    description='Temperature derivative',
                                    compatible_unit_str='K/s',
                                    lower_replace_min=Q(-100.0, 'kelvin / second'),
                                    upper_replace_max=Q(100.0, 'kelvin / second'),
                                    info_checks=None,
                                    common_units=list(common_units.temperature / common_units.time),
                                    )

pressure = SensorType(name='pressure',
                      description='Pressure',
                      compatible_unit_str='bar',
                      lower_replace_min=Q(-0.5, 'bar'),
                      lower_replace_max=Q(0.0, 'bar'),
                      lower_replace_value=Q(0.0, 'bar'),
                      info_checks=None,
                      common_units=list(common_units.pressure),
                      )

bool = SensorType(name='bool',
                  description='Boolean',
                  compatible_unit_str='dimensionless',
                  info_checks=None,
                  common_units=list(common_units.bool)
                  )

float = SensorType(name='float',
                   description='Float',
                   compatible_unit_str='dimensionless',
                   info_checks=None,
                   common_units=list(common_units.float)
                   )

float_0_1 = SensorType(name='float_0_1',
                       description='Float between 0 and 1',
                       compatible_unit_str='dimensionless',
                       lower_replace_min=Q(0.0),
                       upper_replace_max=Q(1.0),
                       info_checks=None,
                       common_units=list(common_units.float)
                       )

float_0_100 = SensorType(name='float_0_100',
                         description='Float between 0 and 100',
                         compatible_unit_str='dimensionless',
                         lower_replace_min=Q(0.0),
                         upper_replace_max=Q(100.0),
                         info_checks=None,
                         common_units=list(common_units.float)
                         )

angle_0_180 = SensorType(name='angle_0_180',
                         description='Angle between 0 and 180',
                         compatible_unit_str='°',
                         lower_replace_min=Q(0.0, 'degree'),
                         upper_replace_max=Q(180.0, 'degree'),
                         info_checks=None,
                         common_units=list(common_units.angle),
                         )

angle_0_360 = SensorType(name='angle_0_360',
                         description='Angle between 0 and 360',
                         compatible_unit_str='°',
                         lower_replace_min=Q(0.0, 'degree'),
                         upper_replace_max=Q(360.0, 'degree'),
                         info_checks=None,
                         common_units=list(common_units.angle),
                         )

angle_0_90 = SensorType(name='angle_0_90',
                        description='Angle between 0 and 90',
                        compatible_unit_str='°',
                        lower_replace_min=Q(0.0, 'degree'),
                        upper_replace_max=Q(90.0, 'degree'),
                        info_checks=None,
                        common_units=list(common_units.angle),
                        )

angle__90_90 = SensorType(name='angle__90_90',
                          description='Angle between -90 and 90',
                          compatible_unit_str='°',
                          lower_replace_min=Q(-90.0, 'degree'),
                          upper_replace_max=Q(90.0, 'degree'),
                          info_checks=None,
                          common_units=list(common_units.angle),
                          )

all_sensor_types = [x for x in sys.modules[__name__].__dict__.values() if isinstance(x, SensorType)]
