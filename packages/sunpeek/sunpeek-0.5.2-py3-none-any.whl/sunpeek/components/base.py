import warnings
from typing import Union, Dict
import enum
import dataclasses
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy import Column, Integer, Identity, String
from sqlalchemy.orm.collections import attribute_mapped_collection

from sunpeek.common.errors import ConfigurationError
from sunpeek.common.unit_uncertainty import Q
from sunpeek.components import types
from sunpeek.components.helpers import IsVirtual, AttrSetterMixin, SensorMap, ORMBase, AlgoCheckMode
from sunpeek.components.sensor import Sensor


@dataclasses.dataclass
class SensorSlot:
    """
    A pydantic class used to hold and validate information on a component sensor slot.
    
    Parameters
    ----------
    name : str
        The name of the slot, which behaves like a component attribute and can be used to access the mapped sensor from
        the component. e.g. te_amb. `name` only needs to be unique and understandable in the context of a specific
        component, e.g. the `tp` slot of a plant includes the total power of all arrays, whereas `tp` of an array is
        just that array's power.
    descriptive_name : str
        A longer more descriptive name, e.g. for display to a user in a front end client. Limited to 24 characters
    description : str
        A description of the purpose and use of the slot.
    virtual : enum
        Whether the sensor for a slot is always virtual, can be virtual given certain conditions, or is never virtual
    """

    name: str
    sensor_type: types.SensorType
    descriptive_name: Union[str] = None
    virtual: IsVirtual = IsVirtual.never
    description: Union[str] = None
    # Idea: Implement SensorSlot availability, also see ComponentParam.available
    # available: Optional[bool] = None


class Component(ORMBase, AttrSetterMixin):
    """Base class to be used for physical components of a Plant, also specifies a DB table to allow polymorpic
    references to any subclass (i.e. via FK on components.id)"""

    __tablename__ = 'components'

    component_id = Column(Integer, Identity(), primary_key=True)

    sensor_slots: Dict[str, SensorSlot] = {}
    sensors = association_proxy("_sensor_map", "sensor")
    component_type = Column(String)
    __mapper_args__ = {
        "polymorphic_identity": "component",
        "polymorphic_on": component_type,
    }

    @declared_attr
    def _sensor_map(self):
        return relationship("SensorMap",
                            collection_class=attribute_mapped_collection("slot_name"),
                            cascade="all, delete-orphan")

    @property
    def sensor_map(self):
        return self._sensor_map

    @sensor_map.setter
    def sensor_map(self, str_map):
        if isinstance(str_map, dict):
            if not str_map:  # Nothing to do, avoid unnecessary call to plant.config_virtuals()
                return
            self.defer_post_config_changed_actions = True
            for slot_name, sensor in str_map.items():
                sensor = self.get_raw_sensor(sensor, raise_if_not_found=True)
                self.map_sensor(sensor=sensor, slot_name=slot_name)
                # elif sensor is None and slot_name in self.sensor_map:
                #     del self.sensor_map[slot_name]

            self.defer_post_config_changed_actions = False
            if self.plant is not None:
                [func(self.plant) for func in self.plant.post_config_changed_callbacks]

        else:
            raise ConfigurationError(f"sensor_map must be in the form {'slot_name:sensor_raw_name'}, got {str_map}.")

    def __setattr__(self, key, value):
        if key in self.sensor_slots:
            return self.map_sensor(value, key)
        return super().__setattr__(key, value)

    def update_sensors(self, is_remove):
        if is_remove:
            # Not doing in for loop because of "RuntimeError: dictionary changed size during iteration"
            vsensors = [s for s in self.sensors.values() if s.is_virtual]
            for sensor in vsensors:
                sensor.remove_references()
        else:
            for sensor in self.sensors.values():
                sensor.plant = self.plant

        return self

    def set_sensors(self, **kwargs):
        """Maps one or multiple sensors (by calling `map_sensor()`) and handles configuring virtual sensors.
        """
        self.defer_post_config_changed_actions = True
        for slot_name, sensor in kwargs.items():
            self.map_sensor(sensor, slot_name)
        self.defer_post_config_changed_actions = False
        if self.plant is not None:
            [func(self.plant) for func in self.plant.post_config_changed_callbacks]

    def map_sensor(self, sensor: Sensor, slot_name: str):
        """Maps sensor to slot_name of given component, including some sanity checks.
        """
        real_slots = [slot.name for slot in self.get_real_slots()]
        if sensor is not None and slot_name in real_slots:
            remove_old = False
            if self._sensor_map.get(slot_name) is not None:
                # If there is a mapping to the slot already, we need to explicitly unmap it before remapping, otherwise
                # we get 2 SensorMap objects referring to the same slot/component, the redundant one would be cleaned up
                # but triggers `_unique_mapping_per_component_slot` first.
                old_s = self.sensors[slot_name]
                self._sensor_map[slot_name].unmap(include_sensor=True)
                if old_s.is_virtual:
                    # If mapping real sensor to a slot that was previously calculated: Remove virtual sensor
                    remove_old = True

            self._sensor_map[slot_name] = SensorMap(slot_name, sensor, component=self,
                                                    sensor_type=self.sensor_slots[slot_name].sensor_type)
            if remove_old:
                # self.plant.raw_sensors.pop(self.plant.raw_sensors.index(old_s))
                old_s.remove_references()

        elif (not self.sensors[slot_name].is_virtual if self.sensors.get(slot_name) is not None else False):
            # If slot is not empty and sensor currently in slot is not virtual
            self.sensor_map[slot_name].unmap()
        elif self.sensors[slot_name].is_virtual:
            warnings.warn('You cannot set a virtual sensor directly. Virtual sensors are calculated automatically.')

        return

    def map_vsensor(self, slot_name: str, feedback: 'sunpeek.serializable_models.CoreMethodFeedback'):
        """Create virtual Sensor and map it to component.slot_name, or map None if it cannot be calculated.

        Parameters
        ----------
        slot_name : str, slot / channel name of the component self to which the virtual sensor will be mapped.
        feedback : CoreMethodFeedback, problems reported at config time, prior to vsensor calculation.
        """
        if not self.has_virtual_slot_named(slot_name):
            raise ConfigurationError(f'Cannot map virtual sensor because slot {slot_name} of {self} '
                                     f'does not accept virtual sensors.')
        # print(f'map_vsensor: component={self}, slot_name={slot_name}')
        try:
            sensor = self.sensors[slot_name]
        except KeyError:
            sensor = None

        can_calculate = feedback.success and (slot_name not in feedback.problem_slots)

        # Sensor already mapped? Update only, don't create new Sensor
        if sensor is not None:
            if sensor.is_virtual:
                sensor.problems = feedback
                sensor.can_calculate = can_calculate
            # Not virtual? Do nothing / Do not overwrite existing real sensor
            return

        # Create new sensor
        vsensor_name = f"{slot_name}__virtual__{self.__class__.__name__}_{self.name}".replace(' ', '_').lower()
        if (self.plant is not None) and (self.plant.get_raw_sensor(vsensor_name) is not None):
            # vsensor with matching name already exists in Plant
            sensor = self.plant.get_raw_sensor(vsensor_name)
            sensor.feedback = feedback
            sensor.can_calculate = can_calculate
        else:
            # Create virtual sensor
            # Needs to store compatible_unit of sensor_type, so it can later check if vsensor calc result units are ok.
            sensor = Sensor(is_virtual=True,
                            plant=self.plant,
                            raw_name=vsensor_name,
                            problems=feedback,
                            can_calculate=can_calculate,
                            native_unit=self.sensor_slots[slot_name].sensor_type.compatible_unit_str
                            )

        SensorMap(slot_name, sensor, component=self, sensor_type=self.sensor_slots[slot_name].sensor_type)

    def has_virtual_slot_named(self, slot_name):
        """Assert component has a (possibly or always) virtual sensor slot named slot_name.
        """
        vnames = [slot.name for slot in self.sensor_slots.values() if slot.virtual != IsVirtual.never]
        return slot_name in vnames

    @classmethod
    def get_real_slots(cls):
        """Get component's slot names for (possibly or always) real (not virtual) sensors
        """
        return [slot for slot in cls.sensor_slots.values() if slot.virtual != IsVirtual.always]

    def is_sensor_missing(self, slot_name: str, check_mode) -> bool:
        """Return True if component slot has no sensor mapped or sensor is not ready for calculations.
        """
        # May raise AttributeError
        sensor = getattr(self, slot_name)
        if sensor is None:
            return True
        if isinstance(sensor, Q):
            raise TypeError(f'In {self.name}, {self.__class__.__name__}.{slot_name} exists, '
                            f'but is a ComponentParam, not a sensor. Check the calling code.')
        if not sensor.is_virtual:
            return False

        # Virtual sensor "missing" status depends on check mode (config / config + data)
        if check_mode == AlgoCheckMode.config_only:
            is_slot_ok = sensor.can_calculate
        elif check_mode == AlgoCheckMode.config_and_data:
            is_slot_ok = sensor.data.notna().any()
        else:
            raise ValueError(f'Unexpected check_mode "{check_mode}". '
                             f'Expected: {", ".join(list(AlgoCheckMode))}')
        return not is_slot_ok

    def is_real_sensor_missing(self, slot_name: str, check_mode) -> bool:
        """Like is_sensor_missing, but additionally checks if sensor in named slot is real (not virtual).
        """
        sensor = getattr(self, slot_name)
        if sensor is None:
            return True
        if isinstance(sensor, Q):
            raise TypeError(f'In {self.name}, {self.__class__.__name__}.{slot_name} exists, '
                            f'but is a ComponentParam, not a sensor. Check the calling code.')
        if sensor.is_virtual:
            return True
        return False

    def is_attrib_missing(self, attrib_name) -> bool:
        """Return True if component attribute is None or not a ComponentParam holding a Quantity.
        """
        # May raise AttributeError
        attrib = getattr(self, attrib_name)
        if attrib is None:
            return True
        if isinstance(attrib, Sensor):
            raise TypeError(f'In {self.name}, {self.__class__.__name__}.{attrib_name} exists, '
                            f'but is a sensor, not a ComponentParam. Check the calling code.')
        if not isinstance(attrib, Q):
            return True
        return False

    def get_raw_sensor(self, str_map, raise_if_not_found=False):
        if str_map is None:
            return None
        return self.plant.get_raw_sensor(str_map, raise_if_not_found)

    # 2022-10-11 Currenly this method is not in use. If re-activated, also uncomment the tests in get_display_name
    # def get_display_name(self, slot_name: str, fmt: str = 'dru'):
    #     """Return display name in different formats, based on Sensor and SensorMap information.
    #     """
    #     if slot_name not in self.sensors:
    #         return None
    #     sensor = self.sensors[slot_name]
    #     map = self.sensor_map[slot_name]
    #     raw = sensor.raw_name.split('___virtual')[0] if sensor.is_virtual else sensor.raw_name
    #     raw = '(' + raw + ')'
    #     descriptive = map.descriptive_name
    #     # pint string formatting: https://pint.readthedocs.io/en/0.10.1/tutorial.html#string-formatting
    #     # unit = None if sensor.native_unit is None else f"{sensor.native_unit:~H}"
    #     unit = 'None' if sensor.native_unit is None else f"{sensor.native_unit:~P}"
    #     unit = '[' + unit + ']'
    #
    #     if fmt in ['r', 'raw']:
    #         return raw
    #     if fmt in ['d', 'descriptive']:
    #         return descriptive
    #     if fmt in ['u', 'unit']:
    #         return unit
    #     if fmt == 'ru':
    #         return f"{raw} {unit}"
    #     if fmt == 'du':
    #         return f"{descriptive} {unit}"
    #     if fmt == 'rd':
    #         return f"{raw} {descriptive}"
    #     if fmt == 'dr':
    #         return f"{descriptive} {raw}"
    #     if fmt == 'dru':
    #         return f"{descriptive} {raw} {unit}"
    #     if fmt == 'dur':
    #         return f"{descriptive} {unit} {raw}"
    #     raise NotImplementedError(f'Format {fmt} not implemented.')
