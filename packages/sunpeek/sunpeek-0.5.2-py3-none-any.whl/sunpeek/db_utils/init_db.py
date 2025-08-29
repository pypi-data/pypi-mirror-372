import os
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlalchemy.exc
import alembic
import alembic.config
import importlib
from sunpeek.common.unit_uncertainty import Q

import sunpeek.components as cmp
from sunpeek.common import utils
from sunpeek.definitions import collectors, fluid_definitions


def init_db():
    db_url = utils.get_db_conection_string()
    importlib.reload(collectors)
    importlib.reload(fluid_definitions)
    if not database_exists(db_url):
        utils.sp_logger.info(f'[init_db] Attempting to setup fresh DB {os.environ.get("HIT_DB_NAME", "harvestit")} on '
                             f'{os.environ.get("HIT_DB_HOST", "localhost:5432")}')

        create_database(db_url)
        cmp.make_tables(utils.db_engine)

        with utils.S.begin() as session:
            # Add collectors
            for item in collectors.all_definitions:
                session.add(item)

            # Add fluids
            for item in fluid_definitions.all_definitions:
                session.add(item)

            session.commit()
            session.expunge_all()

        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
        alembicArgs = ['--raiseerr', 'stamp', 'head']
        alembic.config.main(argv=alembicArgs)
    else:
        apply_db_migrations()


def apply_db_migrations():
    utils.sp_logger.info(f'[init_db] Applying migrations and updates to DB {os.environ.get("HIT_DB_NAME", "harvestit")} '
                         f'on {os.environ.get("HIT_DB_HOST", "localhost:5432")}')
    os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))
    alembic.config.main(argv=['--raiseerr', 'upgrade', 'head'])

    col_types = [(item, item.name) for item in collectors.all_definitions]
    fluid_defs = [(item, item.name) for item in fluid_definitions.all_definitions]

    with utils.S.begin() as session:
        with session.no_autoflush:
            # Add collector types
            for col_type, name in col_types:
                try:
                    existing_col = session.query(cmp.Collector).filter(cmp.Collector.name == name).one()
                    col_type.id = existing_col.id
                    print(f'overwriting {name}')
                    session.merge(col_type)
                except sqlalchemy.exc.NoResultFound:
                    print(f'adding {col_type.name}')
                    session.add(col_type)

            # Add fluids
            for fluid, name in fluid_defs:
                try:
                    existing_fluid = session.query(cmp.FluidDefinition).filter(cmp.FluidDefinition.name == name).one()
                    fluid.id = existing_fluid.id
                    print(f'overwriting {name}')
                    session.merge(fluid)
                except sqlalchemy.exc.NoResultFound:
                    print(f'adding {name}')
                    session.add(fluid)

        session.commit()
        session.expunge_all()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if os.environ.get('HIT_DB_TYPE', 'postgresql') == 'sqlite':
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


if __name__ == '__main__':
    init_db()
