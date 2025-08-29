import json
import datetime as dt
from sqlalchemy.orm import Session

import sunpeek.demo
from sunpeek.common import config_parser
from sunpeek.data_handling import data_uploader
from sunpeek.data_handling.wrapper import use_csv
from sunpeek.db_utils import crud
import sunpeek.components as cmp
import sunpeek.core_methods.virtuals as virtuals


def requires_demo_data(func):
    if not sunpeek.demo.DEMO_DATA_AVAILABLE:
        raise ModuleNotFoundError(
            "This function requires optional dependency sunpeek-demo. Install it with `pip install sunpeek[demo]`")
    return func


@requires_demo_data
def create_demoplant(session: Session, name: str = None):
    with open(sunpeek.demo.DEMO_CONFIG_PATH, 'r') as f:
        conf = json.load(f)

    # Plant name must be unique in database => create unique
    if name is None:
        name = f'demoplant_{dt.datetime.now().strftime("%Y%m%d_%H%M%S")}'
    conf['plant']['name'] = name

    config_parser.make_and_store_plant(conf, session)

    plant = crud.get_plants(session, plant_name=name)
    virtuals.config_virtuals(plant)
    session.commit()
    return plant


@requires_demo_data
def add_demo_data(plant: cmp.Plant, session: Session = None):
    files = [sunpeek.demo.DEMO_DATA_PATH_1MONTH]
    timezone = 'UTC'
    datetime_template = data_uploader.DatetimeTemplates.year_month_day

    if session is not None:
        up = data_uploader.DataUploader_pq(plant=plant,
                                           timezone=timezone,
                                           datetime_template=datetime_template,
                                           )
        up.do_upload(files=files)  # includes virtual sensor calculation
        session.commit()
    else:
        use_csv(plant, csv_files=files,
                timezone=timezone,
                datetime_template=datetime_template)
