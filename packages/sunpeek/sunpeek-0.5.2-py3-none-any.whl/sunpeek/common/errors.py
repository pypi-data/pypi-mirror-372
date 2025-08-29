class SunPeekError(Exception):
    pass


class ConfigurationError(SunPeekError):
    pass


class CollectorDefinitionError(SunPeekError):
    """Error in Collector definition.
    E.g. if supplied information is contradictory or not sufficient for full Collector definition.
    See #70 for valid Collector definitions.
    """
    pass


class IncompatibleUnitError(SunPeekError):
    """Supplied unit (of raw sensor) is not compatible with the expected unit, e.g. as defined in SensorType.
    """
    pass


class VirtualSensorConfigurationError(SunPeekError):
    """Error in calcluation of virtual sensor due to missing input or input being None.
    """
    pass


class PCMethodError(SunPeekError):
    """General error in definition / configuration / calculation of PC method.
    """
    pass


class CalculationError(SunPeekError):
    """General error in definition / handling of virtual senso.
    """
    pass


class AlgorithmError(SunPeekError):
    """Error in some core_method algorithm.
    """
    pass


class DuplicateNameError(SunPeekError):
    """Error due to creating a component with a duplicate name, where this is not allowed"""
    pass


class SensorNotFoundError(SunPeekError):
    """Error due to not finding a sensor when one was expected to exist"""
    pass


class SensorDataNotFoundError(SunPeekError):
    """Error due to not finding a data column for a sensor in the current data store"""
    pass


class NoDataError(SunPeekError):
    """No data are available in the selected data range"""
    pass


class TimeIndexError(SunPeekError):
    """Error handling or retrieving plant.time_index."""
    pass


class TimeZoneError(SunPeekError):
    """Error related to time zone"""
    pass


class DataProcessingError(SunPeekError):
    """Error related to data upload and processing"""
    pass


class DatabaseAlreadyExistsError(SunPeekError):
    pass
