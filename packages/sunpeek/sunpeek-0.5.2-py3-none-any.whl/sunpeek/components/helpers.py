"""
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
"""

import numpy as np
import sqlalchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Identity, ARRAY, Enum, UniqueConstraint, JSON, \
    Boolean, DateTime
import sqlalchemy.orm
import sqlalchemy.exc
from sqlalchemy.orm import relationship
import sqlalchemy.event
import enum

from sunpeek.common.unit_uncertainty import Q
import sunpeek.common.unit_uncertainty as uu
from sunpeek.common.errors import ConfigurationError
from sunpeek.common.utils import DatetimeTemplates
from sunpeek.common.utils import ORMBase


class ComponentParam:
    """Used to define parameters which are represented by Quantities, with optional limit checking.  
    
    Attributes
    ----------
    unit: compatible unit
    minimum: value of the parameters should not be below this
    maximum: value of the parameters should not be above this
    array_type: either "scalar" or "array", defaults to used to create the correct database column types and apply checks correctly.
    """

    def __init__(self, unit: str = None, minimum: float = -np.inf, maximum: float = np.inf, param_type: str = 'scalar'):
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.array_type = param_type


class AttrSetterMixin:
    name = None
    defer_post_config_changed_actions = False

    @classmethod
    def define_component_attrs(cls):
        for sub_cls in cls.all_subclasses():
            # Get all ComponentParam from all component / subclass attributes
            params = {attr: obj for attr, obj in sub_cls.__dict__.items() if isinstance(obj, ComponentParam)}
            for attr, obj in params.items():
                sub_cls.add_component_attr(attr, obj.unit, obj.minimum, obj.maximum, obj.array_type)

    @classmethod
    def add_component_attr(cls, name, unit=None, minimum=-np.inf, maximum=np.inf, array_type='scalar'):
        if array_type == 'scalar':
            setattr(cls, f'_{name}_mag', Column(Float))
        elif 'array':
            setattr(cls, f'_{name}_mag', Column(JSON))
        setattr(cls, f'_{name}_unit', Column(String))
        prop = property(fset=lambda cls, value: cls.set_component_attribute(name, value, array_type),
                        fget=lambda cls: cls.get_component_attribute(name))
        setattr(cls, name, prop)
        if not hasattr(cls, '_attr_props'):
            cls._attr_props = {}
        cls._attr_props[name] = {'unit': unit, 'minimum': minimum, 'maximum': maximum}
        # print (self.attr_props[name])

    @classmethod
    def all_subclasses(cls, c=None):
        if c is None: c = cls
        return set(c.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in c.all_subclasses(c)])

    @classmethod
    def register_callback(cls, callback_type, func):
        print(cls)
        try:
            getattr(cls, callback_type).append(func)
        except AttributeError:
            cls.post_config_changed_callbacks = [func]

    def _check_value(self, name, value, param_type):
        unit = self._attr_props[name]['unit']

        uu.assert_compatible(value.units, unit)

        val = value.to(unit).magnitude
        min = self._attr_props[name]['minimum']
        max = self._attr_props[name]['maximum']

        if param_type == 'scalar' or param_type is None:
            if isinstance(value.magnitude, np.ndarray):
                raise ConfigurationError("Attempting to assign an array quantity to a scalar type parameter")
            if val < min:
                raise ConfigurationError(
                    f"attempting to set a value for attribute {name} that is less than the minimum of {min}{unit}")
            if val > max:
                raise ConfigurationError(
                    f"attempting to set a value for attribute {name} that is greater than the maximum of {max}{unit}")

        if param_type == 'array':
            if not isinstance(value.magnitude, np.ndarray):
                raise ConfigurationError("Attempting to assign an array quantity to a scalar type parameter")
            if (val < min).any():
                raise ConfigurationError(
                    f"attempting to set a value for attribute {name} that is less than the minimum of {min}{unit}")
            if (val > max).any():
                raise ConfigurationError(
                    f"attempting to set a value for attribute {name} that is greater than the maximum of {max}{unit}")

    def set_component_attribute(self, name, value, array_type):
        if value is not None:
            value = uu.parse_quantity(value)
            if not self._attr_props[name]['unit'] == 'no_check':
                self._check_value(name, value, array_type)

            if array_type == 'scalar' or array_type is None:
                mag = value.magnitude
            elif array_type == 'array':
                mag = value.magnitude.tolist()
            else:
                raise ValueError("type must be either 'scalar' or 'array'")

            setattr(self, f'_{name}_mag', mag)
            setattr(self, f'_{name}_unit', str(value.units))
        else:
            # setattr(self, name, None)
            setattr(self, f'_{name}_mag', None)
            setattr(self, f'_{name}_unit', None)

        if getattr(self, 'plant', None) is not None and (self.__class__.__name__ != 'Sensor'):
            # Update whether virtual sensor can be calculated with new plant information
            if not self.defer_post_config_changed_actions:
                [func(self.plant) for func in self.plant.post_config_changed_callbacks]

    def get_component_attribute(self, name):
        if self.__getattribute__(f'_{name}_mag') is None:
            return None
        return Q(self.__getattribute__(f'_{name}_mag'), self.__getattribute__(f'_{name}_unit'))

    def __getattr__(self, item):
        # print('attr==sens')
        if (item == "sensors") or ('_AssociationProxy__sensor_map' in item) or (
                item in ['_sa_instance_state', '_proxy_dicts']):
            raise AttributeError

        try:
            return self.sensors[item]
        except KeyError:
            if item in self.sensor_slots.keys():
                return None
            else:
                raise AttributeError(f"{item} not found in component {self}.")
        except (AttributeError, AssertionError, sqlalchemy.exc.InvalidRequestError) as ex:
            raise AttributeError(f"{item} not found in component {self}. Original exception: {ex}")

    @classmethod
    def get_default_unit(cls, name: str) -> str:
        """Return default unit of a class attribute defined as ComponentParam.
        """
        return cls._attr_props[name]['unit']

    def __str__(self):
        try:
            if self.name is not None:
                return f'HarvestIT {self.__class__.__name__} component called {self.name}'
            else:
                return f'HarvestIT {self.__class__.__name__} object'
        except sqlalchemy.exc.InvalidRequestError:
            return "unknown SunPeek component"

    def __repr__(self):
        return self.__str__()

    def __dir__(self):
        try:
            return list(self.sensor_slots.keys()) + list(super().__dir__())
        except AttributeError:
            return super().__dir__()


class AccuracyClass(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class InstallCondition(str, enum.Enum):
    perfect = "perfect"
    fair = "fair"
    bad = "bad"


class IsVirtual(str, enum.Enum):
    never = "never"
    possible = "possible"
    always = "always"


class ResultStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"


class SensorMap(ORMBase):
    """Class which defines the many-to-many mapping table and performs required logic to map Sensor objects to sensor
    channels on components.
    The `sensor_type` argument to the __init__ method determines the SensorType that will be attached to the sensor.
    If a sensor type has already been attached, attempting to create another mapping with a different type, a ConfigurationError
    will be raised.
    When a SensorMap is created, the sensor_type is not attached immediately. Instead, the `sensor_type_name` attribute
    of the sensor is set. When the SensorMap object is attached to a database session, a lookup is performed against the
    sensor_types table, and an appropriate SensorType object loaded and attached to the sensor.

    Attributes
    ----------

    sensor : py:class:sunpeek.components.sensor.Sensor
        The sensor object to be mapped
    slot_name: str
        The name of the sensor channel being mapped to, e.g. `te_amb`
    array : physical.Array
        Array object, if the mapping is to an array
    plant : physical.Plant
        Plant object, if the mapping is to a plant
    heat_exchanger : helpers.pyHeatExchanger
        HeatExchanger object, if the mapping is to a hx
    """
    __tablename__ = 'sensor_map'

    id = Column(Integer, Identity(0), primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id', ondelete="CASCADE"))
    slot_name = Column(String)

    component_id = Column(Integer, ForeignKey('components.component_id', ondelete="CASCADE"))

    # reference to the "Sensor" object
    sensor = relationship("Sensor", back_populates="mappings")
    component = relationship("Component", back_populates="_sensor_map")


    @sqlalchemy.orm.validates('sensor', include_removes=True)
    def _handle_unmaps(self, _, val, is_remove):
        if is_remove or val is None:
            self.unmap(include_sensor=False)
        return val

    def __init__(self, slot_name: str, sensor, sensor_type=None, component=None):
        if sensor is None:
            return
        self.slot_name = slot_name

        if isinstance(sensor, str):
            raise ConfigurationError(f'SensorMap was passed a string instead of a sensor object. This could be because '
                                     f'channel {slot_name} of {component} was mapped to a raw sensor that does not exist.')
            # This should have been excluded by _on_array_append
        if component.plant is None:
            raise ConfigurationError(f'Cannot map sensor to channel {slot_name} of component {component} because '
                                     f'component.plant is None.')

        if isinstance(sensor_type, str):
            type_name = sensor_type
        else:
            type_name = sensor_type.name
        if sensor.sensor_type is None:
            # sensor.sensor_type = type_name
            pass
        # elif sensor.sensor_type.name == type_name:
        #     pass
        elif sensor.sensor_type.name != type_name:
            raise ConfigurationError(
                f'Sensor {sensor.raw_name} already has type "{sensor.sensor_type.name}". Mapping to "{slot_name}" of '
                f'{component} requires type "{type_name}". Check your config.')

        sensor.plant = component.plant

        self.sensor = sensor

        self.component = component

        # In case the attribute for channel name was already set to None, remove it so that __getattr__ looks in sensors
        component.__dict__.pop(slot_name, None)
        sensor.plant = component.plant

    def unmap(self, include_sensor=True):
        self.component = None
        if include_sensor:
            self.sensor = None
        # session = sqlalchemy.orm.Session.object_session(self)
        # if session is not None:
        #     # Calling this inside an ORM object method isn't ideal, but seems to be necessary to avoid violating
        #     # `_unique_mapping_per_component_slot` constraint under certain circumstances.
        #     session.delete(self)
        #     session.flush()


class DataUploadDefaults(ORMBase):
    __tablename__ = 'data_upload_defaults'

    id = Column(Integer, Identity(0), primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", back_populates='data_upload_defaults')

    datetime_template = Column(Enum(DatetimeTemplates))
    datetime_format = Column(String)
    timezone = Column(String)
    csv_separator = Column(String)
    csv_decimal = Column(String)
    csv_encoding = Column(String)
    index_col = Column(Integer)


class PCSettingsDefaults(ORMBase):
    __tablename__ = 'pc_settings_defaults'

    id = Column(Integer, Identity(0), primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"), unique=True, nullable=False)
    plant = relationship("Plant", back_populates="pc_settings_defaults")

    evaluation_mode = Column(Enum('ISO', 'extended', name='pc_evaluation_modes'))
    formula = Column(Integer)
    wind_used = Column(Boolean)

    safety_uncertainty = Column(Float)
    safety_pipes = Column(Float)
    safety_others = Column(Float)

    def __init__(self, *args, **kwargs):
        self.evaluation_mode = "ISO"
        super().__init__(*args, **kwargs)


class UploadHistory(ORMBase):
    __tablename__ = 'upload_history'

    id = Column(Integer, Identity(0), primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"), nullable=False)
    plant = relationship("Plant", back_populates="upload_history")

    name = Column(String)
    size_bytes = Column(Float)
    status = Column(String)
    error_cause = Column(String)
    n_rows = Column(Integer)
    date_of_upload = Column(DateTime())
    start = Column(DateTime())
    end = Column(DateTime())
    _missing_columns = Column(String)       # list of string -> converted to string with ; as separator

    SEPARATOR = ";"

    @property
    def missing_columns(self):
        return [] if (self._missing_columns == "") else self._missing_columns.split(self.SEPARATOR)

    @missing_columns.setter
    def missing_columns(self, value):
        if isinstance(value, str):
            value = [value]
        self._missing_columns = "" if (value is None) else self.SEPARATOR.join(value)


# class Row(AttrSetterMixin, ORMBase):
#     """
#     Implements a single collector row with its inlet and outlet temperatures, as part of an Array.
#
#     Note
#     ----
#     An array may consist of several rows. Row components are useful if inlet or outlet temperatures (`te_in`,
#     `te_out`) are measured only at row level, and no measurements are available for the whole array. In this case,
#     one option would be to set the array level `te_in` | `te_out` as the average of all the array's rows.
#     Instantiating a Row only makes sense if either `te_in` or `te_out` (or both) are available measurement channels.
#
#     Attributes
#     ----------
#     array : Array object
#         Array to which the Row belongs.
#     te_in : Sensor, optional
#         Inlet / return temperature of collector row.
#     te_out : Sensor, optional
#         Outlet / flow temperature of collector row.
#     """
#     __tablename__ = 'rows'
#
#     id = Column(Integer, Identity(0), primary_key=True)
#     array_id = Column(Integer, ForeignKey(Array.id))
#     array = relationship("Array")
#
#     sensors = association_proxy("sensor_map", "sensor")
#
#     def __init__(self, array=None, te_in=None, te_out=None):
#         self.array = array
#         self.te_in = te_in
#         self.te_out = te_out
#
#         SensorMap('te_in', te_in, 'fluid_temperature', component=self)
#         SensorMap('te_out', te_out, 'fluid_temperature', component=self)


# array_results_association_table = sqlalchemy.Table('array_results_association', ORMBase.metadata,
#                                                    Column('result_id', primary_key=True),
#                                                    Column('result_time', primary_key=True),
#                                                    Column('array_id', ForeignKey('arrays.id'), primary_key=True),
#                                                    ForeignKeyConstraint(["result_id", "result_time"], ["pc_results.id",
#                                                                                                        "pc_results.datetime_eval_done"]),
#                                                    )


# AttrSetterMixin.define_component_attrs()


def make_tables(engine):
    """Uses the table definitions contained in the component classes to create DB tables"""
    ORMBase.metadata.create_all(engine)


class AlgoCheckMode(str, enum.Enum):
    config_only = 'config_only'
    config_and_data = 'config_and_data'
