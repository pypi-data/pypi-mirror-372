from pydantic import BaseModel as PydanticBaseModel
from pydantic import validator
import pint
from typing import List
import numpy as np

class BaseModel(PydanticBaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        fields = {
            'class_': 'class'
        }

    @validator('*', pre=True)
    def make_strings(cls, v):
        if isinstance(v, pint.Unit):
            v = str(v)
            return v
        # elif isinstance(v, pint.Quantity):
        #     return str(v.units)
        # elif isinstance(v, cmp.Collector):
        #     return v.name
        return v

    @validator('units', 'native_unit', pre=True, check_fields=False)
    def validate_units(cls, v):
        if isinstance(v, pint.Quantity):
            return str(v.units)
        return v


def np_to_list(val):
    if isinstance(val, np.ndarray) and val.ndim == 1:
        return list(val)
    elif isinstance(val, np.ndarray) and val.ndim > 1:
        out = []
        for array in list(val):
            out.append(np_to_list(array))
        return out
    return val


class Quantity(BaseModel):
    magnitude: float | List[float] | List[List[float]]
    units: str

    @validator('magnitude', pre=True)
    def convert_numpy(cls, val):
        return np_to_list(val)

    @validator('units', pre=True)
    def pretty_unit(cls, val):
        if isinstance(val, pint.Unit):
            return f"{val:~P}"
        return val