# from io import BytesIO
# import sys, os
# import psycopg2
# from psycopg2 import OperationalError, sql
# import psycopg2.extras as extras
# import pandas as pd
# import time
# import datetime
# from sqlalchemy import text, MetaData, Table, Column, Boolean, String, Float, DateTime, inspect
#
# from sunpeek.common.utils import sp_logger
# from sunpeek.db_utils import DATETIME_COL_NAME
#
#
# # default page size for database execute - this can be very large which should improve performance
# DEFAULT_PAGE_SIZE = 100000
#
#
# def show_psycopg2_exception(err):
#     """Prints errors ocurred during postgresql db interactions.
#
#     Parameters
#     ----------
#     err
#         Error catched in program execution regarding PostgreSQL operations.
#
#     Notes
#     -----
#     This code is part of the article by Learner CARES in
#     https://medium.com/analytics-vidhya/part-4-pandas-dataframe-to-postgresql-using-python-8ffdb0323c09
#     Used for debugging and logging purposes.
#
#     """
#     # get details about the exception
#     err_type, err_obj, traceback = sys.exc_info()
#     # get the line number when exception occured
#     line_n = traceback.tb_lineno
#     sp_logger.error(f"\n[psycopg2_exception] ERROR: {err} on line number: {line_n}")
#     sp_logger.error(f"[psycopg2_exception] traceback: {traceback} -- type: {err_type}")
#     sp_logger.error(f"\n[psycopg2_exception] extensions.Diagnostics: {err.diag}")
#     sp_logger.error(f"[psycopg2_exception] pgerror: {err.pgerror}")
#     sp_logger.error(f"[psycopg2_exception] pgcode: {err.pgcode} \n")
#
#
# # connection methods
#
#
# def get_db_connection_dict():
#     try:
#         port = os.environ.get('HIT_DB_HOST', 'localhost:5432').split(':')[1]
#     except IndexError:
#         port = 5432
#
#     conn_params_dict = {
#         "host": os.environ.get('HIT_DB_HOST', 'localhost:5432').split(':')[0],
#         "port": port,
#         "database": os.environ.get('HIT_DB_NAME', 'harvestit'),
#         "user": os.environ.get('HIT_DB_USER'),
#         "password": os.environ.get('HIT_DB_PW')
#     }
#
#     return conn_params_dict
#
#
# def get_db_connection():
#     """Init db connections
#     """
#     db_connection = connect(get_db_connection_dict())
#     if db_connection is None:
#         raise ConnectionError('Failed to connect to to database')
#     return db_connection
#
#
# def connect(conn_params_dict):
#     """Connects to an specific database.
#
#     Parameters
#     ----------
#     conn_params_dict : `dict`
#         A dictionary containing the user credentials for the conection,
#         the host and the name of the desired database.
#
#     Returns
#     -------
#     connection : `psycopg2_connection`
#         Established connection object to database.
#     """
#
#     try:
#         sp_logger.info('[connect] Connecting to the PostgreSQL...........')
#         connection = psycopg2.connect(**conn_params_dict)
#         sp_logger.info("[connect] Connected !")
#
#     except OperationalError as err:
#         sp_logger.exception(err)
#         # passing exception to function
#         show_psycopg2_exception(err)
#         # set the connection to 'None' in case of error
#         connection = None
#     return connection
#
#
# def disconnect_db(connection):
#     """Closes the connection with database.
#
#     Parameters
#     ----------
#     connection : `psycopg2_connection`
#         Connection object to database.
#     """
#     connection.close()
#     sp_logger.info("[disconnect_db] HIT DB connection closed!")
#
#
# # util methods
# def db_table_exists(engine, table_name):
#     """
#     Checks the existence of the provided table in the database. Used for initialization of dynamic table creation.
#
#     Parameters
#     ----------
#     engine : `sqlalchemy engine object`
#         Connection object to database.
#
#     table_name : `str`
#         Table name to check for.
#
#     Returns
#     -------
#     True/False : `bool`
#         True if table exists in database, False otherwise.
#     """
#
#     insp = inspect(engine)
#     return insp.has_table(table_name)
#
#
# def get_sensor_data(connection, sensor_names, table_name, start_timestamp, end_timestamp=None):
#     """Retrieves the data from a sensor in the specified table. It can return both a single value or a range depending on the timestamps provided.
#
#     Parameters
#     ----------
#     connection : `psycopg2_connection`
#         Connection object to database.
#
#     sensor_names : `str`, `list`
#         Name of the sensor(s) to retrieve the data.
#
#     table_name : `str`
#         Name of the table where the sensor data is stored.
#
#     start_timestamp,`datetime.datetime` or `str`
#         Timestamp of the data entry.
#
#     end_timestamp, optional `datetime.datetime` or `str`, optional
#         Timestamp to retrieve a range of values if provided.
#
#     """
#
#     sp_logger.debug(f"[get_sensor_data] Getting data for sensor \"{sensor_names}\" in \"{table_name}\" table")
#
#     # SQL query to execute
#     if isinstance(sensor_names, str):
#         sensor_names = [sensor_names]
#
#     fields = [sql.Identifier(col.lower()) for col in sensor_names]
#     fields = [sql.Identifier(DATETIME_COL_NAME)] + fields
#
#     if end_timestamp:
#         sql_object = sql.SQL(
#             """SELECT {fields} FROM {tb_name} WHERE {col_name} BETWEEN {start_tmstmp} AND {end_tmstmp} ORDER BY {order_col_name} ASC"""
#         ).format(
#             fields=sql.SQL(',').join(fields),
#             tb_name=sql.Identifier(table_name),
#             col_name=sql.Identifier(DATETIME_COL_NAME),
#             start_tmstmp=sql.Literal(start_timestamp),
#             end_tmstmp=sql.Literal(end_timestamp),
#             order_col_name=sql.Identifier(DATETIME_COL_NAME)
#         )
#     else:
#         # query for queh just start timestamp is supplied
#         sql_object = sql.SQL(
#             """SELECT {fields} FROM {tb_name} WHERE {col_name} = {start_tmstmp} ORDER BY {order_col_name} ASC"""
#         ).format(
#             fields=sql.SQL(',').join([
#                 sql.Identifier(DATETIME_COL_NAME),
#                 sql.Identifier(sensor_names),
#             ]),
#             tb_name=sql.Identifier(table_name),
#             col_name=sql.Identifier(DATETIME_COL_NAME),
#             start_tmstmp=sql.Literal(start_timestamp),
#             order_col_name=sql.Identifier(DATETIME_COL_NAME)
#         )
#
#     cursor = connection.cursor()
#     try:
#         t_start = time.time()
#         cursor.execute(sql_object)
#         query_data = cursor.fetchall()
#         sp_logger.debug(f"[get_sensor_data] Data retrieved in {time.time() - t_start}")
#
#         sensor_data = pd.DataFrame(list(query_data), columns=[DATETIME_COL_NAME]+sensor_names)
#         sensor_data = sensor_data.set_index(DATETIME_COL_NAME, drop=True)
#
#         # close the cursor object to prevent memory leaks
#         cursor.close()
#         return sensor_data
#
#     except (Exception, psycopg2.DatabaseError) as err:
#         sp_logger.error("[get_sensor_data] Error in get_sensor_data()")
#         # pass exception to function
#         if isinstance(err, (psycopg2.DatabaseError, OperationalError)):
#             show_psycopg2_exception(err)
#         cursor.close()
#
#
# def update_virtual_sensor_data(connection,
#                                sensor_data: pd.Series,
#                                table,
#                                # plant_name: str,
#                                # sensor_raw_name: str,
#                                page_size=DEFAULT_PAGE_SIZE):
#
#     """Saves the re calculated data of a virtual sensor in the corresponsing raw_table.
#
#     Is different from execute_batch() in that it does not batch-erase overlapping data
#
#     """
#
#     sp_logger.debug(f"[update_virtual_sensor_data] Inserting data into \"{table}\" table")
#
#     fld_name = sensor_data.name
#
#     df = sensor_data.to_frame()
#     df = df.rename_axis(DATETIME_COL_NAME).reset_index()
#     df = df.reindex(columns=df.columns[::-1])
#     tpls = df.to_records(index=False).tolist()
#     print(tpls[0])
#     sp_logger.debug(f"[execute_batch] Tuple to save example:\n{tpls[0]}")
#
#     # original
#     insert_str = sql.SQL("UPDATE {} SET {} = {} WHERE {} = {}").format(
#         sql.Identifier(table),
#         sql.Identifier(fld_name),
#         sql.Placeholder(),
#         sql.Identifier(DATETIME_COL_NAME),
#         sql.Placeholder()
#     )
#     # insert_str = sql.SQL("UPDATE {} SET {} = {} WHERE {} = {}").format(
#     #     sql.Identifier(table),
#     #     sql.Identifier(sensor_data.columns[1]),
#     #     sql.Placeholder(sensor_data.iloc[:,1]),
#     #     sql.Identifier("ds"),
#     #     sql.Placeholder(sensor_data.iloc[:,0])
#     # )
#     # https://stackoverflow.com/questions/60845779/psycopg2-how-to-insert-and-update-on-conflict-using-psycopg2-with-python
#     # insert_sql = '''
#     #     INSERT INTO tablename (col1, col2, col3, col4)
#     #     VALUES (%s, %s, %s, %s)
#     #     ON CONFLICT (col1) DO UPDATE SET
#     #     (col2, col3, col4) = (EXCLUDED.col2, EXCLUDED.col3, EXCLUDED.col4);
#     # '''
#
#     cursor = connection.cursor()
#
#     # cursor.rowcount
#     # cursor.execute("""
#     #     UPDATE table_name
#     #     SET z = codelist.z
#     #     FROM codelist
#     #     WHERE codelist.id = vehicle.id;
#     #     """)
#     # cursor.rowcount
#
#     try:
#         extras.execute_batch(cursor, insert_str, tpls, page_size=page_size)
#         # perhaps: cursor.execute(insert_str, tpls)
#         sp_logger.debug("[save_virtual_sensor_data] Virtual sensor data inserted successfully!")
#         connection.commit()
#         return True
#     except (Exception, psycopg2.DatabaseError, OperationalError) as err:
#         sp_logger.error(f"[save_virtual_sensor_data] Error in save_virtual_sensor_data()")
#         sp_logger.exception(err)
#         # pass exception to function
#         if isinstance(err, (psycopg2.DatabaseError, OperationalError)):
#             show_psycopg2_exception(err)
#         cursor.close()
#         connection.rollback()
#         return False
#
#
# def create_table_dynamic(session, table_name, types_dict):
#     """
#     Creates a table dynamically based on the keys and datatypes from the provided dictionary
#
#     Params
#     ------
#     `sqlalchemy engine object` engine: An sqlalchemy engine object used to connect to the database.
#     `str` table_name: A string to name the db table.
#     `dict` data_dict: Dictionary in the form {<name>: <python datatype>} for all columns to be created.
#     """
#
#     sp_logger.info(f"[create_table_dynamic] Creating table {table_name} dynamically...")
#
#     db_types = {bool: Boolean,
#                 float: Float,
#                 str: String,
#                 datetime.datetime: DateTime(timezone=True)}
#
#     metadata_obj = MetaData()
#
#     table = Table(table_name, metadata_obj)
#     table.append_column(Column(DATETIME_COL_NAME, db_types[datetime.datetime]))
#
#     for key, value in types_dict.items():
#         db_key = key.strip().lower()
#         table.append_column(Column(db_key, db_types[value]))
#
#     try:
#         table.create(session.get_bind())
#
#         # mk_hypertable_query = sql.SQL("SELECT create_hypertable({}, {}, chunk_time_interval => INTERVAL '1 month');"
#         #                               "CREATE INDEX ix_time ON {tn} ({ds} DESC);")\
#         #     .format(
#         #         sql.Placeholder(),
#         #         sql.Placeholder(),
#         #         tn = sql.Identifier(table_name),
#         #         ds = sql.Identifier(DATETIME_COL_NAME)
#         #     )
#
#         mk_hypertable_query = sql.SQL("CREATE INDEX ix_time ON {tn} ({ds} DESC);").format(
#                 tn = sql.Identifier(table_name),
#                 ds = sql.Identifier(DATETIME_COL_NAME)
#         )
#
#         con = session.get_bind().raw_connection()
#         con.cursor().execute(mk_hypertable_query, (table_name, DATETIME_COL_NAME))
#         con.commit()
#         sp_logger.debug(f"[CTD] Table {table_name} created!")
#
#     except OperationalError as err:
#         # pass exception to function
#         session.rollback()
#         show_psycopg2_exception(err)
#         raise
#
#
# def create_new_data_cols(engine, table_name, types_dict):
#     """
#     Compares a dictionary of column names against the columns already in the table called table_name, and creates any
#     columns that are in the dictionary but not the table, using datatypes compatible with the python types provided.
#     Parameters
#     ----------
#     `sqlalchemy engine object` engine:
#         An sqlalchemy engine object used to connect to the database.
#     `str` table_name: A string to name the db table.
#     `dict` data_dict: Dictionary in the form {<name>: <python datatype>} for new columns to be created. Existing columns
#       can be included, they will be ignored.
#     """
#     db_types = {bool: 'boolean',
#                 float: 'double precision',
#                 str: 'VARCHAR',
#                 datetime.datetime: 'timestamp with time zone'}
#
#     metadata_obj = MetaData()
#     raw_table = Table(table_name, metadata_obj, autoload_with=engine)
#     new_cols = set([key.lower() for key in types_dict.keys()]) - set([col.name for col in raw_table.columns])
#
#     for key in new_cols:
#         db_key = key.strip().lower()
#         stmt = sql.SQL('ALTER TABLE {0} ADD COLUMN {1} {2}').format(sql.Identifier(raw_table.name),
#                                                                     sql.Identifier(db_key),
#                                                                     sql.SQL(db_types[types_dict[key]]))
#         with engine.connect() as connection:
#             connection.execute(stmt.as_string(engine.raw_connection().connection))
#
#
# def delete_overlapping_data(connection, table_name, overlapping_boundaries):
#     """
#     Deletes all the entries in the DB in case there is overlapping with the incoming data.
#
#     Returns
#     -------
#     overlapping : Bool
#         Either overlapping entries were deleted in the db or not.
#     """
#
#     # overlaping handling
#     # 1. Run delete command on database for entries inside the overlapping range
#     # 2. This returns the number of rows affected, 0 if no entries are inside the range
#     # 3. Return a boolean value reporting if the overlapping delete was carried out.
#
#     overlapping = False
#     left_boundary, right_boundary = overlapping_boundaries
#
#     cursor = connection.cursor()
#     rows_deleted = 0
#     try:
#
#         delete_str = sql.SQL("DELETE FROM {} WHERE {} BETWEEN {} AND {}").format(
#             sql.Identifier(table_name),
#             sql.Identifier(DATETIME_COL_NAME),
#             sql.Literal(left_boundary),
#             sql.Literal(right_boundary)
#         )
#
#         cursor.execute(delete_str)
#         rows_deleted = cursor.rowcount
#
#         if rows_deleted > 0:
#             sp_logger.warning(
#                 f"[delete_overlapping_data] Overlapping detected! Deleting data between the range [{left_boundary}, {right_boundary}] in the {table_name} table")
#             sp_logger.warning(f"[delete_overlapping_data] Deleted overlapping entries: {rows_deleted}")
#             overlapping = True
#             return overlapping
#         else:
#             sp_logger.debug(f"[delete_overlapping_data] The incoming data does not overlap with records in the db.")
#             return overlapping
#
#     except (Exception, psycopg2.DatabaseError, OperationalError) as err:
#         sp_logger.exception(err)
#         # pass exception to function
#         if isinstance(err, (psycopg2.DatabaseError, OperationalError)):
#             show_psycopg2_exception(err)
#         cursor.close()
#         connection.rollback()
#         return False
#
#
# def df_to_db(connection, datafrm, table):
#     cursor = connection.cursor()
#     try:
#         fio = BytesIO()
#         datafrm.to_csv(fio, sep=';', header=False)
#         fio.seek(0)
#         # Use psychopg2 cursor.copy_from method to send data from CSV buffer and perform copy database side.
#         cursor.copy_from(fio, table, sep=';', null='', columns=[datafrm.index.name]+[col.lower() for col in datafrm.columns])
#         cursor.close()
#         return True
#     except Exception as ex:
#         sp_logger.error(ex)
#         cursor.close()
#         return False
