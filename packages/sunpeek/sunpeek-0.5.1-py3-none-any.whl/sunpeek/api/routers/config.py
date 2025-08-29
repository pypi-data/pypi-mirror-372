from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from typing import List
import enum
from sqlalchemy.orm import Session

import sunpeek.components as cmp
from sunpeek.api.dependencies import session, crud
import sunpeek.serializable_models as smodels
from sunpeek.common.errors import ConfigurationError
import sunpeek.components.sensor_types as st
from sunpeek.api.routers.helper import update_obj, update_plant
from sunpeek.components.types import CollectorTestTypes

config_router = APIRouter(
    prefix="/config",
    tags=["config"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@config_router.get("/ping")
def ping_harvestIT_old():
    """old version for backward compatibility"""
    return "success"


@config_router.get("/ping_backend")
def ping_harvestIT():
    return "success"


@config_router.get("/ping_database")
def ping_database(sess: Session = Depends(session)):
    sess.execute('SELECT 1')
    return True


# @config_router.post("/sensors", response_model=Union[smodels.Sensor, List[smodels.Sensor]], tags=["sensors"],
#                     responses= {409: {"description": "Conflict, most likely because the plant name or name of a child object already exists",
#                     "model": smodels.Error}}))
# def sensors(id: int = None, raw_name: str=None, plant_id: int = None, plant_name: str = None,
#             sess: Session = Depends(session), crud = Depends(crud)):
#     sensors = crud.get_sensors(sess, id, raw_name, plant_id, plant_name)
#     return sensors


@config_router.get("/sensor_types",
                   response_model=smodels.SensorTypeValidator | List[smodels.SensorTypeValidator],
                   tags=["sensors"], summary="Get a list of sensor types, or select by id or name and plant")
def sensor_types(name: str = None):
    if name is not None:
        return getattr(st, name)
    return st.all_sensor_types


@config_router.get("/fluid_definitions",
                   response_model=List[smodels.FluidDefinition] | smodels.FluidDefinition,
                   tags=["fluids"], summary="Get a single list of fluid_definitions, or select by id or name and plant")
def fluids(id: int = None,
           name: str = None,
           plant_id: int = None,
           plant_name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_components(sess, cmp.FluidDefinition, id, name, plant_id, plant_name)


@config_router.get("/fluid_definitions/{id}", response_model=smodels.FluidDefinition, tags=["fluids"],
                   summary="Get a single fluid definition by id")
def fluids(id: int = None,
           name: str = None,
           plant_id: int = None,
           plant_name: str = None,
           sess: Session = Depends(session),
           crd=Depends(crud)):
    return crd.get_components(sess, cmp.FluidDefinition, id, name, plant_id, plant_name)


@config_router.get("/collectors",
                   response_model=List[smodels.Collector] | smodels.Collector,
                   tags=["collectors"],
                   summary="Get a list of collectors, or select by id or name, or filter by collectors used "
                           "in a specific plant.")
def collectors(id: int = None,
               name: str = None,
               plant_id: int = None,
               plant_name: str = None,
               sess: Session = Depends(session),
               crd=Depends(crud)):
    if plant_id is not None or plant_name is not None:
        plant = crd.get_plants(sess, plant_id, plant_name)
        return [array.collector for array in plant.arrays]

    return crd.get_components(sess, cmp.Collector, id, name)


@config_router.post("/collectors/new",
                    response_model=smodels.Collector | List[smodels.Collector],
                    tags=["collectors"],
                    status_code=201,
                    summary="Create a new collector or collectors")
def create_collector(collector:
smodels.CollectorSST | smodels.CollectorQDT | List[smodels.CollectorSST] | List[smodels.CollectorQDT],
                     sess: Session = Depends(session),
                     crd=Depends(crud)):
    collectors_ = collector if isinstance(collector, list) else [collector]

    for i, collector in enumerate(collectors_):
        coll_dict = collector.dict(exclude_unset=True)
        test_type = coll_dict.pop('test_type')

        if test_type == CollectorTestTypes.SST.value:
            coll = cmp.CollectorSST(**coll_dict)
        elif test_type == CollectorTestTypes.QDT.value:
            coll = cmp.CollectorQDT(**coll_dict)
        else:
            raise ConfigurationError(f'Collector test_type must be one of {", ".join(CollectorTestTypes)}.')

        collectors_[i] = crd.create_component(sess, coll)
    sess.commit()

    return collectors_


@config_router.get("/collectors/{id}",
                   response_model=smodels.Collector,
                   tags=["collectors"],
                   summary="Get a single collector by id")
def get_collector(id: int,
                  sess: Session = Depends(session),
                  crd=Depends(crud)):
    return crd.get_components(sess, cmp.Collector, id=id)


@config_router.post("/collectors/{id}",
                    response_model=smodels.CollectorUpdate,
                    tags=["collectors"],
                    summary="Update a collector")
def update_collector(id: int,
                     collector_update: smodels.Collector,
                     sess: Session = Depends(session),
                     crd=Depends(crud)):
    collector = crd.get_components(sess, cmp.Collector, id=id)
    collector = update_obj(collector, collector_update)
    collector.update_parameters()

    all_arrays = crd.get_components(sess, cmp.Array)
    all_arrays = all_arrays if isinstance(all_arrays, list) else [all_arrays]
    unique_plants = {a.plant for a in all_arrays if a.collector == collector and a.plant is not None}

    for plant in unique_plants:
        plant = update_plant(plant)
        crd.update_component(sess, plant)

    return crd.update_component(sess, collector)


@config_router.delete("/collectors/{id}",
                      status_code=204,
                      tags=["collectors"],
                      summary="Delete a single collector by id")
def delete_collector(id: int,
                     sess: Session = Depends(session),
                     crd=Depends(crud)):
    collector = crd.get_components(sess, cmp.Collector, id=id)

    # Find out if collector is being used by any array
    all_arrays = crd.get_components(sess, cmp.Array)
    all_arrays = all_arrays if isinstance(all_arrays, list) else [all_arrays]
    arrays_using_collector = [a for a in all_arrays if a.collector == collector]
    if arrays_using_collector:
        plant_names = {a.plant.name for a in arrays_using_collector}
        return JSONResponse(
            status_code=409,
            content={'error': f'Cannot delete collector.',
                     'message': f'Cannot delete collector because it is configured to be used by arrays. '
                                f'Collector is used in {len(plant_names)} plants: {", ".join(plant_names)}'}
        )
    crd.delete_component(sess, collector)


@config_router.get("/sensor_slots",
                   response_model=List[smodels.SensorSlotValidator],
                   tags=["arrays", "plants", "sensor_slots"],
                   summary="Get a list of slot names to which sensors can be assigned for the given component type")
def slot_names(component_type: enum.Enum('cmp_types', {"Plant": "plant", "Array": "array"}),
               include_virtuals: bool = False):
    if include_virtuals:
        return cmp.__dict__[component_type.name].sensor_slots.values()
    else:
        return cmp.__dict__[component_type.name].get_real_slots()
