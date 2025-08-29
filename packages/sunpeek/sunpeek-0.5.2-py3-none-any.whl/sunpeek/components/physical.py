import os
from typing import List
import uuid
import numpy as np
import pandas as pd
import pytz
import sqlalchemy
import sqlalchemy.event
from sqlalchemy.orm import relationship, Session, backref
from sqlalchemy import Column, String, Integer, Float, Boolean, Enum, ForeignKey, UniqueConstraint

from sunpeek.common.unit_uncertainty import Q, parse_quantity
import sunpeek.common.errors as err
import sunpeek.common.time_zone as tz
from sunpeek.components.helpers import AccuracyClass, ComponentParam, IsVirtual, DataUploadDefaults, PCSettingsDefaults
from sunpeek.components.operational_events import OperationalEvent
from sunpeek.components.base import Component, SensorSlot
from sunpeek.components.fluids import FluidFactory, FluidDefinition, UninitialisedFluid
from sunpeek.components.sensor import Sensor
from sunpeek.components.types import Collector, UninitialisedCollector
from sunpeek.components import sensor_types as st
import sunpeek.db_utils.crud
from sunpeek.core_methods.common import shading


class Plant(Component):
    """
    Implements large solar thermal plant as the overarching component on which the kernel methods are applied.

    Attributes
    ----------

    name : str
        Plant name. Must be unique within HarvestIT 'plant' database.
    owner : str, optional
        Name of plant owner.
    operator : str, optional
        Name of plant operator.
    description : str, optional
        Description of the plant, its components, hydraulic setup and other relevant information.
    location_name : str, optional
        Name of the location. Example: 'Graz, Austria'
    latitude : pint Quantity
        Geographical latitude. Positive is north of the equator. See `pvlib Location`_.
    longitude : pint Quantity
        Geographical longitude. Positive is east of the prime meridian. See `pvlib Location`_.
    elevation : pint Quantity, optional
        Location elevation, e.g. Q(440, 'm'). If available, used to improve pvlib's solar position calculation.
    data_upload_defaults : DataUploadDefaults,
        Defaults for parsing raw data files for this plant. Defaults to an all null DataUploadDefaults

    fluid_solar : Fluid object
        Fluid in the solar circuit. Optional for the PC (Performance Check)
        method (but stated in the standard report, see Annex A1 in `ISO standard 24194`_),
        required for the D-CAT (Dynamic Collector Array Test) method.
    fluidvol_total : pint Quantity, optional
        Total fluid content of the solar side (including all pipes, collectors etc).
    tp : Sensor
        Total thermal power of the plant, including all its collector arrays.
    vf : Sensor
        Total volume flow in the solar circuit of the plant, for all collector arrays.
    mf : Sensor
        Total mass flow in the solar circuit of the plant, for all collector arrays.
    te_amb : Sensor
        Ambient air temperature representative for the plant.
    ve_wind : Sensor, optional
        Wind speed / wind velocity representative for the plant.
    rh_amb : Sensor, optional
        Ambient relative humidity representative for the plant.
    te_dew_amb : Sensor, optional, or virtual Sensor
        Dew point temperature representative for the plant. Is calculated as a virtual sensor if both te_amb and
        rh_amb have data (are not None).
    pr_amb : Sensor, optional
        Ambient air pressure representative for the plant.
    te_in : Sensor, optional
        Inlet / return temperature of the plant; this is the temperature after the heat exchanger, sent back to the
        collector arrays.
    te_out : Sensor, optional
        Outlet / flow temperature of the plant; this is the temperature received by all collector arrays together,
        before the fluid enters the heat exchanger.
    rd_ghi : virtual Sensor
        Global horizontal irradiance. Calculated by a radiation model from in_global, in_beam, in_diffuse, in_dni.
    rd_bhi : virtual Sensor
        Direct / beam horizontal irradiance. Calculated by a radiation model from in_global, in_beam, in_diffuse,
        in_dni.
    rd_dhi : virtual Sensor
        Diffuse horizontal irradiance. Calculated by a radiation model from in_global, in_beam, in_diffuse, in_dni.
    sun_azimuth : virtual Sensor
        Solar azimuth angle.
    sun_zenith : virtual Sensor
        Solar zenith angle.
    sun_apparent_zenith : virtual Sensor
        Apparent solar zenith angle.
    sun_elevation : virtual Sensor
        Solar elevation / altitude angle.
    sun_apparent_elevation : virtual Sensor
        Apparent solar elevation / altitude angle.

    rd_dni : virtual Sensor
        Direct normal irradiance. Calculated by a radiation model from in_global, in_beam, in_diffuse, in_dni.
    rd_dni_extra : virtual Sensor
        Extraterrestrial solar radiation.
    linke_turbidity : virtual Sensor
        Linke turbidity calculated for specific location and date.
    rd_ghi_clearsky : virtual Sensor
        Clear sky global horizontal irradiance based on Linke turbidity, calculated with pvlib.clearsky.ineichen
    rd_dni_clearsky : virtual Sensor
        Clear sky direct normal irradiance (DNI) based on Linke turbidity, calculated with pvlib.clearsky.ineichen
    rel_airmass : virtual Sensor
        Relative airmass.
    abs_airmass : virtual Sensor
        Absolute airmass.

    These sensors start with _ because they don't really belong to the plant, they are just input Sensor to calculate
    the proper Plant.rd_ghi, .rd_bhi, .rd_dhi
    in_global : Sensor, optional
        Global radiation sensor to be used to calculate horizontal radiation components for the plant. The sensor may
        be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_beam : Sensor, optional
        Direct / beam radiation sensor to be used to calculate horizontal radiation components for the plant. The
        sensor may be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_diffuse : Sensor, optional
        Diffuse radiation sensor to be used to calculate horizontal radiation components for the plant. The
        sensor may be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_dni : Sensor, optional
        Direct normal irradiance (DNI) sensor to be used to calculate horizontal radiation components for the plant.

    References
    ----------
    .. _pvlib:
        https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.location.Location.html
    .. _IANA / tz database df_timezone string:
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    .. _Timezonefinder library:
        https://github.com/jannikmi/timezonefinder
    .. _ISO standard 24194:
        https://www.iso.org/standard/78074.html
    """

    __tablename__ = 'plant'

    __mapper_args__ = {
        "polymorphic_identity": "plant"
    }
    id = Column(Integer, ForeignKey('components.component_id'), primary_key=True)
    name = Column(String, unique=True)
    owner = Column(String)
    operator = Column(String)
    description = Column(String)

    raw_data_path = Column(String)
    calc_data_path = Column(String)
    virtuals_calculation_uptodate = Column(Boolean)

    operational_events = relationship("OperationalEvent", back_populates="plant", cascade="all, delete-orphan")

    _latitude = ComponentParam('deg', -90, 90)
    _longitude = ComponentParam('deg', -180, 180)
    tz_data_offset = Column(Float)
    elevation = ComponentParam('m', -430.5, 8848.86)  # Anything between the Dead Sea and Everest
    location_name = Column(String)

    fluid_solar = relationship("Fluid", back_populates='plant', uselist=False, cascade="all, delete")
    fluidvol_total = ComponentParam('m**3', 0, np.inf)

    plant_measurement_accuracy = Column(Enum(AccuracyClass))
    raw_sensors = relationship("Sensor", back_populates="plant", cascade="all, delete-orphan")

    upload_history = relationship("UploadHistory", back_populates="plant", cascade="all, delete-orphan",
                                  passive_deletes=True)
    data_upload_defaults = relationship("DataUploadDefaults", back_populates="plant", cascade="all, delete-orphan",
                                        passive_deletes=True, uselist=False)
    pc_settings_defaults = relationship("PCSettingsDefaults", back_populates="plant", cascade="all, delete-orphan",
                                        passive_deletes=True, uselist=False)

    raw_names = {}

    sensor_slots = {
        'tp':
            SensorSlot('tp', st.thermal_power,
                       'Thermal power', IsVirtual.possible,
                       description='Total thermal power of the plant, including all its collector arrays.'),
        'vf':
            SensorSlot('vf', st.volume_flow,
                       'Volume flow', IsVirtual.never,
                       description='Total volume flow in the solar circuit of the plant, for all collector arrays.'),
        'mf':
            SensorSlot('mf', st.mass_flow,
                       'Mass flow', IsVirtual.possible,
                       description='Total mass flow in the solar circuit of the plant, for all collector arrays.'),
        'te_in':
            SensorSlot('te_in', st.fluid_temperature,
                       'Inlet temperature', IsVirtual.never,
                       description='Inlet / return temperature of the plant; this is the temperature after the '
                                   'heat exchanger, sent back to the collector arrays.'),
        'te_out':
            SensorSlot('te_out', st.fluid_temperature,
                       'Outlet temperature', IsVirtual.possible,
                       description='Inlet / return temperature of the plant; this is the temperature received by '
                                   'all collector arrays together, before the fluid enters the heat exchanger.'),
        'te_amb':
            SensorSlot('te_amb', st.ambient_temperature,
                       'Ambient temperature', IsVirtual.never,
                       description='Ambient air temperature representative for the plant.'),
        've_wind':
            SensorSlot('ve_wind', st.wind_speed,
                       'Wind speed', IsVirtual.never,
                       description='Wind speed / wind velocity representative for the plant.'),
        'rh_amb':
            SensorSlot('rh_amb', st.float_0_100,
                       'Relative humidity', IsVirtual.never,
                       description='Ambient relative humidity representative for the plant.'),
        'pr_amb':
            SensorSlot('pr_amb', st.pressure,
                       'Air pressure', IsVirtual.never,
                       description='Ambient air pressure representative for the plant.'),
        'te_dew_amb':
            SensorSlot('te_dew_amb', st.ambient_temperature,
                       'Dew point temperature', IsVirtual.possible,
                       'Dew point temperature representative for the plant. Is calculated as a virtual '
                       'sensor if both te_amb and rh_amb have data (are not None).'),
        'in_global':
            SensorSlot('in_global', st.global_radiation,
                       'Global radiation input', IsVirtual.never,
                       description='Global radiation sensor to be used to calculate horizontal radiation '
                                   'components for the plant. The sensor may be installed at a non-zero '
                                   'tilt angle, in that case the horizontal radiation components will be '
                                   'calculated by a radiation model.'),
        'in_beam':
            SensorSlot('in_beam', st.direct_radiation,
                       'Direct radiation input', IsVirtual.never,
                       description='Direct / beam radiation sensor to be used to calculate horizontal '
                                   'radiation components for the plant. The sensor may be installed at a '
                                   'non-zero tilt angle, in that case the horizontal radiation components '
                                   'will be calculated by a radiation model.'),
        'in_diffuse':
            SensorSlot('in_diffuse', st.diffuse_radiation,
                       'Diffuse radiation input', IsVirtual.never,
                       description='Diffuse radiation sensor to be used to calculate horizontal radiation '
                                   'components for the plant. The sensor may be installed at a non-zero '
                                   'tilt angle, in that case the horizontal radiation components will be '
                                   'calculated by a radiation model.'),
        'in_dni':
            SensorSlot('in_dni', st.dni_radiation,
                       'DNI radiation input', IsVirtual.never,
                       description='Direct normal irradiance (DNI) sensor to be used to calculate horizontal '
                                   'radiation components for the plant.'),
        'rd_ghi':
            SensorSlot('rd_ghi', st.global_radiation,
                       'Global radiation', IsVirtual.always,
                       description='Global horizontal irradiance. Calculated by a radiation conversion model '
                                   'from in_global, in_beam, in_diffuse, in_dni.'),
        'rd_bhi':
            SensorSlot('rd_bhi', st.direct_radiation,
                       'Direct radiation', IsVirtual.always,
                       description='Direct / beam horizontal irradiance. Calculated by a radiation conversion '
                                   'model from in_global, in_beam, in_diffuse, in_dni.'),
        'rd_dhi':
            SensorSlot('rd_dhi', st.diffuse_radiation,
                       'Diffuse radiation', IsVirtual.always,
                       description='Diffuse horizontal irradiance. Calculated by a radiation conversion model '
                                   'from in_global, in_beam, in_diffuse, in_dni.'),
        'rd_dni':
            SensorSlot('rd_dni', st.dni_radiation,
                       'DNI (direct normal) radiation', IsVirtual.always,
                       description='Direct normal irradiance. Calculated by a radiation model from '
                                   'in_global, in_beam, in_diffuse, in_dni.'),
        'sun_azimuth':
            SensorSlot('sun_azimuth', st.angle_0_360,
                       'Solar azimuth angle', IsVirtual.always,
                       description='Solar azimuth angle.'),
        'sun_zenith':
            SensorSlot('sun_zenith', st.angle_0_180,
                       'Solar zenith angle', IsVirtual.always,
                       description='Solar zenith angle'),
        'sun_apparent_zenith':
            SensorSlot('sun_apparent_zenith', st.angle_0_180,
                       'Apparent solar zenith angle', IsVirtual.always,
                       description='Apparent solar zenith angle'),
        'sun_elevation':
            SensorSlot('sun_elevation', st.angle__90_90,
                       'Solar elevation angle', IsVirtual.always,
                       description='Solar elevation / altitude angle.'),
        'sun_apparent_elevation':
            SensorSlot('sun_apparent_elevation', st.angle__90_90,
                       'Apparent solar elevation angle', IsVirtual.always,
                       description='Apparent solar elevation angle'),
        'rd_dni_extra':
            SensorSlot('rd_dni_extra', st.dni_radiation,
                       'Extraterrestrial solar radiation', IsVirtual.always,
                       description='Extraterrestrial solar radiation.'),
        'rel_airmass':
            SensorSlot('rel_airmass', st.float_0_100,
                       'Relative airmass', IsVirtual.always,
                       description='Relative airmass.'),
        'abs_airmass':
            SensorSlot('abs_airmass', st.float_0_100,
                       'Absolute airmass', IsVirtual.always,
                       description='Absolute airmass.'),
        'linke_turbidity':
            SensorSlot('linke_turbidity', st.float_0_100,
                       'Linke turbidity', IsVirtual.always,
                       description='Linke turbidity calculated for specific location and date.'),
        'rd_ghi_clearsky':
            SensorSlot('rd_ghi_clearsky', st.global_radiation,
                       'Clear sky global horizontal irradiance', IsVirtual.always,
                       description='Clear sky global horizontal irradiance based on Linke turbidity, '
                                   'calculated with pvlib.clearsky.ineichen'),
        'rd_dni_clearsky':
            SensorSlot('rd_dni_clearsky', st.dni_radiation,
                       'Clear sky direct normal irradiance', IsVirtual.always,
                       description='Clear sky direct normal irradiance (DNI) based on Linke turbidity, '
                                   'calculated with pvlib.clearsky.ineichen')
    }

    def __init__(self, name=None, owner=None, operator=None, description=None, plant_measurement_accuracy=None,
                 location_name=None, latitude=None, longitude=None, elevation=None,
                 fluid_solar=None, fluidvol_total=None, arrays=None, sensor_map=None, raw_sensors=None,
                 **kwargs):

        # To change plant context, explicitly attach a different Context object to plant in the calling code
        from sunpeek.data_handling.context import Context
        self.context = Context(plant=self)
        self.defer_post_config_changed_actions = True

        self.name = name or str(uuid.uuid4().hex[0:12])
        self.owner = owner
        self.operator = operator
        self.description = description
        self.plant_measurement_accuracy = plant_measurement_accuracy
        self.location_name = location_name
        self.tz_data_offset = None
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation or Q(100, 'm')

        self.raw_sensors = raw_sensors or []
        self.fluid_solar = fluid_solar
        self.fluidvol_total = fluidvol_total
        self.arrays = arrays or []

        self.raw_data_path = os.environ.get('SUNPEEK_RAW_DATA_PATH', './raw_data') + '/' + self.name
        self.calc_data_path = os.environ.get('SUNPEEK_CALC_DATA_PATH', './calc_data') + '/' + self.name
        self.virtuals_calculation_uptodate = False

        self.data_upload_defaults = DataUploadDefaults()
        self.pc_settings_defaults = PCSettingsDefaults()

        self.sensor_map = sensor_map or {}
        self.set_sensors(**kwargs)

    def add_array(self, arrays):
        """
        Convenience method for adding items to plant.arrays. Equivalent to plant.arrays += array or plant.arrays.append(array).

        Parameters
        ----------
        arrays : `~sunpeek.components.physical.Array` or list of `~sunpeek.components.physical.Array`

        Returns
        -------
        Updated list of `~sunpeek.components.physical.Array` objects for the plant
        """
        if isinstance(arrays, Array):
            arrays = [arrays]
        for array in arrays:
            self.arrays.append(array)
        return self.arrays

    @sqlalchemy.orm.reconstructor
    def _init_on_load(self):
        self.set_default_context(datasource='pq')

    @property
    def latitude(self):
        return self._latitude

    @property
    def longitude(self):
        return self._longitude

    @latitude.setter
    def latitude(self, val):
        val = parse_quantity(val)
        if (val is not None) and (self.longitude is not None):
            self.tz_data_offset = tz.get_timezone_offset_minutes(latitude=val, longitude=self.longitude)
        self._latitude = val

    @longitude.setter
    def longitude(self, val):
        val = parse_quantity(val)
        if (val is not None) and (self.latitude is not None):
            self.tz_data_offset = tz.get_timezone_offset_minutes(latitude=self.latitude, longitude=val)
        self._longitude = val

    @property
    def tz_data(self) -> pytz.FixedOffset:
        return tz.get_data_timezone(self.tz_data_offset)

    @property
    def local_tz_string_with_DST(self) -> str | None:
        if (self.latitude is None) or (self.longitude is None):
            return None
        return tz.get_timezone_string(latitude=self.latitude, longitude=self.longitude)

    @sqlalchemy.orm.validates('arrays', include_removes=True)
    def _validate_arrays(self, attr_name, component, is_remove):
        """ Used to automatically convert array dict representations to components and
        set sensors to plant when an array is added to the plant
        """
        if isinstance(component, dict):
            return Array(plant=self, **component)

        component = component.update_sensors(is_remove=is_remove)

        return component

    @sqlalchemy.orm.validates('fluid_solar')
    def _validate_fluids(self, _, component):
        """ Used to automatically convert fluid dict representations when a fluid is added to the plant.
        """
        if isinstance(component, dict):
            return FluidFactory(**component)
        return component

    @sqlalchemy.orm.validates('data_upload_defaults')
    def _validate_data_upload_defaults(self, _, component):
        """ Used to automatically convert dict representation to DataUploadDefaults object.
        """
        if isinstance(component, dict):
            return DataUploadDefaults(**component)
        return component

    @sqlalchemy.orm.validates('pc_settings_defaults')
    def _validate_pc_settings_defaults(self, _, component):
        """ Used to automatically convert dict representation to PCSettingsDefaults object.
        """
        if isinstance(component, dict):
            return PCSettingsDefaults(**component)
        return component

    @property
    def plant(self):
        return self

    @property
    def ignored_ranges(self) -> List[pd.Interval]:
        """Gets a list of time ranges to be ignored from the plant's `operational_events`
        """
        intervals = []
        for event in self.operational_events:
            if event.ignored_range:
                intervals.append(
                    pd.Interval(pd.to_datetime(event.event_start), pd.to_datetime(event.event_end), closed='both'))

        return list(set(intervals))

    def is_ignored(self, timestamp) -> bool:
        """
        Checks if a timestamp is in an ignored range

        Parameters
        ----------
        timestamp : datetime.datetime or pandas.Timestamp or str
        """

        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        for r in self.ignored_ranges:
            if timestamp in r:
                return True

        return False

    def add_operational_event(self, start, end=None, tz=None, description=None, ignored_range=False) -> None:
        """
        Parameters
        ----------
        start : A datetime object, or a string. If the string does not contain a df_timezone like '2022-1-1 00:00+1',
            then the tz argument must also be specified.
        end : A datetime object, or a string. If the string does not contain a df_timezone like '2022-1-2 00:00+1',
            then the tz argument must also be specified.
        tz : A df_timezone string like 'Europe/Vienna' or any pytz time zone, like pytz.FixedOffset(60)
        description : str
            A description of the event or reason for ignored range.
        ignored_range : bool
            If data in the period specified in the event should be ignored
        """

        OperationalEvent(event_start=start, event_end=end, tz=tz, ignored_range=ignored_range, description=description,
                         plant=self)
        if ignored_range and self.context is not None:
            self.reset_cache()

    # @property
    # def radiation_input_slots(self):
    #     return self.in_global, self.in_beam, self.in_diffuse, self.in_dni

    @property
    def area_gr(self):
        return sum([a.area_gr for a in self.arrays])

    @property
    def area_ap(self):
        return sum([a.area_ap for a in self.arrays])

    @property
    def time_index(self):
        return self.context.time_index if self.context is not None else None

    @sqlalchemy.orm.validates('raw_sensors', include_removes=True)
    def _validate_raw_sensors(self, _, val, is_remove):
        # assert isinstance(val, list), "raw_sensors must be a list of Sensor objects or dicts"
        if is_remove:
            val.remove_references(include_plant=False)
        if isinstance(val, dict):
            val = Sensor(**val)
        return val

    def get_raw_sensor(self, raw_name, raise_if_not_found=False):
        session = sqlalchemy.orm.object_session(self)
        if raw_name is None:
            return None
        if session is None:
            for sensor in self.raw_sensors:
                if sensor.raw_name == raw_name:
                    return sensor
        else:
            try:
                return sunpeek.db_utils.crud.get_sensors(session, plant_id=self.id, raw_name=raw_name)
            except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
                pass
        if raise_if_not_found:
            raise err.SensorNotFoundError(f"Either no sensor with raw_name '{raw_name}' was found, "
                                          f"or more than one such sensor was")

    def get_raw_names(self, include_virtuals=False, only_virtuals=False):
        if include_virtuals:
            return [sensor.raw_name for sensor in self.raw_sensors]
        if only_virtuals:
            return [sensor.raw_name for sensor in self.raw_sensors if (sensor.is_virtual and sensor.can_calculate)]
        return [sensor.raw_name for sensor in self.raw_sensors if not sensor.is_virtual]

    def set_default_context(self, datasource=None):
        """Create and set default context as Context with parquet datasource. Does not upload or affect any data.
        """
        from sunpeek.data_handling.context import Context
        self.context = Context(plant=self, datasource=datasource)

    def reset_cache(self) -> None:
        if self.context is not None:
            self.context.cache.reset()

    def delete_all_data(self) -> None:
        if self.context is not None:
            self.context.delete_all_data()


class Array(Component):
    """
    Implements collector array with given area, homogeneous tilt and azimuth angles and exactly 1 collector.

    Attributes
    ----------
    name : str
        Name of array. Must be unique within parent plant.
    plant : Plant object
        Plant to which the array belongs.
    collector
        Collector used in this array. An array has exactly 1 `collector`.
    area_gr : pint Quantity
        Total gross collector area of the collector array.
    area_ap : pint Quantity, optional
        Total aperture collector area of the collector array.

    azim : pint Quantity
        Azimuth angle of the array surface. An array has exactly 1 scalar `azim`. North=0, East=90,
        South=180, West=270. See `surface_azimuth` in `pvlib FixedMount`_
    tilt : pint Quantity
        Tilt angle of the array, defined as angle from the horizontal. Examples: surface facing up / towards zenith:
        tilt=Q(0,'deg'), surface facing horizon: tilt=Q(90, 'deg). An array has exactly 1 scalar `tilt`. See
        `surface_tilt` in `pvlib FixedMount`_
    row_spacing : pint Quantity, optional
        The spacing between adjacent rows of collectors in the array, measured along the ground surface.
        If the ground is tilted, this is not the same as the horizontal distance (on the horizontal projection).
    n_rows : pint Quantity
        Number of collector rows in the collector array.
    ground_tilt : pint Quantity, optional
        Tilt angle of the ground or more generally of the plane on which the collector field is mounted; in the
        direction of the azimuth of the collector field; positive values increase the absolute tilt of the collectors.
    ground_azim : pint Quantity, optional
        Azimuth angle of the ground or more generally of the plane on which the collector field is mounted;
        An array has exactly 1 scalar `ground_azim`. North=0, East=90, South=180, West=270.
    mounting_level : pint Quantity, optional
        Distance of the lowest part of a collector from the ground (back edge).

    fluidvol_total : pint Quantity, optional
        Total fluid content of the array (including all pipes and collectors etc).
    rho_ground : pint Quantity, optional
        Ground reflectance coefficient used for solar irradiance calculations for collector arrays. Can be overridden
        by individual arrays.
    rho_colbackside : pint Quantity, optional
        Reflectance coefficient of the collector backside.
    rho_colsurface : pint Quantity, optional
        Reflectance coefficient of the collectors (usually close to zero).
    max_aoi_shadow : pint Quantity, optional
        At times when the angle of incidence (aoi) is above `max_aoi_shadow`, the array is considered as shadowed
        in the virtual sensor `array.is_shadowed`.
    min_elevation_shadow : pint Quantity, optional
        At times when the sun apparent elevation is below `min_elevation_shadow`, the array is considered as shadowed
        in the virtual sensor `array.is_shadowed`.
    te_in : Sensor, optional
        Inlet / return temperature characteristic for this array.
    te_out : Sensor, optional
        Outlet / flow / supply temperature characteristic for this array.
    tp : Sensor, optional
        Thermal power of collector array.
    vf : Sensor, optional
        Total volume flow of collector array.
    mf : Sensor, optional
        Total mass flow of collector array.

    is_shadowed : Sensor, optional, or virtual Sensor
        Boolean variable that describes whether at a particular timestamp the array is considered
        partly or completely shadowed (shadowed: value 1 or True, not shadowed: value 0 or False).
        A user can set `is_shadowed` as a real sensor to provide shadow information from external sources,
        e.g. from a calculation that takes horizon or the 3D surroundings of the array into account.
        If not provided by user, `is_shadowed` is calculated as a virtual sensor taking into account
        maximum angle of incidence, minimum sun elevation, no internal (row-to-row) shading.
    aoi : virtual Sensor
        Angle of incidence of sun on plane of array, i.e. the angle between the solar vector and the array surface
        normal.
    internal_shading_fraction : virtual Sensor
        Fraction of internal shading (row-to-row shading) of the array, a numeric value between 0 (no shading) and 1
        (completely shaded).

    rd_gti : virtual Sensor
        Global irradiance on array, calculated by a radiation conversion model following a chosen strategy (e.g.
        poa, feedthrough, detailed); see class `RadiationConversionTilted` for details.
        Radiation conversion uses input Sensors in_global, .in_beam .in_diffuse, .in_dni
        Optionally takes ground diffuse, beam shading and diffuse masking into account.
    rd_bti : virtual Sensor
        Direct / beam irradiance on array, calculated by a radiation conversion model following a chosen strategy (
        e.g. poa, feedthrough, detailed); see class `RadiationConversionTilted` for details.
        Radiation conversion uses input Sensors in_global, .in_beam, .in_diffuse, .in_dni
        Optionally takes ground diffuse, beam shading and diffuse masking into account.
    rd_dti : virtual Sensor
        Diffuse irradiance on array, calculated by a radiation conversion model following a chosen strategy (e.g.
        poa, feedthrough, detailed); see class `RadiationConversionTilted` for details.
        Radiation conversion uses input Sensors in_global, .in_beam, .in_diffuse, .in_dni
        Optionally takes ground diffuse, beam shading and diffuse masking into account.

    These radiation sensors starting with "in_" are input sensors used to compute the proper array irradiances,
    namely the Array virtual sensors rd_gti (POA hemispheric), rd_bti (beam in POA), rd_dti (diffuse in POA).
    in_global : Sensor, optional
        Global radiation sensor to be used to calculate tilted radiation components for the array. The sensor may
        be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_beam : Sensor, optional
        Direct / beam radiation sensor to be used to calculate tilted radiation components for the array. The
        sensor may be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_diffuse : Sensor, optional
        Diffuse radiation sensor to be used to calculate tilted radiation components for the array. The
        sensor may be installed at a non-zero tilt angle, in that case the horizontal radiation components will be
        calculated by a radiation model.
    in_dni : Sensor, optional
        Direct normal irradiance (DNI) sensor to be used to calculate tilted radiation components for the array.

    .. _Fixed Mount:
        https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.pvsystem.FixedMount.html#pvlib.pvsystem.FixedMount
    """

    __tablename__ = 'arrays'

    __mapper_args__ = {
        "polymorphic_identity": "array"
    }

    id = Column(Integer, ForeignKey('components.component_id'), primary_key=True)

    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", foreign_keys=[plant_id], backref=backref("arrays", cascade="all, delete"))
    name = Column(String)
    collector_id = Column(Integer, ForeignKey('collectors.id'))
    _collector = relationship("Collector", passive_deletes='all')

    area_gr = ComponentParam('m**2', 1, np.inf)
    area_ap = ComponentParam('m**2', 1, np.inf)
    _azim = ComponentParam('deg', 0, 360)
    _tilt = ComponentParam('deg', 0, 90)
    _row_spacing = ComponentParam('m', 0, np.inf)
    n_rows = ComponentParam('', 0, np.inf)
    _ground_tilt = ComponentParam('deg', 0, 90)
    _ground_azim = ComponentParam('deg', 0, 360)
    mounting_level = ComponentParam('m', 0, 10)
    fluidvol_total = ComponentParam('m**3', 0, np.inf)
    rho_ground = ComponentParam('', 0, 1)
    rho_colbackside = ComponentParam('', 0, 1)
    rho_colsurface = ComponentParam('', 0, 1)
    max_aoi_shadow = ComponentParam('deg', 30, 90)
    min_elevation_shadow = ComponentParam('deg', 0, 90)

    __table_args__ = (UniqueConstraint('name', 'plant_id', name='_unique_array_names_per_plant'),)

    sensor_slots = {
        'tp':
            SensorSlot('tp', st.thermal_power,
                       'Thermal power', IsVirtual.possible,
                       description='Thermal power of collector array.'),
        'vf':
            SensorSlot('vf', st.volume_flow,
                       'Volume flow', IsVirtual.never,
                       description='Total volume flow of collector array.'),
        'mf':
            SensorSlot('mf', st.mass_flow,
                       'Mass flow', IsVirtual.possible,
                       description='Total mass flow of collector array.'),
        'te_in':
            SensorSlot('te_in', st.fluid_temperature,
                       'Inlet temperature', IsVirtual.never,
                       description='Inlet / return temperature characteristic for this array.'),
        'te_out':
            SensorSlot('te_out', st.fluid_temperature,
                       'Outlet temperature', IsVirtual.possible,
                       description='Outlet / flow / supply temperature characteristic for this array.'),
        'is_shadowed':
            SensorSlot('is_shadowed', st.bool,
                       'Array is shadowed', IsVirtual.possible,
                       description='Boolean variable that describes whether at a particular timestamp '
                                   'the array is considered partly or completely shadowed '
                                   '(shadowed: value 1 or True, not shadowed: value 0 or False).'
                                   'A user can set `is_shadowed` as a real sensor to provide shadow '
                                   'information from external sources, e.g. from a calculation that takes '
                                   'horizon or the 3D surroundings of the array into account. If not '
                                   'provided by user, `is_shadowed` is calculated as a virtual sensor '
                                   'taking into account maximum angle of incidence, minimum sun elevation, '
                                   'no internal (row-to-row) shading.'),
        'in_global':
            SensorSlot('in_global', st.global_radiation,
                       'Global radiation input', IsVirtual.never,
                       description='Global radiation sensor to be used to calculate tilted radiation '
                                   'components for the array. The sensor may be installed at a non-zero '
                                   'tilt angle, in that case the horizontal radiation components will be '
                                   'calculated by a radiation model.'),
        'in_beam':
            SensorSlot('in_beam', st.direct_radiation,
                       'Direct radiation input', IsVirtual.never,
                       description='Direct / beam radiation sensor to be used to calculate tilted radiation '
                                   'components for the array. The sensor may be installed at a '
                                   'non-zero tilt angle, in that case the horizontal radiation components '
                                   'will be calculated by a radiation model.'),
        'in_diffuse':
            SensorSlot('in_diffuse', st.diffuse_radiation,
                       'Diffuse radiation input', IsVirtual.never,
                       description='Diffuse radiation sensor to be used to calculate tilted radiation '
                                   'components for the array. The sensor may be installed at a non-zero '
                                   'tilt angle, in that case the horizontal radiation components will be '
                                   'calculated by a radiation model.'),
        'in_dni':
            SensorSlot('in_dni', st.dni_radiation,
                       'DNI radiation input', IsVirtual.never,
                       description='Direct normal irradiance (DNI) sensor to be used to calculate tilted '
                                   'radiation components for the array.'),
        'rd_gti':
            SensorSlot('rd_gti', st.global_radiation,
                       'Global radiation', IsVirtual.always,
                       description='Global horizontal irradiance. Calculated by a radiation conversion model '
                                   'from in_global, in_beam, in_diffuse, in_dni.'),
        'rd_bti':
            SensorSlot('rd_bti', st.direct_radiation,
                       'Direct radiation', IsVirtual.always,
                       description='Direct / beam horizontal irradiance. Calculated by a radiation conversion '
                                   'model from in_global, in_beam, in_diffuse, in_dni.'),
        'rd_dti':
            SensorSlot('rd_dti', st.diffuse_radiation,
                       'Diffuse radiation', IsVirtual.always,
                       description='Diffuse horizontal irradiance. Calculated by a radiation conversion model '
                                   'from in_global, in_beam, in_diffuse, in_dni.'),
        'aoi':
            SensorSlot('aoi', st.angle__90_90,
                       'Angle of incidence', IsVirtual.possible,
                       description='Angle of incidence of sun on plane of array, i.e. the angle between the solar '
                                   'vector and the array surface normal.'),
        'internal_shading_fraction':
            SensorSlot('internal_shading_fraction', st.float_0_1,
                       'Internal shading of the array', IsVirtual.always,
                       description='Internal shading (row-to-row shading) fraction of the array, a numeric'
                                   ' value between 0 (no shading) and 1 (completely shaded).'),
        'te_op':
            SensorSlot('te_op', st.fluid_temperature,
                       'Mean fluid temperature', IsVirtual.always,
                       description='Mean fluid temperature, arithmetic mean of inlet and outlet temperatures.'),
        'te_op_deriv':
            SensorSlot('te_op_deriv', st.temperature_derivative,
                       'Derivative of mean fluid temperature', IsVirtual.always,
                       description='Derivative of the mean operating temperature te_op.'),
        'iam':
            SensorSlot('iam', st.float,
                       'Incidence angle modifier of direct radiation', IsVirtual.always,
                       description='Incidence angle modifier of direct radiation.'),
    }

    def __init__(self, name=None, plant=None, collector=None, area_gr=None, area_ap=None, azim=None, tilt=None,
                 row_spacing=None, n_rows=None, ground_tilt=None, ground_azim=None, mounting_level=None,
                 fluidvol_total=None, rho_ground=None, rho_colbackside=None, rho_colsurface=None,
                 max_aoi_shadow=None, min_elevation_shadow=None, sensor_map=None, **kwargs):

        self.defer_post_config_changed_actions = True
        self.name = name
        self.collector = collector

        self.area_ap = area_ap
        self.area_gr = area_gr or self.calc_area_gr_from_collector()
        self.azim = azim
        self.tilt = tilt

        self.row_spacing = row_spacing
        self.n_rows = n_rows
        self.ground_tilt = ground_tilt or Q(0, 'deg')
        self.ground_azim = ground_azim or self.azim
        self.mounting_level = mounting_level or Q(0, 'm')

        self.fluidvol_total = fluidvol_total
        self.rho_ground = rho_ground
        self.rho_colbackside = rho_colbackside
        self.rho_colsurface = rho_colsurface or Q(0)
        self.max_aoi_shadow = max_aoi_shadow or Q(80, 'deg')
        self.min_elevation_shadow = min_elevation_shadow
        self.plant = plant
        self.sensor_map = sensor_map or {}
        self.set_sensors(**kwargs)

    def calc_area_gr_from_collector(self):
        """Set array.area_gr from area_ap and collector information, if None
        """
        coll = self.collector
        if coll is None or isinstance(coll, UninitialisedCollector):
            return None
        if coll.area_ap is None:
            return None
        return self.area_ap * (coll.area_gr / coll.area_ap)

    @property
    def collector(self):
        return self._collector

    @collector.setter
    def collector(self, value):
        if isinstance(value, Collector):
            self._collector = value
        elif isinstance(value, str) and sqlalchemy.orm.object_session(self) is not None:
            _convert_to_concrete_coll(sqlalchemy.orm.object_session(self), self, 'collector',
                                      UninitialisedCollector(value, parent=self, attribute='collector'))
        elif isinstance(value, str):
            self._collector = UninitialisedCollector(value, parent=self, attribute='collector')
        elif value is None:
            self._collector = None
        else:
            raise err.ConfigurationError("Collector must be a Collector object, or the name of an existing collector.")
        # Changing the collector influences the overlap check --> need to call check again.
        self._check_overlap()

    @property
    def row_spacing(self):
        return self._row_spacing

    @row_spacing.setter
    def row_spacing(self, value):
        """Need this setter to check potential collector overlap (for in-roof or facade array configurations).
        """
        # Call this before _check_overlap to benefit from the checks done by ComponentParam
        # (make sure it's a Quantity, and it complies with the defined boundary values).
        self._row_spacing = value
        # This resets self._row_spacing to None if the check fails.
        self._check_overlap()

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, value):
        """Need this setter to check potential collector overlap (for in-roof or facade array configurations).
        """
        # Call this before _check_overlap to benefit from the checks done by ComponentParam
        self._tilt = value
        # This resets self._row_spacing to None if the check fails.
        self._check_overlap()

    @property
    def azim(self):
        return self._azim

    @azim.setter
    def azim(self, value):
        """Need this setter to check potential collector overlap (for in-roof or facade array configurations).
        """
        # Call this before _check_overlap to benefit from the checks done by ComponentParam
        self._azim = value
        # This resets self._row_spacing to None if the check fails.
        self._check_overlap()

    @property
    def ground_tilt(self):
        return self._ground_tilt

    @ground_tilt.setter
    def ground_tilt(self, value):
        """Need this setter to check potential collector overlap (for in-roof or facade array configurations).
        """
        # Call this before _check_overlap to benefit from the checks done by ComponentParam
        self._ground_tilt = value
        # This resets self._row_spacing to None if the check fails.
        self._check_overlap()

    @property
    def ground_azim(self):
        return self._ground_azim

    @ground_azim.setter
    def ground_azim(self, value):
        """Need this setter to check potential collector overlap (for in-roof or facade array configurations).
        """
        # Call this before _check_overlap to benefit from the checks done by ComponentParam
        self._ground_azim = value
        # This resets self._row_spacing to None if the check fails.
        self._check_overlap()

    def _check_overlap(self) -> None:
        """Check that the collectors don't overlap, given the current array configuration.

        Note
        ----
        For in-roof or facade configurations, certain combinations of array row spacing and collector length
        would represent an overlap in the collectors, which does not make sense.
        Check is skipped if there is no collector defined for the array.
        Resets self._row_spacing to None if the check fails.

        Raises
        ------
        ConfigurationError
            If the collectors would overlap, given the current array and collector attributes.
        """
        if self.collector is None:
            return
        if None in (self.tilt, self.ground_tilt,
                    self.azim, self.ground_azim,
                    self.row_spacing, self.collector.gross_length):
            return

        same_tilt = self.tilt == self.ground_tilt
        same_azim = self.azim == self.ground_azim
        is_in_roof = same_tilt & same_azim
        low_row_spacing = self.row_spacing < self.collector.gross_length

        if is_in_roof and low_row_spacing:
            row_spacing = self.row_spacing
            self._row_spacing = None
            raise err.ConfigurationError(f'If collector array and ground have the same azimuth and tilt angles, the '
                                         f'array row spacing must be at least as large as the collector gross length. '
                                         f'Row spacing: {row_spacing.to("m").m:.1f} m, '
                                         f'collector gross length: {self.collector.gross_length.to("m").m:.1f} m.')

    @property
    def masking_angle(self) -> Q:
        return shading.calc_masking_angle_05(self)

    @property
    def fluid_solar(self):
        return self.plant.fluid_solar

    @property
    def orientation(self):
        """Return dictionary with array's "tilt" and "azim" values converted to deg, for radiation calculations.
        """
        return {'tilt': self.tilt.m_as('deg'),
                'azim': self.azim.m_as('deg')}

    def has_orientation(self):
        """Returns True if array has tilt and azimuth well-defined. Useful for radiation calculations.
        """
        return (self.tilt is not None) and (self.azim is not None)


# @property
# def radiation_input_slots(self):
#     return self.in_global, self.in_beam, self.in_diffuse, self.in_dni

# Commented, because currently not used. Database table still exists, not removed by Alembic.
# class HeatExchanger(Component):
#     """
#     Implements a heat exchangers including references to its hot- and cold-side fluids.
#
#     Attributes
#     ----------
#     plant : Plant object
#         Plant to which the heat exchanger belongs.
#     fluid_hot : Sensor, optional
#         Fluid on the hot side of the heat exchanger (often an antifreeze, in a solar thermal plant).
#     fluid_cold : Sensor, optional
#         Fluid on the cold side of the heat exchanger (often water).
#     ua_nom : pint Quantity, optional
#         Nominal heat transfer coefficient.
#     """
#     __tablename__ = 'heat_exchangers'
#
#     __mapper_args__ = {
#         "polymorphic_identity": "heat_exchanger"
#     }
#
#     id = Column(Integer, ForeignKey('components.component_id'), primary_key=True)
#
#     plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
#     plant = relationship("Plant", foreign_keys=[plant_id],
#                          backref=backref("heat_exchangers", cascade="all, delete-orphan"))
#     fluid_hot_id = Column(Integer, ForeignKey('fluids.id'))
#     fluid_hot = relationship("Fluid", foreign_keys=[fluid_hot_id],
#                              cascade="all, delete", uselist=False, passive_deletes=True)
#     fluid_cold_id = Column(Integer, ForeignKey('fluids.id'))
#     fluid_cold = relationship("Fluid", foreign_keys=[fluid_cold_id],
#                               cascade="all, delete", uselist=False, passive_deletes=True)
#     name = Column(String)
#
#     ua_nom = ComponentParam('kW K**-1', 0, np.inf)
#
#     def __init__(self, name, plant, fluid_hot=None, fluid_cold=None, ua_nom=None):
#         self.defer_post_config_changed_actions = True
#         self.name = name
#         self.plant = plant
#         self.fluid_hot = fluid_hot
#         self.fluid_cold = fluid_cold
#         self.ud_nom = ua_nom
#         self.defer_post_config_changed_actions = False


def _check_duplicate_coll_defs(session, inst):
    try:
        db_coll = session.query(Collector).filter(Collector.name == inst.name).one()
        if inst == db_coll:
            return True
        else:
            raise err.DuplicateNameError(
                f"Attempting to create a Collector called {inst.name}, however a Collector "
                f"with this name already exists, but with different attributes.")
    except sqlalchemy.exc.NoResultFound:
        return False


def _convert_to_concrete_coll(session, inst, attribute, val):
    with session.no_autoflush:
        db_coll = session.query(Collector).filter(Collector.name == val.name).one()
        setattr(inst, attribute, db_coll)


def _convert_to_concrete_fluid(session, inst, attribute, val):
    with session.no_autoflush:
        fluid_def = FluidDefinition.get_definition(val.fluid_def_name, session)
        kwargs = val.stored_args
        kwargs['fluid'] = fluid_def
        fluid = FluidFactory(**kwargs)
        setattr(inst, attribute, fluid)


@sqlalchemy.event.listens_for(Session, "transient_to_pending")
def convert_to_concrete_components(session, inst):
    if isinstance(inst, Component):
        with session.no_autoflush:
            fluids = {attr: val for attr, val in inst.__dict__.items() if isinstance(val, UninitialisedFluid)}
            u_cols = {attr: val for attr, val in inst.__dict__.items() if isinstance(val, UninitialisedCollector)}
            collectors = {attr: val for attr, val in inst.__dict__.items()
                          if isinstance(val, Collector) and not isinstance(val, UninitialisedCollector)}
            for attribute, val in fluids.items():
                if val in session:
                    session.expunge(val)
                _convert_to_concrete_fluid(session, inst, attribute, val)
            for attribute, val in u_cols.items():
                if val in session:
                    session.expunge(val)
                _convert_to_concrete_coll(session, inst, attribute, val)
                # Check for duplicate definitions
            for attribute, val in collectors.items():
                _check_duplicate_coll_defs(session, val)


@sqlalchemy.event.listens_for(Session, "before_commit")
def _update_before_commit(session):
    for inst in session.dirty:
        convert_to_concrete_components(session, inst)
