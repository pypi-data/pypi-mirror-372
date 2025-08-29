import json
import tarfile, tempfile, io, time, os
import pandas as pd
import sqlalchemy
import sqlalchemy.orm
from typing import Union
import platform
import parquet_datastore_utils as pu

import sunpeek
import sunpeek.components as cmp
import sunpeek.common
from sunpeek.components.helpers import ResultStatus
import sunpeek.serializable_models as smodels
from sunpeek.db_utils import db_data_operations, crud
import sunpeek.common.utils
# from sunpeek.db_utils import DATETIME_COL_NAME


def create_export_config(plant):
    collectors = [array.collector for array in plant.arrays]
    fluid_definitions = [plant.fluid_solar.fluid if plant.fluid_solar is not None else None]

    return {"collectors": collectors,
            "fluid_definitions": fluid_definitions,
            "plant": plant}


def _bundle(conf, sensors, plant, session):
    years = plant.time_index.year.unique()
    conf_file = io.BytesIO(bytes(conf.json(), 'UTF-8'))
    temp_handle, temp_path = tempfile.mkstemp(suffix='.tar.gz')
    index = pd.Series(plant.time_index, index=plant.time_index)

    with tarfile.open(temp_path, 'w:gz') as tf:
        info = tarfile.TarInfo(name=f"configuration_{plant.name}.json")
        info.size = len(conf_file.getbuffer())
        info.mtime = time.time()
        conf_file.seek(0)
        tf.addfile(tarinfo=info, fileobj=conf_file)

        for year in years:
            start = index[str(year)][0]
            end = index[str(year)][-1]
            df_raw = pu.read(uri=plant.raw_data_path,
                             columns=[sensor.raw_name for sensor in sensors if not sensor.is_virtual])
            df_calc = pu.read(uri=plant.calc_data_path,
                              columns=[sensor.raw_name for sensor in sensors if sensor.is_virtual])
            df = pd.concat([df_raw, df_calc], axis=1)
            f = io.BytesIO()
            df.to_csv(f, sep=';')
            info = tarfile.TarInfo(name=f"rawdata_{plant.name}_{year}.csv")
            info.size = len(f.getbuffer())
            info.mtime = time.time()
            f.seek(0)
            tf.addfile(tarinfo=info, fileobj=f)

        os.close(temp_handle)
        return temp_path


def _update_job(job, attr, value):
    if job:
        setattr(job, attr, value)
    return job


def create_export_package(plant: cmp.Plant, include_virtuals: bool, job: cmp.Job=None):
    session = sqlalchemy.orm.object_session(plant)
    if session is None:
        # Because this function can be called as a background job, session may have been closed before function runs.
        session = sunpeek.common.utils.S()
        session.add(plant)

    if include_virtuals:
        sensors = [sensor for sensor in plant.raw_sensors if not sensor.is_virtual]
    else:
        sensors = [sensor for sensor in plant.raw_sensors]

    job = _update_job(job, 'status', ResultStatus.running)
    crud.update_component(session, job)

    try:
        conf = smodels.ConfigExport(**create_export_config(plant))
        temp_path = _bundle(conf, sensors, plant, session)

        job = _update_job(job, 'status', ResultStatus.done)
        job = _update_job(job, 'result_path', temp_path)
        crud.update_component(session, job)
        session.close()
        return temp_path
    except:
        _update_job(job, 'status', ResultStatus.failed)
        session.close()
        raise
    session.close()

def _get_plants_config(plants):
    confs = []
    for plant in plants:
        confs.append(json.loads(smodels.Plant.from_orm(plant).json())) #Ensure we can convert to json later if needed
    return confs


def dump_debug_info(include_plants: Union[bool, list] = True, include_db_structure: bool = True, file_path: str = None,
                    session: sqlalchemy.orm.Session = None):
    """
    Creates a file in memory containing various information that is useful for reproducing issues for debugging purposes.
    Can optionally write this to disk or return the file object.

    Parameters
    ----------
    include_plants : bool or list of plant names
        True to include all plants, False for none or specify the names of specific plants to include
    include_db_structure : bool
        Whether to include a list of database tables and their columns. If include_plants is a list, only raw data
        tables for plants listed will be included
    file_path : str
       An optional path to write the output to. If this is given, the absolute path to the output file will be returned.
    session : sqlalchemy.orm.Session
       An optional database session object, required if include_plants or include_db_structure is True

    Returns
    -------
    out : dict or absolute output file path as str
    """

    out = {}
    out['version'] = sunpeek.__version__
    out['platform'] = platform.platform()
    out['architecture'] = platform.architecture()
    out['in_docker'] = os.path.exists('/.dockerenv')

    if session is None and (include_db_structure or include_plants):
        raise TypeError('include_db_structure or include_plants was True with session set to None. '
                        'Need a valid database session to get plant or database structure information.')
    elif session is None:
        return out

    include_plants_is_list = False
    if include_plants:
        plants = session.query(cmp.Plant).all()
        out['plant_configurations'] = _get_plants_config(plants)
    else:
        try:
            plants = [session.query(cmp.Plant).where(cmp.Plant.name == name).one() for name in include_plants]
            out['plant_configurations'] = _get_plants_config(plants)
            include_plants_is_list = True
        except TypeError:
            pass

    if include_db_structure:
        db_tables = {}
        metadata = sqlalchemy.MetaData()
        metadata.reflect(sunpeek.common.utils.db_engine)
        for table in metadata.tables.values():
            if include_plants_is_list and 'raw_data' in table.name and any([plant_name in table.name for plant_name in include_plants]):
                continue
            if not include_plants and 'raw_data' in table.name:
                continue
            db_tables[table.name] = {'columns': [col.name for col in table.columns]}
        out['database_tables'] = db_tables

    if file_path is None:
        return out
    else:
        with open(file_path, 'w') as f:
            json.dump(out, f)
    return os.path.abspath(file_path)
