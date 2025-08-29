"""
Implements the data ingestion process as roughly described in HarvestIT #187.
Data source backend can either be DataFrame or database (as implemented in Context class).
This module implements the same data ingestion process for both data sources.

Instantiate with DataUploader_df or DataUploader_pq,
then do_upload() to trigger the upload.

Data ingestion is implemented in this module. Data stored (in database or dataframe) have gone through some
sanity checking. As a result, we can rely on having a timezone-aware, sorted datetime index with no duplicates,
data is either numeric or NaN, all component slots are populated with data.
The same import & sanity procedures are used for both database and dataframe backend.
Any further, dynamic data processing steps are done on-the-fly (see `Context` class), things like ignored intervals and
min-max replacement intervals.
In this way, for instance, an ignored range can be added or deleted in a plant, and sensor data will behave
accordingly. This is implemented in common.context.

Data ingestion triggers virtual sensor calculation.
do_upload() returns data quality check ("sensor validation"), available as per-day and per-sensor information.

Notes
-----
Main method is do_upload() which returns the upload response in a dict. What it does:
- checks timezone info in csv files
- handles strings in data
- sorts timestamps and drops duplicates
- calculates virtual sensors
- calls sensor validation and kernel method validation
- uploads data to store in raw_data table in db#
"""

import os
import warnings
import pathlib
import numpy as np
from typing import List, Union
import pendulum
import pandas as pd
import pytz
from io import BytesIO
import datetime as dt
from pydantic import validator
from charset_normalizer import from_fp

import sunpeek.common.time_zone as time_zone
from sunpeek.common.utils import DatetimeTemplates, sp_logger
from sunpeek.db_utils import DATETIME_COL_NAME, PARTITION_COLS
from sunpeek.data_handling.context import Context, sanitize_index
from sunpeek.base_model import BaseModel
from sunpeek.common.errors import DataProcessingError, TimeZoneError
import parquet_datastore_utils as pu
from sunpeek.common.time_zone import process_timezone
from sunpeek.components.helpers import UploadHistory


class DataUploadResponseFile(BaseModel):
    name: Union[str, None]
    exists: Union[bool, None]
    size_bytes: Union[int, None]
    missing_columns: List[str] = []
    error_cause: Union[str, None]

    status: Union[str, None]
    date_of_upload: Union[dt.datetime, None]
    start: Union[dt.datetime, None]
    end: Union[dt.datetime, None]
    n_rows: Union[int, None]
    id: Union[int, None]


class DataUploadResponse(BaseModel):
    n_uploaded_data_rows: Union[int, None]
    n_duplicates_index: Union[int, None]
    response_per_file: Union[List[DataUploadResponseFile], None]
    db_response: Union[dict, None]


class DataUploadSettings(BaseModel):
    csv_separator: Union[str, None]
    csv_decimal: Union[str, None]
    csv_encoding: Union[str, None]
    index_col: Union[int, None]
    datetime_template: Union[str, None]
    datetime_format: Union[str, None]
    timezone: Union[str, None]

    @validator('datetime_template', pre=True)
    def to_string(cls, v):
        if isinstance(v, DatetimeTemplates):
            return str(v.value)
        return str(v)

    @validator('timezone', pre=True)
    def to_string_pytz(cls, v):
        return str(v)


class DataInspectionResponse(BaseModel):
    sensors: Union[List[str], None]
    dtypes: Union[List[str], None]
    index: Union[str, None]
    settings: Union[DataUploadSettings, None]
    data: Union[dict, None]


class DataUploader_df:
    """
    Data uploads of csv files to a plant using Context backend with datasource 'dataframe'.

    Notes
    -----
    - This class does not need and not use the database. Use DataUploader_pq for parquet backend.
    - The csv files need not be in chronological order.
    - Number of columns needs not be the same across files.
    - Time zone information must either be given in csv timestamps or as timezone.
    """

    def __init__(self,
                 plant,
                 datetime_template: DatetimeTemplates = None,
                 datetime_format: str = None,
                 timezone: Union[str, pytz.timezone] = None,
                 csv_separator: str = ';',
                 csv_decimal: str = '.',
                 csv_encoding: str = 'utf-8',
                 index_col: int = 0,
                 eval_start: dt.date = None,
                 eval_end: dt.date = None,
                 on_file_error: str = 'report',
                 ):
        """
        Parameters
        ----------
        plant : Plant
        timezone : str or pytz.timezone.
            Optional. To be provided if timestamps in the data have no time zone information.
        csv_separator : str
            Used in pd.read_csv as 'sep' kwarg
        csv_decimal : str
            Used in pd.read_csv as 'decimal' kwarg
        csv_encoding : str
            Used in pd.read_csv as 'encoding' kwarg
        datetime_format : str
            Used to parse datetimes from csv file. Leave to None infers the format.
        index_col : int
            DataUploader will try to parse timestamps from this column.
        eval_start : dt.datetime
            Limit the data that is read and imported
        eval_end : dt.datetime
            Limit the data that is read and imported
        on_file_error : str
            Behaviour if an error is encountered reading a file, either `report` to store details in the file response
            and continue, or `raise`, to raise the error and stop.
        """
        if (datetime_template is None) and (datetime_format is None):
            raise DataProcessingError('Either "datetime_template" or "datetime_format" needs to be specified.')

        self.plant = plant
        self.eval_start = eval_start
        self.eval_end = eval_end
        self.datetime_format = datetime_format
        self.datetime_template = DatetimeTemplates[datetime_template] if isinstance(datetime_template,
                                                                                    str) else datetime_template
        self._original_timezone = timezone
        self.timezone = process_timezone(timezone, plant=self.plant)
        self.csv_decimal = csv_decimal
        self.index_col = index_col
        self.on_file_error = on_file_error
        self.csv_separator = csv_separator
        self.csv_encoding = csv_encoding
        self.output = DataUploadResponse()

    def read_csv(self, csv, **kwargs):
        return pd.read_csv(csv, on_bad_lines='skip', parse_dates=False, dtype='str', **kwargs)

    def get_settings(self):
        return self.__dict__

    @staticmethod
    def __validate_files(files):
        if files is None:
            raise DataProcessingError('No files to upload supplied.')
        if not isinstance(files, list):
            files = [files]
        if not (len(files) > 0):
            raise DataProcessingError('No files to upload supplied.')
        return files

    @staticmethod
    def _to_BytesIO(bio_or_file):  # noqa
        if hasattr(bio_or_file, 'filename'):
            bio = bio_or_file.file
        elif isinstance(bio_or_file, str) or isinstance(bio_or_file, os.PathLike):
            with open(bio_or_file, 'rb') as f:
                bio = BytesIO(f.read())
        else:
            # could be many types: BytesIO,  io.BufferedReader, tempfile.SpooledTemporaryFile, ...
            bio = bio_or_file
        bio.seek(0)
        return bio

    def do_upload(self, files: Union[str, os.PathLike, List[Union[str, os.PathLike]]],
                  calculate_virtuals: bool = True) -> DataUploadResponse:
        """Full measurement data ingestion process, also triggers virtual sensor calculation and sensor validation.

        Parameters
        ----------
        files : UploadFile, str, os.PathLike
            Files to upload.
        calculate_virtuals : bool
            Whether to trigger virtual sensor calculation.

        Raises
        ------
        FileNotFoundError
        ConnectionError

        Returns
        -------
        DataUploadResponse : Response from the data upload, various info fields.
        """
        start_time = pendulum.now()

        files = self.__validate_files(files)
        df = self._parse_files(files)
        self.plant.context = Context(plant=self.plant, datasource='df')
        self.plant.context.use_dataframe(df, calculate_virtuals=calculate_virtuals)
        self._post_upload()

        sp_logger.debug(f"[data_uploader] --- Finished after {(pendulum.now() - start_time).total_seconds():.1f} seconds ---")
        return self.output

    def _parse_files(self, files):
        """Concatenates the uploaded files into a single df.

        Notes
        -----
        - Columns which do not match with any of the plant's sensor raw_names are dropped.
        - Works for fastAPI's UploadFile as well as for normal csv files.
        """
        sp_logger.debug(f"[data_uploader] Reading csv files to DataFrame.")
        sp_logger.debug(f"[data_uploader] Concatenating {len(files)} files.")
        start_time = pendulum.now()

        # Iterate trough files and gather DataFrames
        df_all_files = None
        self.output.response_per_file = []
        for file in files:
            file_response = UploadHistory(plant=self.plant, date_of_upload=dt.datetime.now())
            try:
                # is either a FlaskApi File or file-path, or a BytesIO object
                if hasattr(file, 'filename'):
                    file_response.name = file.filename
                    file_response.exists = True
                elif isinstance(file, str) or isinstance(file, pathlib.Path):
                    file_response.name = os.path.basename(file)
                    file_response.exists = os.path.exists(file)
                    if not file_response.exists:
                        raise FileNotFoundError(f'Cannot find file: "{file_response.name}".')
                elif isinstance(file, BytesIO):
                    file_response.name = None
                    file_response.exists = True
                else:
                    raise FileNotFoundError(f'Cannot interpret input for file: "{file}".')

                # get size
                bio = self._to_BytesIO(file)
                bio.seek(0, os.SEEK_END)
                file_response.size_bytes = bio.tell()
                bio.seek(0)

                try:
                    # parsing file
                    expected_sensors = self.plant.get_raw_names(include_virtuals=False)
                    df_file = self._parse_single_file(bio, usecols=expected_sensors)

                    # after-processing
                    df_file = df_file.rename_axis(DATETIME_COL_NAME)
                    missing_columns = set(expected_sensors) - set(df_file.columns)
                    df_file[list(missing_columns)] = np.nan

                    # get statistics
                    file_response.start = df_file.index.min()
                    file_response.end = df_file.index.max()
                    file_response.missing_columns = missing_columns
                    file_response.n_rows = len(df_file)

                    # Check if df has at least one column, except index col and valid timestamps
                    if len(missing_columns) == len(expected_sensors):
                        raise ValueError("Uploaded file contains no data columns that match with sensor names.")
                    elif len(df_file.index) == 0:
                        raise ValueError("Uploaded file contains no valid timestamps. "
                                         "Is it possible that the uploaded file contains no measurement data?")

                except Exception as ex:
                    sp_logger.warning(ex)
                    file_response.error_cause = f'Error: {ex}'
                    if self.on_file_error == 'raise':
                        raise
                    warnings.warn(f'Failed to read csv file using pandas read_csv. {ex}')
                    continue

                # Concatenate the dataframes
                if len(df_file) > 0:
                    df_all_files = pd.concat([df_all_files, df_file], ignore_index=False)
                    if not isinstance(df_all_files.index, pd.DatetimeIndex):
                        raise DataProcessingError('Cannot concatenate DataFrames with mixed timezones since this '
                                                  'results in the DataFrame index not being a DatetimeIndex anymore.')

            finally:
                self.output.response_per_file.append(file_response)

        # Check for duplicates etc.
        df_all_files, n_duplicates_index = sanitize_index(df_all_files)
        self.output.n_duplicates_index = n_duplicates_index
        if self.output.n_duplicates_index:
            duplicate_warning = f"Found {self.output.n_duplicates_index} duplicate index entries in data. " \
                                f"All rows with duplicate index will be removed."
            sp_logger.warning(duplicate_warning)
            warnings.warn(duplicate_warning)

        if (df_all_files is None) or len(df_all_files) < 2:
            df_all_files = None
            self.output.n_uploaded_data_rows = 0
            df_none_warning = 'Reading csv files resulted in a DataFrame with less than 2 rows.'
            sp_logger.warning(df_none_warning)
            warnings.warn(df_none_warning)
        else:
            self.output.n_uploaded_data_rows = len(df_all_files)

        sp_logger.debug(
            f"[data_uploader] --- Done parsing {len(files)} files in {(pendulum.now() - start_time).total_seconds():.1f} seconds.")
        return df_all_files

    def _parse_single_file(self, bio, usecols=None, nrows=None) -> pd.DataFrame:
        """Read a BytesIO object to DataFrame.

        Parameters
        ----------
        bio : BytesIO object or File
            From an UploadFile or from a normal csv file.

        Returns
        -------
        df : pandas.DataFrame
            DataFrame with tz-aware DatetimeIndex

        Raises
        ------
        AssertionError

        Notes
        -----
        - Returns a DataFrame with DatetimeIndex taken from the first column, index is named according to
         sunpeek.db_utils.DATETIME_COL_NAME.
        - Missing columns are added as all-NaN columns.
        """
        bio = self._to_BytesIO(bio)

        # If bounds (start|end) are provided, the index column is parsed alone, to determine rows to skip.
        # this is a slight overhead as the file is read twice. However, it can speed up the data import when a lot of
        # rows are skipped. In addition, this allows to skip line which would lead to errors otherwise.
        skiprows = None
        bounds_provided = (self.eval_start is not None) or (self.eval_end is not None)
        if bounds_provided:
            index = self.read_csv(bio, usecols=[self.index_col], encoding=self.csv_encoding, sep=self.csv_separator,
                                  nrows=nrows).iloc[:, 0]
            index = self.__parse_datetime_index(index)

            skiprows = index.isna()
            if self.eval_start is not None:
                skiprows = skiprows | (index < self.eval_start)
            if self.eval_end is not None:
                skiprows = skiprows | (index > self.eval_end)
            skiprows = [i for i, x in enumerate(np.insert(skiprows, 0, False)) if x]

        # Pandas requires that index_column name is inside usecols
        index_col = self.index_col
        if usecols is not None:
            index_name = self.get_index_name(bio)
            all_cols = [index_name] + usecols
            usecols = lambda x: x in all_cols
            index_col = index_name

        # load data
        bio.seek(0)
        try:
            df = self.read_csv(bio,
                               usecols=usecols,
                               skiprows=skiprows,
                               nrows=nrows,
                               index_col=[index_col],
                               encoding=self.csv_encoding,
                               sep=self.csv_separator
                               )
        except UnicodeDecodeError as e:
            bio.seek(0)
            suggested_encoding = from_fp(bio).best().encoding  # The most probable encoding string
            raise DataProcessingError(f'Cannot parse file due to an encoding problem. '
                                      f'Probably, "{self.csv_encoding}" is not the right encoding of this file. '
                                      f'We suggest to try the "{suggested_encoding}" encoding. '
                                      f'Original error message: {str(e)}')

        # conversion to valid date
        df.index = self.__parse_datetime_index(df.index.to_series())

        # read_csv with decimal kwarg fails when reading string, hence the two calls to apply()
        if self.csv_decimal is not None:
            df = df.apply(lambda x: x.str.replace(self.csv_decimal, '.'))
        df = df.apply(pd.to_numeric, errors='coerce')

        return df

    def __parse_datetime_index(self, ds):
        try:
            if self.datetime_format is not None:
                fmt = self.datetime_format
                day_first = None
                year_first = None
            else:
                fmt = None
                day_first = True if (self.datetime_template == DatetimeTemplates.day_month_year) else False
                year_first = True if (self.datetime_template == DatetimeTemplates.year_month_day) else False

            ds = pd.to_datetime(ds, errors='coerce', format=fmt, dayfirst=day_first, yearfirst=year_first)
            ds = pd.DatetimeIndex(ds)

            if ds.isna().all():
                raise DataProcessingError(
                    f"Pandas to_datetime was unable to parse timestamps from the file, given datetime_format="
                    f"{self.datetime_format} and datetime_template={self.datetime_template}."
                    f"Please check your input for 'datetime_format'.")

            ds = time_zone.validate_timezone(ds, timezone=self._original_timezone, plant=self.plant)
            return ds

        except (DataProcessingError, TimeZoneError):
            raise
        except (pd.errors.ParserError, ValueError) as e:
            raise DataProcessingError(
                f"Pandas to_datetime was unable to parse timestamps from the file, given datetime_template="
                f"{self.datetime_template}. Try to set an explicit 'datetime_format' instead.")
        except Exception as e:
            # Mixed timezone timestamp columns lead to Index class df.index with dtype 'object'
            # see https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html
            raise TimeZoneError(
                '[data_uploader] Could not convert timestamps of the csv file to a DatetimeIndex. '
                'One cause why this happens are mixed-timezone timestamps or only some rows having timezones.', e)

    def do_inspection(self, files, nrows=500) -> pd.DataFrame:
        """Returns the data of an example measurement file (or BytesIO) for inspection purposes.
        The same method as do_upload is called, but without storing the data or restricting expected columns
        """
        files = self.__validate_files(files)
        bio = self._to_BytesIO(files[0])
        df = self._parse_single_file(bio, nrows=nrows)

        return df

    def get_index_name(self, files):
        """Returns name of the index column based on an example file (or BytesIO)
        Parameters
        ----------
        files : UploadFile, str, os.PathLike
            Files to upload.
        """
        files = self.__validate_files(files)
        bio = self._to_BytesIO(files[0])
        df = self.read_csv(bio, nrows=0, encoding=self.csv_encoding, sep=self.csv_separator)

        return list(df.columns.values)[self.index_col]

    def _post_upload(self):
        pass


class DataUploader_pq(DataUploader_df):
    """
    Data upload from csv files to parquet datastore.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sensor_raw_names = None
        self.raw_data_path = self.plant.raw_data_path
        self.calc_data_path = self.plant.calc_data_path

    def _post_upload(self) -> None:
        """This comes after self.do_upload(), so we have a dataframe context and all data in the context dataframe.
        """
        # Behavior of uploader is to start with a dataframe context.
        df = self.plant.context.df
        if df is None:
            # Do nothing, this is already accounted for by Context. 
            return

        # (actually already done, but to be on the safe side)
        df, n_duplicated = sanitize_index(df)

        df['year'] = df.index.year
        df['quarter'] = df.index.quarter

        raw_df = df[self.plant.get_raw_names(include_virtuals=False) + PARTITION_COLS]
        calc_df = df[self.plant.get_raw_names(only_virtuals=True) + PARTITION_COLS]

        pu.write(data=raw_df, uri=self.raw_data_path, partition_cols=PARTITION_COLS, overwrite_period=True)
        pu.write(data=calc_df, uri=self.calc_data_path, partition_cols=PARTITION_COLS, overwrite_period=True)

        # From now on, data is accessed by 'pq' and uses the full datetime range available in the datastore
        self.plant.context = Context(plant=self.plant, datasource='pq')
