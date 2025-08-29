from sunpeek.core_methods import virtuals
from sunpeek.components.physical import convert_to_concrete_components


def update_obj(obj, update_model):
    update_dict = update_model.dict(exclude_unset=True)

    for key, val in update_dict.items():
        if val != getattr(obj, key):
            setattr(obj, key, val)

    return obj


def update_plant(plant, update_model=None, session=None):
    """For a plant, update the plant including config-dependent virtual sensors state.

    Parameters
    ----------
    plant : A cmp.Plant instance
    update_model : updated component model

    Returns
    -------
    The updated plant.
    """
    if update_model is not None:
        update_obj(plant, update_model)

    if session is not None:
        convert_to_concrete_components(session, plant)
    virtuals.config_virtuals(plant)

    return plant


def recalculate_plant(plant, eval_start, eval_end):
    """For a plant, recalculate virtual sensors, set context and flush results to parquet.

    Parameters
    ----------
    plant : A cmp.Plant instance
    eval_start, eval_end : Recalculation can be limited to this interval. Can be datetime or None.

    Returns
    -------
    The updated plant.
    """
    plant.context.set_eval_interval(eval_start=eval_start, eval_end=eval_end)
    virtuals.calculate_virtuals(plant)
    plant.context.flush_virtuals_to_parquet()

    return plant
