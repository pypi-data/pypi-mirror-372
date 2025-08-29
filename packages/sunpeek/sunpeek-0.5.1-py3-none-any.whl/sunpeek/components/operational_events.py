import sqlalchemy.orm
from sqlalchemy import Column, Identity, ForeignKey, Integer, DateTime, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import pytz
from pandas import to_datetime

from sunpeek.components.helpers import ORMBase
from sunpeek.common.errors import ConfigurationError, TimeZoneError


def _check_has_tz(val, val_name):
    if val.tzinfo is None:
        raise ConfigurationError(f"Operational event {val_name} timestamp must be timezone aware. Pass a tz aware datetime"
                                 f" object, or use set_start with a tz argument, or a string like 2022-1-1 00:00+02")


def _check_tz_matches(val, tz):
    if tz is not None and val.tzinfo is not None:
        if not pytz.timezone(tz).utcoffset(val.combine(val.date(), val.time())) == val.utcoffset():
            raise TimeZoneError('A timezone aware timestamp and a timezone argument were supplied, but the timezones did not match')


class OperationalEvent(ORMBase):
    __tablename__ = 'operational_events'

    id = Column(Integer, Identity(0), primary_key=True)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", back_populates="operational_events")
    _event_start = Column(DateTime)
    _event_end = Column(DateTime)
    original_timezone = Column(String)
    ignored_range = Column(Boolean)
    description = Column(String)

    def __init__(self, plant, event_start, event_end=None, tz=None, description=None, ignored_range=False):
        self.plant = plant
        self.set_start(event_start, tz)
        self.set_end(event_end, tz)
        self.ignored_range = ignored_range
        self.description = description
        self.original_timezone = tz

    @hybrid_property
    def event_start(self):
        try:
            if self._event_start is None:
                return self._event_start
            elif self._event_start.tzinfo is None:
                return pytz.timezone('utc').localize(self._event_start)
            else:
                return pytz.timezone('utc').normalize(self._event_start)
        except AttributeError:
            return self._event_start

    @event_start.setter
    def event_start(self, val):
        _check_has_tz(val, 'start')
        if val > self.event_end if self.event_end is not None else False:
            raise ConfigurationError('OperationalEvent end must be after start')
        self._event_start = pytz.timezone('utc').normalize(val)

    def set_start(self, val, tz=None):
        dt = to_datetime(val).to_pydatetime()
        _check_tz_matches(dt, tz)
        if tz is not None and dt.tzinfo is None:
            dt = pytz.timezone(tz).localize(dt)
        self.event_start = dt

    @hybrid_property
    def event_end(self):
        try:
            if self._event_end is None:
                return self._event_end
            elif self._event_end.tzinfo is None:
                return pytz.timezone('utc').localize(self._event_end)
            else:
                return pytz.timezone('utc').normalize(self._event_end)
        except AttributeError:
            return self._event_end

    @event_end.setter
    def event_end(self, val):
        if val is None:
            return
        _check_has_tz(val, 'end')
        if val < self.event_start if self.event_start is not None else False:
            raise ConfigurationError('OperationalEvent end must be after start')
        self._event_end = pytz.timezone('utc').normalize(val)

    def set_end(self, val, tz=None):
        if val is None:
            return
        dt = to_datetime(val).to_pydatetime()
        _check_tz_matches(dt, tz)
        if tz is not None and dt.tzinfo is None:
            dt = pytz.timezone(tz).localize(dt)
        self.event_end = dt
