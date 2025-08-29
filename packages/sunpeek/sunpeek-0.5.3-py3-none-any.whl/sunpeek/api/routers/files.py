from typing import List, Union
import warnings
import datetime as dt

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.datastructures import UploadFile
from sqlalchemy.orm import Session
import parquet_datastore_utils as pu

from sunpeek.common.utils import sp_logger
from sunpeek.db_utils import PARTITION_COLS
from sunpeek.common.time_zone import process_timezone
from sunpeek.data_handling.data_uploader import DataUploader_df, DataUploader_pq, DataUploadResponse, \
    DataUploadResponseFile, DataInspectionResponse
from sunpeek.api.dependencies import session, crud
from sunpeek.api.routers.plant import plant_router
from sunpeek.common.utils import DatetimeTemplates
from sunpeek.components.helpers import UploadHistory
from sunpeek.common.errors import SunPeekError

files_router = APIRouter(
    prefix="/data",
    tags=["data"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@files_router.post("/div-zero")
def zero_div():
    """This is a usage example only for the log class and the HTTP exception raising. It must be deleted for release.
    """
    try:
        x = 1 / 0
    except Exception as err:
        # how to use the logger to report an exception
        sp_logger.exception(err)
        # how to manually report using the INFO level
        sp_logger.info("This won't print in file because of loggers level")
        # str(err) gives the message related to the exception
        error_dict = {"message": "UPS something went wrong", "error": str(err)}
        # raise HTTPException so the API returns an error code instead of freezing
        raise HTTPException(status_code=500, detail=error_dict)


@plant_router.post("/data", tags=["data"],
                   summary='Upload measurement data to plant',
                   response_model=DataUploadResponse, status_code=201)
def upload_measure_data(
        plant_id: int,
        files: List[UploadFile],
        datetime_template: DatetimeTemplates = None,
        datetime_format: str = None,
        timezone: str = None,
        csv_separator: str = ';',
        csv_decimal: str = '.',
        csv_encoding: str = 'utf-8',
        index_col: int = 0,
        response: Response = Response(),
        sess: Session = Depends(session),
        crd: crud = Depends(crud)) -> DataUploadResponse:
    """Ingests csv files to database. For details, see docstring of the `data_uploader` module.

    Parameters
    ----------
    plant_id : A pre-configured plant with this name must exist in the database.
    files : list
        List of csv files that are batch ingested.
    datetime_template : DatetimeTemplates
        Templates to simplify the definition of a datetime format. Overridden by datetime_format (if not None).
    datetime_format : str
        Used to parse datetimes from csv file. Leave to None infers the format.
    timezone : str or pytz.timezone.
        Optional. To be provided if timestamps in the data have no time zone information.
    csv_separator : str
        Used in pd.read_csv as 'sep' kwarg
    csv_decimal : str
        Used in pd.read_csv as 'decimal' kwarg
    csv_encoding : str
        Used in pd.read_csv as 'encoding' kwarg
    index_col : int
        DataUploader will try to parse timestamps from this column.
    response : fastapi.Response
    sess : sqlalchemy.orm.Session
    crd : api.dependencies.crud

    Returns
    -------
    upload_response : DataUploadResponse

    Raises
    ------
    ConnectionError
    HTTPException
    """

    with warnings.catch_warnings(record=True) as wrngs:
        plant = crd.get_plants(sess, plant_id)
        up = DataUploader_pq(plant=plant,
                             datetime_template=datetime_template,
                             datetime_format=datetime_format,
                             timezone=timezone,
                             csv_separator=csv_separator,
                             csv_decimal=csv_decimal,
                             csv_encoding=csv_encoding,
                             index_col=index_col)
        out = up.do_upload(files=files)
        sess.commit()

    if wrngs is not None:
        response.headers['x-sunpeek-warnings'] = str([str(w.message) for w in wrngs])

    return out  # DataUploadResponse


@plant_router.delete("/data", tags=["data"],
                     summary='Delete measurement data from plant in given interval')
def delete_measure_data(plant_id: int,
                        start: dt.datetime,  # Timezone-aware timestamp, or will be interpreted as UTC
                        end: dt.datetime,  # Timezone-aware timestamp, or will be interpreted as UTC
                        sess: Session = Depends(session),
                        crd: crud = Depends(crud)) -> None:
    plant = crd.get_plants(sess, plant_id)
    plant.context.delete_sensor_data(start, end)


@plant_router.delete("/data/all", tags=["data"],
                     summary='Delete all data from plant')
def delete_all_data(plant_id: int,
                    sess: Session = Depends(session),
                    crd: crud = Depends(crud)) -> None:
    plant = crd.get_plants(sess, plant_id)
    plant.delete_all_data()


@plant_router.post("/data/columns", tags=["data"], response_model=DataInspectionResponse,
                   status_code=201)  # for backwards compatibility only
@plant_router.post("/data/inspection", tags=["data"], response_model=DataInspectionResponse, status_code=201)
def get_data_inspection(
        plant_id: int,
        files: List[UploadFile],
        csv_separator: str = ';',
        csv_decimal: str = '.',
        csv_encoding: str = 'utf-8',
        index_col: int = 0,
        datetime_template: DatetimeTemplates = None,
        datetime_format: str = None,
        timezone: str = None,
        response: Response = Response(),
        sess: Session = Depends(session),
        crd: crud = Depends(crud)) -> DataInspectionResponse:
    """Ingests csv files to database. For details, see docstring of the `data_uploader` module.

    Parameters
    ----------
    plant_id : A pre-configured plant with this name must exist in the database.
    files : list
        List of csv files that are batch ingested.
    csv_separator : str
        Used in pd.read_csv as 'sep' kwarg
    csv_decimal : str
        Used in pd.read_csv as 'decimal' kwarg
    csv_encoding : str
        Used in pd.read_csv as 'encoding' kwarg
    index_col : int
        DataUploader will try to parse timestamps from this column.
    datetime_template : DatetimeTemplates
        Templates to simplify the definition of a datetime format. Overridden by datetime_format (if not None).
    datetime_format : str
        Used to parse timestamps from csv file. Leave to None infers the format.
    timezone : str or pytz.timezone.
        Optional. To be provided if timestamps in the data have no time zone information.
    response : fastapi.Response
    sess : sqlalchemy.orm.Session
    crd : api.dependencies.crud

    Returns
    -------
    upload_response : DataColumnsResponse

    Raises
    ------
    ConnectionError
    HTTPException
    """

    with warnings.catch_warnings(record=True) as wrngs:
        plant = crd.get_plants(sess, plant_id)
        timezone = process_timezone(timezone, plant)
        up = DataUploader_df(plant=plant,
                             datetime_template=datetime_template,
                             datetime_format=datetime_format,
                             timezone=timezone,
                             csv_separator=csv_separator,
                             csv_decimal=csv_decimal,
                             csv_encoding=csv_encoding,
                             index_col=index_col)
        df = up.do_inspection(files=files)

        out = DataInspectionResponse(sensors=df.columns.tolist(),
                                     index=df.index.name,
                                     data=df.to_dict(orient='split'),
                                     dtypes=df.dtypes.astype(str).tolist(),
                                     settings=up.get_settings())

    if wrngs is not None:
        response.headers['x-sunpeek-warnings'] = str([str(w.message) for w in wrngs])

    return out


@plant_router.get("/data/history",
                  tags=["data"],
                  response_model=List[DataUploadResponseFile],
                  status_code=201,
                  summary="Get historic data uploads of the plant"
                  )
def get_data_history(plant_id: int, sess: Session = Depends(session), crd: crud = Depends(crud)):
    plant = crd.get_plants(sess, plant_id)
    uploads = plant.upload_history
    return uploads


@plant_router.delete("/data/history/{history_id}",
                     tags=["data"],
                     status_code=201,
                     summary="Delete a single entry of the data history by id"
                     )
def delete_data_history(plant_id: int, history_id: int, sess: Session = Depends(session), crd: crud = Depends(crud)):
    history_entry = sess.query(UploadHistory).get(history_id)
    if history_entry.plant_id != plant_id:
        raise SunPeekError("No entry found with matching id and plant_id")
    crd.delete_component(sess, history_entry)
    return
