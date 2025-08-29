"""
This module implements data access and data handling.

The Context class implements 2 data backends: database and dataframe.
- Database is e.g. for use over WebUI, DataFrame for use as a package and for testing.
A sensor cache is implemented to speed up database access times.
- To quickly add csv data / test something, just do: use_csv(plant, [file_list])

Internally, data is always stored without unit (double / float64); the correct unit (stored in sensor.native_unit)
is attached at data access.
"""
from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
import enum
import datetime as dt
import warnings
from typing import Union, Dict, Tuple
from dataclasses import dataclass
import pandas as pd
import pytz
from pydantic import validator

import parquet_datastore_utils as pu
from sunpeek.common.utils import sp_logger
from sunpeek.base_model import BaseModel
from sunpeek.db_utils import DATETIME_COL_NAME, PARTITION_COLS
import sunpeek.common.errors as err
from sunpeek.common.time_zone import validate_timezone
import sunpeek.core_methods.virtuals as virtuals


class NanReportResponse(BaseModel):
    nan_report: Union[Dict[str, str], None]

    @validator('nan_report', pre=True)
    def df_to_val(cls, dct):
        if dct is not None:
            return {k: v.to_json(date_format='iso') for k, v in dct.items() if not isinstance(v, str)}


def import_db_ops():
    """Import the db_data_operations module and raises a specific error if any of the required modules is missing.
    This is used because some functions in this module only need the db modules imported when using the database backend
    """
    try:
        import sunpeek.db_utils.db_data_operations as db_ops
        return db_ops
    except ModuleNotFoundError:
        raise ModuleNotFoundError("Some modules that a required to work with the database backend are not installed. "
                                  "They can be installed with pip install sunpeek[db].")


def sanitize_index(df: pd.DataFrame) -> (pd.DataFrame, int):
    """Sort DataFrame index, removes NaN entries and duplicates. Guarantees df has a sorted and unique DatetimeIndex.

    Parameters
    ----------
    df : pandas.DataFrame, must have DatetimeIndex.

    Returns
    -------
    tuple : DataFrame with sanitized index, and number of duplicate time index entries (handy to spot error in data
    definition, where certain time stamps happen to exist twice if the wrong time zone is selected).

    Raises
    ------
    err.TimeIndexError : If df has no DatetimeIndex or the resulting index is not sorted (monotonic increasing).

    Notes
    -----
    All duplicate entries are deleted. Automatically keeping any of them (e.g. always keep the first entry) is risky
    because duplicates in the time index typically point to a problem in data logging or tagging, e.g. wrong time zone
    setting in a data logger, or time zone mis-specifiec in SunPeek, or time zone changed at some point during the
    data acquisition interval, etc.
    """
    if df is None:
        return None, 0

    if not isinstance(df.index, pd.DatetimeIndex):
        raise err.TimeIndexError(f'Index error in DataFrame uploaded or passed to backend: Expected DatetimeIndex, '
                                 f'but got {type(df.index)}.')

    df = df[~df.index.isna()]
    # Some core methods require data to be sorted (e.g. PC Method extended -> rolling operation)
    df = df.sort_index()
    # Check for duplicate indices
    is_duplicate = df.index.duplicated(keep=False)
    n_duplicates_index = is_duplicate.sum()
    df = df[~is_duplicate]

    if not df.index.is_monotonic_increasing:
        raise err.TimeIndexError('Index error in DataFrame uploaded or passed to backend: '
                                 'index could not be sorted (index is non-monotonic).')

    # Index is always stored in UTC to avoid possible issues with parquet etc.
    # See https://gitlab.com/sunpeek/sunpeek/-/issues/500
    df.index = df.index.tz_convert('UTC')

    return df, n_duplicates_index


class DataSources(str, enum.Enum):
    pq = "pq"  # parquet
    parquet = "pq"
    df = "df"  # dataframe
    dataframe = "df"
    none = "none"


class DataCache:
    """Implements an ephemeral storage of sensor data and time index.
    Data access from cache is faster than reading from parquet, and should be about
    the same as from DataFrame.
    This :class:`DataCache` is a lightweight wrapper around a dictionary. It implements some additional
    checks / sanitizing and utils for using the cache.
    """

    def __init__(self):
        self.cache = {}

    def add(self, key: str, val: pd.Series | pd.DatetimeIndex,
            ) -> None:
        if val is None:
            return
        # Sanitize input
        if not self.is_empty and (len(self) != len(val)):
            raise ValueError(f'Cannot add value of length {len(val)}. '
                             f'Cache must have unique length. Length is fixed at {len(self)}.')
        self.cache[key] = val

    def get(self, key: str, none_if_not_found: bool = False) -> pd.Series | pd.DatetimeIndex | None:
        if key not in self:
            if none_if_not_found:
                return None
            raise KeyError(f'No value for key {key} found in cache.')
        return self.cache[key]

    def reset(self):
        self.cache = {}

    def __contains__(self, key: str) -> bool:
        return key in self.cache

    def __len__(self):
        # "vertical len", the len of pd.Series | DatetimeIndex
        if self.is_empty:
            return None
        return len(next(iter(self.cache.values())))

    @property
    def is_empty(self):
        # True if cache holds no values
        return len(self.cache.keys()) == 0


class DataOperations:
    """This class encapsulates common data operations and data processing.
    It uses DataOps objects, depending on the given context datasource.
    DataOperations does not interfere with the context cache. Cache operations should be done in Context.
    """

    def __init__(self, context):
        self.context = context

    @property
    def data_ops(self):
        match self.context.datasource:
            case DataSources.dataframe:
                return DataOps_df(self.context)
            case DataSources.parquet:
                return DataOps_pq(self.context)
            case _:
                raise err.ConfigurationError(f'Cannot perform operation: Invalid context.datasource. '
                                             f'Maybe Context is uninitialized. '
                                             f'Context.datasource is {self.context.datasource.none}.')

    def get_time_index(self) -> pd.DatetimeIndex | None:
        return self.data_ops.get_time_index()

    def get_sensor_data(self, sensor: 'sunpeek.components.Sensor') -> pd.Series:
        s = self.data_ops.get_sensor_data(sensor)
        if s is None:
            raise err.ConfigurationError(f'Retrieved sensor value for {sensor.raw_name} is None.')

        # Attach unit, call data cleaning
        s = self._process_data__native_unit(sensor, s)
        native_unit = sensor.native_unit if (sensor.native_unit is not None) else ""
        s = s.astype(f'pint[{native_unit}]')

        return s

    def delete_sensor_data(self, start: dt.datetime, end: dt.datetime) -> None:
        match self.context.datasource:
            case DataSources.dataframe:
                df = self.data_ops.delete_sensor_data(start, end)
                self.context.use_dataframe(df)
            case DataSources.parquet:
                self.data_ops.delete_sensor_data(start, end)
        return

    def delete_all_data(self) -> None:
        self.data_ops.delete_all_data()
        return

    def sanitize_virtual_data(self, sensor: 'sunpeek.components.Sensor', data: pd.Series) -> pd.Series:
        # If a virtual sensor calculation was not possible (for whatever reason), Context will store an all-NaN series.
        idx = self.context.time_index
        if data is None:
            return pd.Series(data=np.nan, index=idx, name=sensor.raw_name)

        if len(data) != len(idx):
            raise err.CalculationError(f'Size of virtual sensor data {len(data)} '
                                       f'is incompatible with size of Plant.time_index {len(idx)}.')

        data.index = idx
        # pint unit is stored with sensor.native_unit and attached at context.get_sensor_data
        # Double astype() needed to go from 'pint[xx]' to numpy float, not only to PandasDtype('float64')
        data = data.astype(float).astype(float)
        data.name = sensor.raw_name
        # All subsequent algorithms shall rely that everything is either a number or NaN.
        # Inf may arise in virtual sensors, e.g. CoolProp returns Inf when temperature exceeds allowed range.
        data[~np.isfinite(data)] = np.nan

        return data

    def flush_virtuals(self) -> None:
        # Only for parquet datasource: batch write virtuals to parquet
        if self.context.datasource != DataSources.parquet:
            raise ValueError("Storing virtual sensor data to parquet is only possible for parquet datasource.")
        self.data_ops.flush_virtuals()

    def _process_data__native_unit(self,
                                   sensor: 'sunpeek.components.Sensor',
                                   s_raw: pd.Series) -> pd.Series:
        """This is the main data processing method, it implements e.g. min max filtering, plant.ignored_ranges etc.
        This method is intended for sensor data which is given as numeric pd.Series, not dtype pint, to accelerate
        runtime.

        Parameters
        ----------
        sensor : Sensor. Process this sensor's data.
        s_raw : pd.Series
            Unprocessed data for sensor, with float (or equiv.) dtype, typically obtained from self.get_sensor_data()

        Returns
        -------
        s : pd.Series
            Processed data for sensor, with numeric dtype.
        """
        # Copying is necessary to avoid that data processing overwrites the dataframe column with processed values.
        # This ensures that data processing is done on the fly, and changing e.g. data processing limits or
        # a sensor native_unit will still use the originally-parsed values (from data_uploader),
        # as opposed to the previously processed values.
        s = s_raw.copy()

        # Set values in ignored ranges to NaN
        for ignored_range in self.context.plant.ignored_ranges:  # pd.Interval
            mask = (s.index >= ignored_range.left) & (s.index <= ignored_range.right)
            s[mask] = np.nan

        # Lower and Upper replacement intervals (see HarvestIT #177)
        s = self._replace_lower__native(s, sensor)
        s = self._replace_upper__native(s, sensor)

        return s

    @staticmethod
    def _replace_lower__native(data: pd.Series,
                               sensor: 'sunpeek.components.Sensor') -> pd.Series:
        """Implement lower replacement interval, see #177.

        Parameters
        ----------
        data : pd.Series with unprocessed data
        sensor : Sensor

        Returns
        -------
        s : pd.Series with replaced values.
        """
        left, right, replace = sensor.value_replacements__native['lower']
        if (left is None) and (right is None) and (replace is None):
            # all None: nothing to do
            return data

        if right is None and replace is None:
            # no replacement value given, only left is not None
            data[data < left] = np.nan
            return data

        if left is None and replace is None:
            # no replacement value given, only right is not None
            data[data < right] = np.nan
            return data

        if left is None:
            data[data < right] = replace
            return data

        # all are not-NaN
        data[data < left] = np.nan
        data[(data >= left) & (data < right)] = replace
        # Does not work, package incompatibility... s[(s >= left) & (s < right)] = replace
        return data

    @staticmethod
    def _replace_upper__native(data: pd.Series,
                               sensor: 'sunpeek.components.Sensor') -> pd.Series:
        """Implement upper replacement interval, see #177.

        Parameters
        ----------
        data : pd.Series with unprocessed data
        sensor : Sensor

        Returns
        -------
        s : pd.Series with replaced values.
        """
        left, right, replace = sensor.value_replacements__native['upper']
        if (left is None) and (right is None) and (replace is None):
            # all None: nothing to do
            return data

        if left is None and replace is None:
            # no replacement value given, only right is not None
            data[data > right] = np.nan
            return data

        if right is None and replace is None:
            # no replacement value given, only left is not None
            data[data > left] = np.nan
            return data

        if right is None:
            data[data > left] = replace
            return data

        # all are not-NaN
        data[data > right] = np.nan
        data[(data > left) & (data <= right)] = replace
        return data


class DataOps(ABC):
    """Interface for data operations supported by Context datasource.
    """

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def get_time_index(self):
        pass

    @abstractmethod
    def get_sensor_data(self, sensor):
        pass

    @abstractmethod
    def delete_sensor_data(self):
        pass

    @abstractmethod
    def delete_all_data(self):
        pass


class DataOps_df(DataOps):
    """Data operations for dataframe datasource.
    """

    def get_time_index(self) -> pd.DatetimeIndex | None:
        df = self.context.df
        if df is None:
            return None
        idx = df.index
        idx = idx[(idx >= self.context.eval_start) & (idx <= self.context.eval_end)]

        return idx

    def get_sensor_data(self, sensor) -> pd.Series:
        df = self.context.df
        if sensor.raw_name not in df.columns:
            raise KeyError(f'Data for sensor {sensor.raw_name} was not found in the dataframe.'
                           f' The context datasource is {self.context.datasource}.')
        s = df.loc[self.context.eval_start:self.context.eval_end, sensor.raw_name]
        return s

    def delete_sensor_data(self, start: dt.datetime, end: dt.datetime) -> pd.DataFrame | None:
        # Delete data, return DataFrame with remaining data
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError('In a context with dataframe datasource, start and end must be timezone-aware.')
        if start > end:
            raise ValueError(f'Timestamp "start" must be equal or less than "end". You provided '
                             f'start={start.isoformat()}, end={end.isoformat()}.')
        df = self.context.df
        filtered_df = df.loc[(df.index < start) | (df.index > end)]
        filtered_df = filtered_df if len(filtered_df) else None
        return filtered_df

    def delete_all_data(self) -> None:
        self.context._df = None
        self.context.set_eval_interval()

class DataOps_pq(DataOps):
    """Data operations for parquet datasource.
    """

    def get_time_index(self) -> pd.DatetimeIndex | None:
        try:
            idx = pu.read(self.context.plant.raw_data_path, columns=[DATETIME_COL_NAME],
                          start_end=(self.context.eval_start, self.context.eval_end)).index
            if not len(idx):
                return None
        except FileNotFoundError:  # returned by parquet-datastore-utils if data folder doesn't exist
            return None
        return idx

    def get_sensor_data(self, sensor) -> pd.Series:
        plant = self.context.plant
        uri = plant.calc_data_path if sensor.is_virtual else plant.raw_data_path
        type_dict = {sensor.raw_name: str} if getattr(sensor.sensor_type, 'compatible_unit_str', '') == 'str' else \
            {sensor.raw_name: float}
        sensor_data_df = pu.read(uri=uri, columns=[sensor.raw_name], types_dict=type_dict,
                                 start_end=(self.context.eval_start, self.context.eval_end))
        s = sensor_data_df.squeeze()
        return s

    def delete_sensor_data(self, start: dt.datetime, end: dt.datetime) -> None:
        # Start and end format required by parquet-datastore-utils.
        pd_dates = [pd.to_datetime(x) for x in [start, end]]
        start_, end_ = ({'timestamp': x.to_pydatetime(), 'year': x.year, 'quarter': x.quarter} for x in pd_dates)
        pu.delete_between(self.context.plant.raw_data_path, start_, end_, partition_cols=PARTITION_COLS)
        pu.delete_between(self.context.plant.calc_data_path, start_, end_, partition_cols=PARTITION_COLS)
        return

    def delete_all_data(self) -> None:
        """Delete parquet directories for raw and calc data.
        """
        def rmtree(root):
            # Remove directory tree + contents
            if not root.exists():
                # This may happen if plant has no data uploaded
                return
            for p in root.iterdir():
                if p.is_dir():
                    rmtree(p)
                else:
                    p.unlink()
            root.rmdir()

        plant = self.context.plant
        for f in [plant.raw_data_path, plant.calc_data_path]:
            rmtree(Path(f))
        self.context.set_eval_interval()
        return

    def flush_virtuals(self) -> None:
        df = pd.DataFrame({name: self.context.cache.get(name).astype(float).astype(float)
                           for name in self.context.plant.get_raw_names(only_virtuals=True)})

        # is needed so partitions are always done with utc
        df, n_duplicated = sanitize_index(df)

        # Double astype() needed to go from 'pint[xx]' to numpy float, not only to PandasDtype('float64')
        assert set(PARTITION_COLS) == {'year', 'quarter'}, 'Partition columns changed. Need to adapt Context code.'
        df['year'] = df.index.year
        df['quarter'] = df.index.quarter
        pu.write(data=df, uri=self.context.plant.calc_data_path, partition_cols=PARTITION_COLS, overwrite_period=True)


class Context:
    @dataclass
    class EvalInterval:
        start: dt.date | None
        end: dt.date | None

        DEFAULT_START = pd.to_datetime('1970-01-01 00:00', utc=True)
        DEFAULT_END = pd.to_datetime('2200-01-01 00:00', utc=True)

        def __post_init__(self):
            self.start = self.start or self.DEFAULT_START
            self.end = self.end or self.DEFAULT_END
            if isinstance(self.start, pd.Timestamp):
                self.start = self.start.to_pydatetime()
            if isinstance(self.end, pd.Timestamp):
                self.end = self.end.to_pydatetime()

            for x in (self.start, self.end):
                if not isinstance(x, dt.date):
                    raise TypeError('Context limits expected to be of type datetime.')
                if x.tzinfo is None:
                    raise err.TimeZoneError(
                        "Both elements of a Context eval_interval tuple must be timezone-aware datetime objects.")
            if self.end <= self.start:
                raise ValueError('A Context eval_interval must be increasing: end must be greater than start.')

    def __init__(self, plant,
                 datasource: DataSources | str | None = None,
                 dataframe: pd.DataFrame = None,
                 df_timezone: str = None,
                 eval_start: dt.date | None = None,
                 eval_end: dt.date | None = None,
                 ):
        if plant is None:
            raise err.ConfigurationError('Context parameter "plant" must not be None.')
        self.plant = plant
        self._datasource = DataSources.none
        self._eval_interval = self.EvalInterval(eval_start, eval_end)
        self.cache = DataCache()
        self._df = None

        if datasource is None:
            return

        if dataframe is not None:
            if datasource == DataSources.parquet:
                raise ValueError('Cannot create Context with parquet datasource when given dataframe.')
            self.datasource = DataSources.df
            self.use_dataframe(dataframe, timezone=df_timezone, )
            return

        # Either df datasource, without dataframe, or parquet datasource
        self.datasource = datasource

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, val):
        raise NotImplementedError('You cannot directly set a Context DataFrame. Use context.use_dataframe() instead.')

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, val: DataSources | str):
        self._datasource = DataSources(val)
        if self._datasource == DataSources.parquet:
            self._df = None
        self.cache.reset()

    @property
    def eval_start(self):
        return self._eval_interval.start

    @property
    def eval_end(self):
        return self._eval_interval.end

    @property
    def time_index(self) -> pd.DatetimeIndex | None:
        if self.datasource is None:
            return None
        idx = self.cache.get(DATETIME_COL_NAME, none_if_not_found=True)
        if idx is None:
            idx = DataOperations(self).get_time_index()
            self.cache.add(DATETIME_COL_NAME, idx)

        if idx is None:
            return None

        index = idx.tz_convert(self.plant.tz_data)
        return index

    def get_data_start_end(self) -> Tuple[dt.datetime, dt.datetime] | None:
        """Get timestamps when data associated with the plant start and end.
        """
        if self.datasource == DataSources.none:
            return None

        self.cache.reset()
        self.set_eval_interval()
        idx = self.time_index
        if idx is None:
            return None
        return idx[0], idx[-1]

    def get_sensor_data(self, sensor: 'sunpeek.components.Sensor') -> pd.Series:
        """Given a sensor and raw data Returns processed data for a given sensor. Usually called as sensor.data

        Parameters
        ----------
        sensor : Sensor. Data are returned in this sensor's native units, with time zone aware DatetimeIndex.

        Returns
        -------
        pd.Series, Processed sensor values

        Notes
        -----
        - If sensor is found in cache, unprocessed data is returned (since the data in the cache is already processed).
        - If sensor is not in cache, data is processed (see DataOperations class).
        """
        s = self.cache.get(sensor.raw_name, none_if_not_found=True)
        if s is None:
            s = DataOperations(self).get_sensor_data(sensor)
            self.cache.add(sensor.raw_name, s)

        # Convert to plant data time zone
        s = s.tz_convert(self.plant.tz_data)
        s = s[~s.index.duplicated(keep='first')]

        return s

    def delete_sensor_data(self, start: dt.datetime, end: dt.datetime) -> None:
        """Delete measurement data from plant in given interval.
        """
        self.cache.reset()
        DataOperations(self).delete_sensor_data(start, end)

    def delete_all_data(self) -> None:
        """Delete all data, as if it had never been uploaded.
        In contrast to delete_sensor_data(), this also works for corrupted parquet files.
        """
        DataOperations(self).delete_all_data()

    def set_eval_interval(self,
                          eval_start: dt.datetime | pd.Timestamp | None = None,
                          eval_end: dt.datetime | pd.Timestamp | None = None,
                          check_overlap: bool = False,
                          method_name: str = '',
                          ) -> None:
        """Try the best to get meaningful eval_interval from available info.
        """
        self.cache.reset()
        self._eval_interval = self.EvalInterval(start=eval_start, end=eval_end)

        if check_overlap:
            overlap = self._check_overlap(eval_start, eval_end, method_name)
            self.set_eval_interval(overlap.left, overlap.right)

    def _check_overlap(self,
                       start: dt.datetime | pd.Timestamp | None,
                       end: dt.datetime | pd.Timestamp | None,
                       method_name: str = '') -> pd.Interval:
        """Return state of uploaded data with respect to given interval (start, end). Return state and overlap interval.
        Raises
        ------
        :class:`err.NoDataError`
        """
        raise_msg = '' if not method_name else f'Cannot run {method_name}. '

        # No datasource set?
        if self.datasource == DataSources.none:
            msg = 'Context has a None datasource. Check if data have been added to the plant.'
            raise err.NoDataError(raise_msg + msg)

        # No data uploaded?
        data_start_end = self.get_data_start_end()
        if not data_start_end:
            msg = 'No data have been uploaded to the plant.'
            raise err.NoDataError(raise_msg + msg)
        uploaded_rng_msg = f'Uploaded measurement data range: {data_start_end[0]} to {data_start_end[-1]}.'

        # No data / not enough data available?
        if len(self.time_index) < 2:
            msg = f'No measurements available for the plant in the selected range {start} to {end}. ' + uploaded_rng_msg
            raise err.NoDataError(raise_msg + msg)

        # No overlap?
        i_data = pd.Interval(pd.to_datetime(data_start_end[0]), pd.to_datetime(data_start_end[-1]), closed='both')
        start = start or i_data.left
        end = end or i_data.right
        i_context = pd.Interval(pd.to_datetime(start), pd.to_datetime(end), closed='both')
        try:
            overlap = pd.Interval(max(i_data.left, i_context.left).tz_convert(self.plant.tz_data),
                                  min(i_data.right, i_context.right).tz_convert(self.plant.tz_data), closed='both')
        except ValueError:
            msg = f'No measurements available in the range {start} to {end}. ' + uploaded_rng_msg
            raise err.NoDataError(raise_msg + msg)

        # Overlap, but no timestamps in overlap
        overlap_idx = ((self.time_index >= overlap.left) & (self.time_index <= overlap.right))
        if overlap_idx.sum() < 2:
            msg = f'No measurements available for the plant in the selected range {start} to {end}. ' + uploaded_rng_msg
            raise err.NoDataError(raise_msg + msg)

        return overlap

    def use_dataframe(self,
                      df: pd.DataFrame,
                      calculate_virtuals: bool = False,
                      timezone: Union[str, pytz.timezone] = None,
                      drop_unneeded_columns: bool = False,
                      missing_columns: str = 'ignore',
                      eval_start: dt.date | None = None,
                      eval_end: dt.date | None = None,
                      ) -> None:
        """Configures Context to use the supplied dataframe as the datasource, instead of accessing the database.

        Parameters
        ----------
        df : pd.DataFrame. Must have a DateTimeIndex index.
        calculate_virtuals : bool. Whether virtual sensor calculation should be triggered (might be slow).
        timezone : timezone string or pytz timezone, example 'Europe/Berlin' or 'UTC' or pytz.FixedOffset(60).
        missing_columns : str, one of ['ignore', 'raise', 'nan']. Treatment of real sensor names expected but not found
        in the df columns.
        drop_unneeded_columns : bool. If True, columns not needed according to plant.get_raw_names(True) are dropped.
        eval_start, eval_end : dt.datetime. Limit the data to part of the provided DataFrame.

        Notes
        -----
        - Only numeric information in df is used. pint dtypes are ignored. No automatic unit conversion implemented.
        - Treatment of missing columns in df compared to expected sensor raw_names: missing_columns kwarg
        """
        if df is None:
            df_none_warning = 'Cannot set DataFrame in Context: DataFrame is None.'
            sp_logger.warning(df_none_warning)
            warnings.warn(df_none_warning)
            self._df = None
            self.cache.reset()
            self.set_eval_interval(None, None)
            return None

        df.index = validate_timezone(df.index, timezone=timezone, plant=self.plant)
        df, n_duplicates = sanitize_index(df)

        # Store only numeric data.
        for (col, dtype) in zip(df.columns, df.dtypes):
            if not pd.api.types.is_numeric_dtype(dtype):
                raise ValueError(
                    "To use a DataFrame as data source for a plant / Context, "
                    "the DataFrame must only contain numeric columns. "
                    f"Column {col} has dtype {dtype}.")
        # pint unit dtype is added at sensor.data, or plant.context.get_sensor_data()
        df = df.astype('float64', errors='raise')

        assert missing_columns in ['ignore', 'raise', 'nan'], f'Invalid "missing_columns": {missing_columns}'
        if missing_columns != 'ignore':
            cols_missing = set(self.plant.get_raw_names(include_virtuals=False)) - set(df.columns)
            if (len(cols_missing) > 0) and (missing_columns == 'raise'):
                raise ValueError(
                    f'DataFrame does not have all required columns. Columns missing: {cols_missing}.')
            if cols_missing == 'nan':
                df[cols_missing] = np.nan

        # Drop unneeded columns (not used by any sensor in the self.plant)
        if drop_unneeded_columns:
            df = df.drop(df.columns.difference(self.plant.get_raw_names(include_virtuals=True)), axis=1)

        self.datasource = DataSources.dataframe
        self._df = df
        self.set_eval_interval(eval_start, eval_end)

        if calculate_virtuals:
            virtuals.calculate_virtuals(self.plant)
        else:
            virtuals.config_virtuals(self.plant)

        return

    def store_virtual_data(self, sensor: 'sunpeek.components.Sensor', data: pd.Series) -> None:
        """Stores virtual sensor calculation results in the cache and, if the datasource is `df`, to the dataframe. If
        the datasource is `pq`, data will _not_ be stored by this method; in this case, `flush_virtuals_to_parquet`
        method should be used when all virtual sensor updates have been completed.

        Parameters
        ----------
        sensor : Sensor. Data will be stored for this virtual sensor.
        data : Union[pd.Series, None]
            Virtual sensor calculation results, with dtype numeric.

        Returns
        -------
        Nothing, new data is stored in the context DataFrame self.df

        Notes
        -----
        - Assumes dataframe backend for speed reason. Calling code needs to take care of storing things to database.
        - Also populates cache
        """
        data = DataOperations(self).sanitize_virtual_data(sensor, data)

        if self.datasource == DataSources.dataframe:
            self.df[sensor.raw_name] = data
        # For parquet, all virtual sensors are stored in batch, see `flush_virtuals_to_parquet`

        # Populate cache for faster data retrieval in subsequent accesses (mostly within virtual sensor calculations)
        self.cache.add(sensor.raw_name, data.astype(f'pint[{sensor.native_unit}]'))

    def flush_virtuals_to_parquet(self) -> None:
        """Store all virtual sensor data from sensor cache to the configured parquet storage.
        """
        DataOperations(self).flush_virtuals()

    # NaN report -----------

    N_TOTAL_TIMESTAMPS = "n_total_timestamps"
    N_AVAILABLE_TIMESTAMPS = "n_available_timestamps"
    NAN_DENSITY_IN_AVAILABLE = "nan_density_in_available"

    def get_nan_report(self,
                       include_virtuals: bool = False) -> NanReportResponse:
        """Data quality information about the plant's sensors' NaN values, taking ignored ranges into account.

        Returns
        -------
        nan_report : dict
            Dictionary keys are sensor.raw_name, dictionary value is a DataFrame reporting data quality.
            DataFrame index are all days between first and last data (within current context limits), regardless whether
            for data of a specific day were included in the current upload. DataFrame column names and descriptions:
            - `n_total_timestamps`: Number of total uploaded timestamps, including timestamps in ignored ranges
            - `n_available_timestamps`: Number of timestamps available for analysis, that is: outside ignored ranges
            - `nan_density_in_available`: NaN density (ratio of NaNs to all values), outside ignored ranges
        """
        # not_ignored: marks the relevant pieces of data. True if timestamp is not within ignored range
        not_ignored = pd.Series(True, index=self.time_index)
        for r in self.plant.ignored_ranges:
            mask = (self.time_index >= r.left) & (self.time_index <= r.right)
            not_ignored.loc[mask] = False

        sensor_names = self.plant.get_raw_names(include_virtuals=include_virtuals)
        nan_report = {s: self._create_sensor_nan_report(not_ignored, self.plant.get_raw_sensor(s))
                      for s in sensor_names}

        nrr = NanReportResponse()
        nrr.nan_report = nan_report

        return nrr

    def _create_sensor_nan_report(self, not_ignored: pd.Series, sensor: 'sunpeek.components.Sensor') -> pd.DataFrame:
        """For a given DataFrame and sensor (raw_name), create a DataFrame, aggregating NaN information by day.

        Parameters
        ----------
        not_ignored : pd.Series, True where outside an ignored range.
        sensor : Sensor

        Returns
        -------
        df : pd.DataFrame with DatetimeIndex. See docstring of `Context.get_nan_report()`.
        """
        # Total number of timestamps per day
        days = self.time_index.date
        n_total_timestamps = not_ignored.groupby(by=days).count()

        # Number of not_ignored timestamps per day == available ranges
        n_available_timestamps = not_ignored.groupby(by=days).sum()

        # Nans in available ignored ranges (the ones that actually hurt)
        is_nan_in_available = sensor.data.isna() & not_ignored
        n_nans_in_available = is_nan_in_available.groupby(by=days).sum()

        # Nan density in available ranges.
        nan_density_in_available = n_nans_in_available / n_available_timestamps

        df_out = pd.concat([n_total_timestamps.rename(self.N_TOTAL_TIMESTAMPS),
                            n_available_timestamps.rename(self.N_AVAILABLE_TIMESTAMPS),
                            nan_density_in_available.rename(self.NAN_DENSITY_IN_AVAILABLE),
                            ], axis=1)
        df_out.index = pd.to_datetime(df_out.index)

        return df_out

    def verify_time_index(self) -> None:
        """Make sure context time_index is accessible.
        """
        self.time_index
        return
