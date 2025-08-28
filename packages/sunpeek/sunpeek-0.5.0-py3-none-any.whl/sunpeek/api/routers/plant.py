from typing import List
import datetime as dt
import pytz
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from fastapi.responses import JSONResponse, Response

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from sunpeek.api.dependencies import session, crud
import sunpeek.serializable_models as smodels
import sunpeek.demo.demo_plant as demo_plant_function
from sunpeek.api.routers.helper import update_obj, update_plant, recalculate_plant
from sunpeek.common import config_parser
import sunpeek.components as cmp
from sunpeek.common.errors import TimeZoneError
from sunpeek.data_handling.context import NanReportResponse
import sunpeek.exporter

plants_router = APIRouter(
    prefix="/plants",
    tags=["plants"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

plant_router = APIRouter(
    prefix="/plants/{plant_id}",
    tags=["plant"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

any_plant_router = APIRouter(
    prefix="/plants/-",
    tags=["plant"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@plants_router.get("",
                   summary="List all plants",
                   response_model=List[smodels.Plant])
def plants(name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_name=name)
    if not isinstance(plant, list):
        plant = [plant]

    return plant


@plants_router.get("/summary",
                   summary="Get a list of all plants, with only minimal information",
                   response_model=List[smodels.PlantSummary])
def plants(name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_plants(sess, plant_name=name)


@plant_router.get("/summary",
                  summary="Get a plant summary, with only minimal information",
                  response_model=smodels.PlantSummary)
def plants(plant_id: int = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_plants(sess, plant_id=plant_id)


@plants_router.post("/new",
                    summary="Create plants",
                    response_model=smodels.Plant,
                    status_code=201,
                    responses={409: {"description": "Conflict, most likely because the plant name or name of a child "
                                                    "object already exists",
                                     "model": smodels.Error}})
def create_plant(new_plant: smodels.NewPlant,
                 sess: Session = Depends(session),
                 crd=Depends(crud)):
    """ Create a new plant. `name`, `latitude`, `longitude` are required. sensors can be mapped by passing a list of sensor
    structures to `sensors`
    """
    plant = config_parser.make_full_plant(new_plant.dict(exclude_unset=True), sess)
    plant = crd.create_component(sess, plant)

    return plant


@plants_router.post("/import",
                    summary="Import a plant from JSON configuration, such as that "
                            "returned by `plants/{plant_id}/export_config`",
                    response_model=List[
                        smodels.Collector | smodels.SensorTypeValidator | smodels.FluidDefinition | smodels.Plant],
                    status_code=201,
                    responses={409: {"description": "Conflict, most likely because the plant name or name of a child "
                                                    "object already exists",
                                     "model": smodels.Error}},
                    tags=["plants", "export/import"])
def import_conf(import_config: smodels.ConfigImport,
                new_plant_name: str | None = None,
                sess: Session = Depends(session),
                crd=Depends(crud)):
    conf = import_config.plant.dict(exclude_unset=True)
    if new_plant_name is not None:
        conf['name'] = new_plant_name
    plant = config_parser.make_full_plant(conf, sess)
    # plant = config_parser.make_full_plant(import_config.plant.dict(exclude_unset=True), sess)

    imported_collectors = [cmp.Collector(**coll.dict(exclude_unset=True)) for coll in import_config.collectors]
    existing_collectors = [col[0] for col in crd.get_components(sess, cmp.Collector.name)]
    new_collectors = [col for col in imported_collectors if col.name not in existing_collectors]

    imported_fluids = [cmp.FluidDefinition(**fluid.dict(exclude_unset=True)) for fluid in
                       import_config.fluid_definitions]
    existing_fluids = [fluid[0] for fluid in crd.get_components(sess, cmp.FluidDefinition.name)]
    new_fluids = [fluid for fluid in imported_fluids if fluid.name not in existing_fluids]

    created = []
    for item in new_collectors + new_fluids:
        crd.get_components(sess, type(item), name=item.name)
        crd.create_component(sess, item, commit=False)
        created.append(item)

    plant = crd.create_component(sess, plant)

    return [plant] + created


@plants_router.get("/create_demo_plant",
                   response_model=smodels.Plant,
                   summary="Create demo plant config, optionally including data, if data is to be included, "
                           "accept_license must also be set to true")
def demo_plant(name: str = None,
               include_data: bool = False,
               accept_license: bool = False,
               sess: Session = Depends(session)):
    plant = demo_plant_function.create_demoplant(sess, name)
    if include_data and accept_license:
        demo_plant_function.add_demo_data(plant, sess)
    return plant


@plant_router.get("",
                  response_model=smodels.Plant,
                  summary="Get a single plant by id",
                  tags=["plants"])
def plants(plant_id: int,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id)

    return plant


@plant_router.get("/export_config",
                  response_model=smodels.ConfigExport,
                  summary="Export a plant configuration, optionally with data",
                  description="Export a plant with the sensor types, collector types, and fluid definitions it uses.",
                  tags=["plants", "export/import"])
def export_conf(plant_id: int,
                sess: Session = Depends(session),
                crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id=plant_id)

    return smodels.ConfigExport(**sunpeek.exporter.create_export_config(plant))


@plant_router.post("/export_complete",
                   response_model=smodels.JobReference,
                   summary="Export a plant with configuration and data",
                   description="""Create an export job for a complete plant with sensor types, collector types, 
                   fluid definitions, and data. When the job completes a tar package containing a json file, 
                   and data 1 CSV file per calender year, is available for download""",
                   tags=["plants", "export/import"],
                   status_code=202)
def create_complete_export(request: Request,
                           background_tasks: BackgroundTasks,
                           plant_id: int,
                           include_virtuals: bool = True,
                           sess: Session = Depends(session),
                           crd=Depends(crud),
                           ):
    plant = crd.get_plants(sess, plant_id=plant_id, load_sensors = True)
    job = cmp.Job(status=cmp.helpers.ResultStatus.pending, plant=plant)

    crd.create_component(sess, job)
    background_tasks.add_task(sunpeek.exporter.create_export_package, plant, include_virtuals, job)

    return smodels.JobReference(job_id=job.id, href=str(request.url_for('jobs')) + str(job.id))


@plant_router.post("",
                   response_model=smodels.Plant | List[smodels.Plant],
                   summary="Update a plant",
                   responses={409: {"description": "Conflict, most likely because the plant name or name of a child "
                                                   "object already exists",
                                    "model": smodels.Error}})
def plants(plant_id: int,
           plant_update: smodels.UpdatePlant,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id=plant_id)
    plant = update_plant(plant, plant_update, sess)
    return crd.update_component(sess, plant)


@plant_router.post("/summary",
                   response_model=smodels.PlantSummary | List[smodels.PlantSummary],
                   summary="Update a plant",
                   responses={409: {"description": "Conflict, most likely because the plant name or name of a child "
                                                   "object already exists",
                                    "model": smodels.Error}})
def plants(plant_id: int,
           plant_update: smodels.PlantSummaryBase,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id=plant_id)
    # This is necessary because a change in a PlantSummaryBase may involve changes to latitude, longitude etc.
    # which are used by virtual sensors / solar position etc.
    plant = update_plant(plant, plant_update)

    return crd.update_component(sess, plant)


@plant_router.delete("",
                     summary="Delete a plant by id")
def plants(plant_id: int,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    # Delete parquet data folders, and delete plant from database
    plant = crd.get_plants(sess, plant_id=plant_id)
    plant.delete_all_data()
    plant_name = plant.name
    sess.delete(plant)
    sess.commit()

    return str(f'plant {plant_name} was deleted')


@plant_router.get("/data_start_end",
                  response_model=smodels.PlantDataStartEnd,
                  summary="Get timestamps when data associated with the plant start and end.",
                  tags=["interval", "data"])
def data_start_end(plant_id: int,
                   sess: Session = Depends(session), crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id=plant_id)

    start_end = plant.context.get_data_start_end()
    start, end = start_end if start_end is not None else (None, None)
    return smodels.PlantDataStartEnd(start=start, end=end)


@plant_router.get("/sensors/nan_report",
                  summary="Triggers calculation of the daily-summarized NaN report for all sensors.",
                  tags=["sensors", "data"])
def nan_report(plant_id: int,
               eval_start: dt.datetime | None = None,
               eval_end: dt.datetime | None = None,
               sess: Session = Depends(session), crd=Depends(crud)) -> NanReportResponse:
    plant = crd.get_plants(sess, plant_id=plant_id)
    plant.context.set_eval_interval(eval_start=eval_start, eval_end=eval_end)

    return plant.context.get_nan_report(include_virtuals=True)


@plant_router.get("/sensors/recalculate_virtuals",
                  summary="Triggers the recalculation of all virtual sensors of that plant",
                  tags=["sensors, virtual"])
def recalculate_virtuals(plant_id: int,
                         eval_start: dt.datetime | None = None,
                         eval_end: dt.datetime | None = None,
                         sess: Session = Depends(session),
                         crd=Depends(crud),
                         ):
    plant = crd.get_plants(sess, plant_id=plant_id)
    recalculate_plant(plant, eval_start, eval_end)
    sess.commit()

    return JSONResponse(status_code=200,
                        content={"description": "Recalculation done!",
                                 "message": "Recalculation of virtual sensors successfully finished."})


@plant_router.get("/sensors",
                  response_model=List[smodels.Sensor] | smodels.Sensor,
                  tags=["sensors"],
                  summary="Get a list of sensors, or select by id or raw name")
@plant_router.get("/sensors/{id}",
                  response_model=smodels.Sensor,
                  tags=["sensors"],
                  summary="Get a single sensor by id")
@any_plant_router.get("/sensors/{id}",
                      response_model=smodels.Sensor,
                      tags=["sensors"],
                      summary="Get a single sensor by id")
def sensors(id: int = None,
            raw_name: str = None,
            plant_id: int | str = None,
            sess: Session = Depends(session),
            crd=Depends(crud)):
    plant_id = None if plant_id == '-' else plant_id
    sensor = crd.get_sensors(sess, id, raw_name, plant_id)

    return sensor


@plant_router.get("/sensors/{id}/data", tags=["sensors", "data"],
                  summary="Get measurement data of a single sensor by id")
@any_plant_router.get("/sensors/{id}/data", response_model=smodels.Sensor, tags=["sensors"],
                      summary="Get measurement data of a single sensor by id")
def sensor_data(id: int = None,
                plant_id: int | str = None,
                eval_start: dt.datetime | None = None,
                eval_end: dt.datetime | None = None,
                sess: Session = Depends(session),
                crd=Depends(crud)):
    plant_id = None if plant_id == '-' else plant_id
    plant = crd.get_plants(sess, plant_id=plant_id)
    plant.context.set_eval_interval(eval_start=eval_start, eval_end=eval_end)
    sensor = crd.get_sensors(sess, plant_id=plant_id, id=id)
    data = sensor.data
    df = data.astype(float)  # to_json does not work with dtype pint.

    return Response(df.to_json(), media_type="application/json")


@any_plant_router.post("/sensors",
                       response_model=List[smodels.Sensor],
                       summary="Batch update a list of sensors, each passed sensor object must contain an id",
                       tags=["sensors"])
def update_sensors(sensor_updates: List[smodels.BulkUpdateSensor],
                   sess: Session = Depends(session),
                   crd=Depends(crud)):
    return_sensors = []
    for sensor_update in sensor_updates:
        sensor = crd.get_sensors(sess, sensor_update.id)
        sensor = update_obj(sensor, sensor_update)
        crd.update_component(sess, sensor, commit=False)
        return_sensors.append(sensor)

    plant_ids = {s.plant.id for s in return_sensors if s.plant is not None}
    for plant_id in plant_ids:
        plant = crd.get_plants(sess, plant_id=plant_id)
        plant = update_plant(plant)
        crd.update_component(sess, plant, commit=False)

    sess.commit()

    return return_sensors


@any_plant_router.post("/sensors/{id}",
                       response_model=smodels.Sensor,
                       summary="Update a single sensor by id",
                       tags=["sensors"])
def update_sensor(id: int,
                  sensor_update: smodels.Sensor,
                  sess: Session = Depends(session),
                  crd=Depends(crud)):
    sensor = crd.get_sensors(sess, id)
    sensor = update_obj(sensor, sensor_update)
    sensor = crd.update_component(sess, sensor)

    if sensor.plant is not None:
        plant = update_plant(sensor.plant)
        crd.update_component(sess, plant, commit=True)

    return sensor


@plant_router.post("/sensors/new",
                   response_model=List[smodels.Sensor],
                   summary="Create a new `Sensor` object or objects",
                   tags=["sensors"],
                   status_code=201,
                   responses={
                       409: {
                           "description": "Conflict, most likely because the sensor raw name already exists in this plant",
                           "model": smodels.Error}})
def create_sensors(plant_id: int,
                   new_sensor: smodels.NewSensor | List[smodels.NewSensor],
                   sess: Session = Depends(session),
                   crd=Depends(crud)):
    """Create a new sensor or sensors. `raw_name` is required.
    To create multiple sensors at once, pass a list of sensor structures
    """
    sensor_list = new_sensor if isinstance(new_sensor, list) else [new_sensor]

    return_sensors = []
    plant = crd.get_plants(sess, plant_id=plant_id)
    for sensor in sensor_list:
        sensor = cmp.Sensor(**sensor.dict(), plant=plant)
        sensor = crd.create_component(sess, sensor, commit=False)
        return_sensors.append(sensor)
    sess.commit()

    return return_sensors


from fastapi import Query
from typing import Annotated


@plant_router.delete("/sensors", summary="Delete multiple sensors by id", tags=["sensors"])
def delete_sensors(ids: Annotated[list[str] | None, Query()] = None,
                   plant_id: int | str | None = None,
                   sess: Session = Depends(session),
                   crd=Depends(crud),
                   ):
    sensors_to_delete = sess.query(cmp.Sensor).filter(cmp.Sensor.id.in_(ids)).filter(
        cmp.Sensor.plant_id == plant_id).all()

    # For faster updates, disable synchronization with post_config_changed_callbacks
    # which would call updates for each sensor to be dropped
    plant = sess.query(cmp.Plant).get(plant_id)
    plant.defer_post_config_changed_actions = True

    # Delete sensors
    for sensor in sensors_to_delete:
        print(sensor.id)
        s = crd.get_sensors(sess, sensor.id)
        with sess.no_autoflush:
            s.remove_references()
        crd.delete_component(sess, sensor)

    # As the deletion is done now, we call the post_config_changed_callbacks and reset to the default
    plant.defer_post_config_changed_actions = False
    plant = update_plant(plant)
    crd.update_component(sess, plant, commit=True)


@any_plant_router.delete("/sensors/{id}",
                         summary="Delete a single sensor by id",
                         tags=["sensors"])
def delete_sensor(id: int,
                  sess: Session = Depends(session),
                  crd=Depends(crud),
                  ):
    sensor = crd.get_sensors(sess, id)
    sensor_plant = sensor.plant if sensor.plant is not None else None

    with sess.no_autoflush:
        sensor.remove_references()
    crd.delete_component(sess, sensor)

    if sensor_plant is not None:
        plant = update_plant(sensor_plant)
        crd.update_component(sess, plant, commit=False)

    sess.commit()


@plant_router.get("/arrays", response_model=List[smodels.Array] | smodels.Array,
                  tags=["arrays"],
                  summary="Get a list of arrays, or select by id or name and plant")
@any_plant_router.get("/arrays/{id}", response_model=smodels.Array, tags=["arrays"],
                      summary="Get a single array by id")
def arrays(id: int = None,
           name: str = None,
           plant_id: int | str = None,
           plant_name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    plant_id = None if plant_id == '-' else plant_id

    return crd.get_components(sess, cmp.Array, id, name, plant_id, plant_name)


@any_plant_router.post("/arrays/{id}", response_model=smodels.Array,
                       tags=["arrays"],
                       summary="Update an array by id")
def update_array(id: int,
                 array_update: smodels.ArrayUpdate,
                 sess: Session = Depends(session),
                 crd=Depends(crud)):
    array = crd.get_components(sess, component=cmp.Array, id=id)
    array = update_obj(array, array_update)

    # This update needed: New arrays might for example trigger new plant.tp value if sum of array.tp powers.
    if array.plant is not None:
        plant = update_plant(array.plant)
        crd.update_component(sess, plant)

    return crd.update_component(sess, array)


@any_plant_router.delete("/arrays/{id}", tags=["arrays"],
                         summary="Delete an array by id")
def arrays(id: int,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    array = crd.get_components(sess, component=cmp.Array, id=id)
    if array.plant is not None:
        array.plant.arrays.pop(array.plant.arrays.index(array))
    sess.delete(array)
    sess.commit()


@plant_router.post("/arrays/new",
                   response_model=List[smodels.Array] | smodels.Array,
                   tags=["arrays"], status_code=201,
                   summary="Get a list of arrays, or select by id or name and plant",
                   responses={
                       409: {"description": "Conflict, most likely because the array name or a child object already "
                                            "exists in this plant", "model": smodels.Error}}
                   )
def create_array(new_array: smodels.NewArray,
                 plant_id: int,
                 sess: Session = Depends(session),
                 crd=Depends(crud)):
    """Create a new array or arrays. `name` and `collector` are required.
    To create multiple arrays at once, pass a list of array structures.
    sensors can be mapped by passing a dict of sensor structures to `sensors` (**NOTE** not actually tested, may not work yet.
    """
    array_list = new_array if isinstance(new_array, list) else [new_array]

    return_arrays = []
    for array in array_list:
        plant = crd.get_plants(sess, plant_id)
        array = cmp.Array(**array.dict(exclude_unset=True), plant=plant)
        array = crd.create_component(sess, array)
        return_arrays.append(array)

    return return_arrays


@plant_router.get("/fluids",
                  response_model=List[smodels.Fluid] | smodels.Fluid,
                  summary="Get a list of fluids, or select by name",
                  tags=["fluids"])
def fluids(id: int = None,
           name: str = None,
           plant_id: int = None,
           plant_name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_components(sess, cmp.Fluid, id, name, plant_id, plant_name)


@plant_router.get("/fluids/{id}", response_model=smodels.Fluid,
                  summary="Get a single fluid by id",
                  tags=["fluids"])
def fluids(id: int,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_components(sess, cmp.Fluid, id=id)


@plant_router.get("/operational_events",
                  response_model=smodels.OperationalEvent | List[smodels.OperationalEvent],
                  summary="Get a list of operational_events for a plant, or select by date range, or id",
                  tags=["operational events"])
def get_operational_events(plant_id: int,
                           id: int = None,
                           search_start: dt.datetime = None,
                           search_end: dt.datetime = None,
                           search_timezone: str = None,
                           sess: Session = Depends(session),
                           crd=Depends(crud)):
    if ((search_start is not None) or (search_end is not None)) and (search_timezone is None):
        raise TimeZoneError(
            'The parameter "timezone" must be specified to interpret search start and search end timestamps correctly.')
    if search_start is not None:
        search_start = pytz.timezone(search_timezone).localize(search_start)
        search_start = pytz.timezone('UTC').normalize(search_start)
    if search_end is not None:
        search_end = pytz.timezone(search_timezone).localize(search_end)
        search_end = pytz.timezone('UTC').normalize(search_end)

    return crd.get_operational_events(sess, id, plant_id, search_start=search_start, search_end=search_end)


@any_plant_router.get("/operational_events/{id}",
                      response_model=smodels.OperationalEvent,
                      summary="an operational event by id",
                      tags=["operational events"])
def get_operational_event(id: int = None,
                          sess: Session = Depends(session),
                          crd=Depends(crud)):
    return crd.get_operational_events(sess, id)


@plant_router.post("/operational_events",
                   response_model=smodels.OperationalEvent,
                   summary="Create an operational event",
                   tags=["operational events"])
def create_operational_event(plant_id: int,
                             event_start: dt.datetime,
                             timezone: str,
                             event_end: dt.datetime = None,
                             description: str = None,
                             ignored_range: bool = False,
                             sess: Session = Depends(session),
                             crd=Depends(crud)):
    plant = crd.get_plants(sess, plant_id)
    event = cmp.OperationalEvent(plant, event_start, tz=timezone, event_end=event_end, description=description,
                                 ignored_range=ignored_range)

    return crd.create_component(sess, event)


@any_plant_router.delete("/operational_events/{id}",
                         summary="Delete an operational event by id",
                         tags=["operational events"])
def delete_operational_event(id: int,
                             sess: Session = Depends(session),
                             crd=Depends(crud)):
    event = crd.get_operational_events(sess, id)
    crd.delete_component(sess, event)
