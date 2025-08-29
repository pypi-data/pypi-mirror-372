import copy
from sqlalchemy import exc

import sunpeek.components as cmp
from sunpeek.common.errors import ConfigurationError, DuplicateNameError


def _check_collector_in_db(session, coll_name):
    if session is not None:
        import sqlalchemy.exc
        try:
            session.query(cmp.Collector).filter(cmp.Collector.name == coll_name).one()
            return True
        except sqlalchemy.exc.NoResultFound:
            return False
    return False


def make_full_plant(conf, session=None):
    conf = copy.deepcopy(conf)
    collectors = {}
    if 'collectors' in conf:
        colls = conf['collectors']
        for coll in colls:
            test_type = coll.pop('test_type')
            if _check_collector_in_db(session, coll['name']):
                coll_obj = coll['name']
            elif test_type in ['SST', "static"]:
                coll_obj = cmp.CollectorSST(**coll)
            elif test_type in ['QDT', "dynamic"]:
                coll_obj = cmp.CollectorQDT(**coll)
            else:
                raise ConfigurationError(
                    "Collector test_type parameter must be 'SST' or 'QDT'.")
            collectors[coll_obj.name] = coll_obj
    if 'plant' in conf:
        conf = conf['plant']
        for array in conf['arrays']:
            if array['collector'] in collectors.keys():
                array['collector'] = collectors[array['collector']]

    plant = cmp.Plant(**conf)

    if session is not None:
        session.add(plant)
        # session.rollback()

    return plant


def make_and_store_plant(conf, session):
    plant = make_full_plant(conf, session)
    session.add(plant)

    try:
        session.flush()
    except exc.IntegrityError as e:
        session.rollback()
        raise DuplicateNameError(f'Plant with name "{plant.name}" already exists.')

    return plant
