"""Temporary wrapper module of methods that used to be implemented in physical.Plant but caused circular import problems there.
"""
import os
from typing import List, Union
import pandas as pd

import sunpeek.data_handling.data_uploader as data_uploader


def use_dataframe(plant,  # physical.Plant
                  df: pd.DataFrame,
                  calculate_virtuals: bool = True,
                  **kwargs) -> Union[dict, None]:
    """Uses a dataframe as plant datasource. Includes configurable sanity checks on the given DataFrame.

    Parameters
    ----------
    plant : Plant
    df : pd.DataFrame. Must have a DateTimeIndex index.
    calculate_virtuals : bool. Whether virtual sensor calculation should be triggered (might be slow).
    """
    plant.context.use_dataframe(df, calculate_virtuals=calculate_virtuals, **kwargs)
    return


def use_csv(plant,  # physical.Plant
            csv_files: Union[str, os.PathLike, List[Union[str, os.PathLike]]],
            calculate_virtuals: bool = True,
            datetime_template: Union[data_uploader.DatetimeTemplates, str] = None,
            datetime_format: str = None,
            on_file_error: str = 'report',
            **kwargs) -> data_uploader.DataUploadResponse:
    """Ingest csv files, calculate virtual sensors, set Context datasource to dataframe.

    Returns
    -------
    import_info : DataUploadResponse, response from data upload process.
    """
    up = data_uploader.DataUploader_df(plant=plant,
                                       datetime_template=datetime_template,
                                       datetime_format=datetime_format,
                                       on_file_error=on_file_error,
                                       **kwargs)
    up.do_upload(files=csv_files, calculate_virtuals=calculate_virtuals)

    return up.output
