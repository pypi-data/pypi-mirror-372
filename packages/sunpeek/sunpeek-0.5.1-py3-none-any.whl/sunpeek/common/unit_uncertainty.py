"""
Collection of utility functions for handling unit and uncertainty within HarvestIT.
"""

import numpy as np
import pandas as pd
import pint
import pint_pandas
# from uncertainties import unumpy
from metpy.units import units
import warnings
import functools
import re
from typing import Union

from sunpeek.common.errors import ConfigurationError

# def create_unit_registry():
#     """
#     Creates pint Unit registry for HarvestIT.
#
#     Returns
#     -------
#     units : `pint.registry.UnitRegistry`
#         pint unit registry with some special tweaks.
#
#     Notes
#     -----
#     Taken from metpy.units to avoid dependency on metpy
#
#     Examples
#     --------
#     # >>> from common import unit_uncertainty as uu
#     # >>> units = uu.create_unit_registry()
#     # >>> units = uu.units
#     # >>> Q = uu.Q
#     """
#
#     units = pint.UnitRegistry(
#         autoconvert_offset_to_baseunit=True,
#         preprocessors=[
#             functools.partial(
#                 re.sub,
#                 r'(?<=[A-Za-z])(?![A-Za-z])(?<![0-9\-][eE])(?<![0-9\-])(?=[0-9\-])',
#                 '**'
#             ),
#             lambda string: string.replace('%', 'percent')
#         ]
#     )
#     # Capture v0.10 NEP 18 warning on first creation
#     with warnings.catch_warnings():
#         warnings.simplefilter('ignore')
#         units.Quantity([])
#
#     # For pint 0.6, this is the best way to define a dimensionless unit. See pint #185
#     units.define(pint.unit.UnitDefinition('percent', '%', (),
#                                           pint.converters.ScaleConverter(0.01)))
#
#     # Define commonly encountered units not defined by pint
#     units.define('degrees_north = degree = degrees_N = degreesN = degree_north = degree_N '
#                  '= degreeN')
#     units.define('degrees_east = degree = degrees_E = degreesE = degree_east = degree_E = degreeE')
#
#     # Alias geopotential meters (gpm) to just meters
#     units.define('@alias meter = gpm')
#
#     # Silence UnitStrippedWarning
#     if hasattr(pint, 'UnitStrippedWarning'):
#         warnings.simplefilter('ignore', category=pint.UnitStrippedWarning)
#
#     return units


# units = create_unit_registry()
pint_pandas.PintType.ureg = units
Q = units.Quantity


# def get_unit_string(s):
#     """Returns unit of a pint unit-aware pd.Series as a string.
#     """
#     return s.pint.units.__str__()


def to_s(num_arr_or_q, unit_str=''):
    """Return the input numeric array converted to pd.Series with dtype pint[unit_str]. No index."""
    if isinstance(num_arr_or_q, pint.Quantity):
        q = num_arr_or_q.to(unit_str)
        num_arr_or_q = q.m
        unit_str = q.units.__str__()
    if unit_str == '':
        unit_str = 'dimensionless'
    return pd.Series(num_arr_or_q).astype(f'pint[{unit_str}]')


def to_numpy(s, unit_str=''):
    """Return the unit-aware pd.Series `s` to a numpy array after converting it to unit_str."""
    if isinstance(s, pint.Quantity):
        s = to_s(s, unit_str)
    return s.pint.to(unit_str).astype(float).to_numpy()


# def copy_unit(copy_from, copy_to):
#     """Copies dtype pint unit from pd.Series `in1` and assigns it to s2 as .astype(pint[unit]).
#     Same for DataFrame, applies to each column then. Both inputs have to be either Series or DataFrames.
#     If inputs are DataFrames, it assumes all columns in in2 are found in in1.
#     Parameters
#     ----------
#     copy_from : pd.Series or pd.DataFrame
#     copy_to : pd.Series or pd.DataFrame
#     Returns
#     -------
#     pd.Series or pd.DataFrame
#         Output pd.Series or pd.DataFrame, depending on input types, with unit attached to it as dtype.
#     """
#     if isinstance(copy_from, pd.Series) and isinstance(copy_to, pd.Series):
#         return to_s(copy_to, get_unit_string(copy_from))
#     elif isinstance(copy_from, pd.DataFrame) and isinstance(copy_to, pd.DataFrame):
#         if not all([col in copy_from.columns for col in copy_to.columns]):
#             raise AttributeError('Columns not found in DataFrame from which dtype is to be copied.')
#         # dtypes = copy_from.dtypes.to_dict()
#         # copy_to.astype()
#         for col in copy_from.columns:
#             copy_to[col] = copy_unit(copy_from[col], copy_to[col])
#         return copy_to
#     else:
#         raise TypeError('Both inputs expected to be of same type, either pandas Series or DataFrames.')


def assert_compatible(uQ1, uQ2):
    """Asserts if 2 unit strings and/or pint Quantities are compatible in units.

    Parameters
    ----------
    uQ1 : str or pint.Quantity
    uQ2 : str or pint.Quantity
    """
    if isinstance(uQ1, str):
        uQ1 = Q(1, uQ1)
    if isinstance(uQ2, str):
        uQ2 = Q(1, uQ2)
    assert uQ1.is_compatible_with(uQ2)


def to_pint(s, unit=None, absolute_uncertainty=None, relative_uncertainty=None,
            relative_unit=None, use_relative_abs=True):   # pragma: no cover
    """
    Converts pandas Series `s` to a pint Quantity object, holding unit and uncertainty.

    Parameters
    ----------
    s : pd.Series
        Data series to convert.

    unit : `string`, optional
        Unit string to be used as units(unit). If not provided or None, unit will be dimensionless.

    absolute_uncertainty : `pint.quantity.Quantity`, optional
        pint Quantity object. Must be compatible with unit.

    relative_uncertainty : `float` or `pint.quantity.Quantity`, optional
        Float (e.g. 0.1) or dimensionless pint Quantity object (e.g. Quantity(10, 'percent').

    relative_unit : `string`, optional
        Unit string to be used for calculating relative uncertainty. Only required for things involing temperatures.

    use_relative_abs : `boolean`, optional
        If true: In calculation of relative uncertainty, use the absolute values of `s`. Applies e.g. to the calculation
        of resistance thermometer uncertainty, typically given as :math:`a + r * abs(T)` according to
        `DIN EN 60751`_.

    Returns
    -------
    pobj
        Unit and uncertainty aware pint Quantity object.

    Notes
    -----
    Drops the series index!

    .. _DIN EN 60751:
        https://www.din.de/de/mitwirken/normenausschuesse/dke/veroeffentlichungen/wdc-beuth:din21:115799593

    Examples
    --------
    # >>> Q = units.Quantity
    # >>> x = to_pint(df['x'], unit='mm', absolute_uncertainty = Q(1, 'mm'), relative_uncertainty = Q(10, 'percent'))
    """

    if unit is None:
        # Try to get unit from s
        try:
            unit = s.dtype.units.__str__()
        except:
            raise ValueError(f'Input pd.Series `s` must have a pint unit (as dtype) if no unit is passed.')

    # is_temperature = punit.is_compatible_with('degC')
    is_temperature = units('degC').is_compatible_with(unit)

    x = s.to_numpy()
    # xu = units.Quantity(x, unit)
    #
    # if absolute_uncertainty is None:
    #     abs_unc = units.Quantity(0, unit)
    # else:
    #     # optionally check compatibility with unit
    #     # absolute_uncertainty.is_compatible_with(unit)
    #     abs_unc = absolute_uncertainty
    # if is_temperature:
    #     abs_unc = units.Quantity(abs_unc.magnitude, 'delta_degC')
    #
    # if relative_uncertainty is None:
    #     rel_unc = units.Quantity(0, unit)
    # else:
    #     # optionally check compatibility:
    #     # relative_uncertainty.is_compatible_with('dimensionless')
    #     if relative_unit is None:
    #         relative_unit = unit
    #     relative_base_value = xu.to(relative_unit)
    #     if use_relative_abs:
    #         relative_base_value = abs(relative_base_value)
    #     if is_temperature:
    #         relative_base_value = units.Quantity(relative_base_value.magnitude, 'delta_degC')
    #     rel_unc = relative_uncertainty * relative_base_value
    #
    # # Calculate uncertainty based on absolute and relative uncertainty
    # unc = abs_unc + rel_unc
    # if is_temperature:
    #     unc_m = unc.magnitude
    # else:
    #     unc_m = unc.to(unit).magnitude
    # uarr = unumpy.uarray(x, unc_m)
    # pobj = units.Quantity(uarr, unit)
    pobj = units.Quantity(x, unit)
    return pobj


def to_dict(q: Q) -> dict | None:
    """"Return dictionary with keys ['magnitude', 'units'], parsable by parse_quantity.
    """
    if q is None:
        return None
    if isinstance(q, dict):
        if set(q.keys()) != {'magnitude', 'units'}:
            raise ValueError(f'Expected dictionary with keys ["magnitude", "units"]. '
                             f'Got keys {", ".join(list(q.keys()))}.')
        return q
    if isinstance(q, Q):
        return {'magnitude': q.magnitude,
                'units': str(q.units)}
    raise TypeError(f'Expected input of type Quantity. Got {q.__class__.__name__}.')


# def to_series(pobj, output_unit=None, direction='plus', k=1, n=1, index=None, name=None):
#     """
#     Converts a (vector) pint Quantity object to a pandas Series by stripping uncertainty and unit from pobj.
#
#     Notes
#     -----
#     Treatment of uncertainty can be controlled by parameters direction and k. This function returns the expanded
#     uncertainty, i.e. lower / upper bound of nominal_value +/- k * standard_uncertainty. For details on expanded
#     uncertainty, see e.g. [1]_
#
#     Parameters
#     ----------
#     pobj : `pint Quantity`
#     pobj
#         Pint object to convert.
#
#     output_unit : `string`, optional
#         Unit string for pobj conversion. If `None`, output series will have the same unit as the input `pobj`.
#         Must be valid unit that can be passed as units(output_unit)
#
#     direction : {'plus', 'minus'}
#         Direction in which uncertainty is added ('plus') or subtracted ('minus') from the nominal values to calculate
#         the expanded uncertainty.
#
#     k : `float`, default=1
#         Amount of uncertainty added to / subtracted from the nominal values to get the expanded uncertainty, in terms
#         of multiples of the standard uncertainty: expanded = nominal_value +/- k * standard_uncertainty
#         Assuming normal distribution, expanded uncertainty with k=1 yields 68% of values, k=2 95%, k=3 99.7%.
#
#     n : `float`, default=1
#         Multiplier of the nominal values in the returned pandas Series. You will in almost all cases leave this at
#         the default value of 1. So the true return formula is: expanded = n * nominal_value +/- k * standard_uncertainty
#
#     index : `pd.Index`, optional
#         pandas.Index that is attached to the output pandas Series.
#
#     name : `string`, optional
#         Name of the output pandas Series.
#
#     Returns
#     -------
#     s : `pd.Series`
#         A pandas Series, optionally with name and index, optionally converted to output_unit.
#
#     References
#     ----------
#     .. [1] `What Does k=2 Mean in Accuracy and Uncertainty
#     Specifications?<https://blog.mensor.com/blog/what-does-k2-mean-in-accuracy-specification>`_
#
#     Examples
#     --------
#     # >>> s = to_series(x)
#     # >>> s = to_series(x, index=index, name='x')
#     # >>> s = to_series(x, direction='plus', k=1, index=index, name='x')
#     # >>> s = to_series(x, output_unit='mm', direction='plus', k=1, index=index, name='x')
#     """
#     # xm = pobj.magnitude
#     # nom = unumpy.nominal_values(xm)
#     # sd = unumpy.std_devs(xm)
#     # sgn = 1 if (direction.lower() == 'plus') else -1
#     # expanded = n * nom + k * sgn * sd
#
#     expanded = pobj.magnitude
#
#     if output_unit is not None:
#         expanded_u = units.Quantity(expanded, pobj.units)
#         expanded = expanded_u.to(output_unit).magnitude
#
#     s = pd.Series(data=expanded, index=index, name=name).astype(f'pint[{output_unit}]')
#     return s


# def nominal_values(pobj, output_unit=None, index=None, name=None):
#     """
#     Strips the uncertainty from a (vector) pint Quantity object and returns the nominal values in a given unit.
#
#     Parameters
#     ----------
#         pint object to convert.
#     pobj : `pint Quantity`
#         pint object to convert.
#     pobj
#         Pint object to convert.
#
#     output_unit : `string`, optional
#         Unit for the output conversion. If `None`, the output series will have the same unit as the input `pobj`.
#         Must be valid unit that can be passed as units(output_unit)
#
#     index : `pd.Index`, optional
#         pandas.Index that is attached to the output pandas Series.
#
#     name : `string`, optional
#         Name of the output pandas Series.
#
#     Returns
#     -------
#     s : `pd.Series`
#         A pandas Series, optionally with name and index, optionally converted to output_unit.
#
#     Examples
#     --------
#     uu.nominal_values(pobj)
#     uu.nominal_values(pobj, output_unit='m')
#     uu.nominal_values(pobj, output_unit='m', index=df.index)
#     uu.nominal_values(pobj, output_unit='m', index=df.index, name='x')
#     """
#     return to_series(pobj, output_unit=output_unit, k=0, index=index, name=name).astype(f'pint[{output_unit}]')


# def std_devs(pobj, output_unit=None, index=None, name=None):
#     """
#     Returns the uncertainty from a (vector) pint Quantity object and returns the uncertainty in a given unit.
#
#     Parameters
#     ----------
#     pobj : `pint Quantity`
#     pobj
#         Pint object to convert.
#
#     output_unit : `string`, optional
#         Unit for the output conversion. If `None`, the output series will have the same unit as the input `pobj`.
#         Must be valid unit that can be passed as units(output_unit)
#
#     index : `pd.Index`, optional
#         pandas.Index that is attached to the output pandas Series.
#
#     name : `string`, optional
#         Name of the output pandas Series.
#
#     Returns
#     -------
#     s : `pd.Series`
#         A pandas Series, optionally with name and index, optionally converted to output_unit.
#
#     Examples
#     --------
#     uu.std_devs(pobj)
#     uu.std_devs(pobj, output_unit='m')
#     uu.std_devs(pobj, output_unit='m', index=df.index)
#     uu.std_devs(pobj, output_unit='m', index=df.index, name='x')
#     """
#     return to_series(pobj, output_unit=output_unit, direction='plus', k=1, n=0, index=index, name=name).astype(
#         f'pint[{output_unit}]')


# def isna(pobj):
#     """
#     Returns boolean array where nominal value or standard deviation of a pint object is NaN.
#
#     Parameters
#     ----------
#     pobj : pint Quantity object
#         Pint object to check.
#
#     Returns
#     -------
#     is_na : `numpy.ndarray`
#         Boolean array, True where nominal value or standard deviation is NaN, False otherwise.
#
#     Examples
#     --------
#     uu.isna(pobj)
#     """
#     is_na_nom = pd.isna(nominal_values(pobj)).to_numpy()
#     is_na_std = pd.isna(std_devs(pobj)).to_numpy()
#     is_na = is_na_nom | is_na_std
#     return is_na


def check_quantity(q, unit='', min_limit=-np.inf, max_limit=np.inf, none_allowed=False, max_ndim=0) -> Q:
    """
    Check that `q` is a valid pint Quantity object.

    Parameters
    ----------
    q : pint Quantity or pd.Series
        Quantity object to check.
    unit : str, optional
        `q` must be compatible with `unit`. Use default `unit=''` for dimensionless quantity.
    min_limit : float, optional
        `q` must be >= `min_limit`, where `min_limit` is interpreted as Quantity in `unit`, so `Q(min_limit, 'unit')`
    max_limit : float, optional
        `q` must be <= `max_limit`, where `max_limit` is interpreted as Quantity in `unit`, so `Q(max_limit, 'unit')`
    none_allowed : bool, optional
        If False: Will raise ValueError if `q` is None.
    max_ndim : int, optional, default 0
        Maximum allowed numpy ndim of `q`. Set max_ndim==0 to enforce `q` as scalar, max_ndim==1 for vector, etc.

    Returns
    -------
    pint Quantity
        Input `q` converted to `unit`, if `q` passes all tests / conditions.

    Raises
    ------
    TypeError
        If `q` is not a scalar pint Quantity or None and none_allowed==False, or if `q` is not compatible with `unit`.
    ValueError
        If `q` is outside `min_limit` | `max_limit`.
    """

    if (q is None) and (not none_allowed):
        raise TypeError('Input `q` must not be None.')
    elif (q is None) and none_allowed:
        return q
    if not isinstance(q, pint.Quantity):
        raise TypeError(f'Input `q` must be a pint Quantity object. Got a {type(q)} instead.')
    if np.array(q.magnitude).ndim > max_ndim:
        raise TypeError(f'Input `q` exceeds maximum allowed dimension {max_ndim}.')
    try:
        q.ito(unit)
    except pint.errors.DimensionalityError:
        raise TypeError(f'Input `q` must be compatible with unit {unit}.')
    min_limit = Q(min_limit, unit)
    max_limit = Q(max_limit, unit)
    if any(np.array(q < min_limit).ravel()) or any(np.array(q > max_limit).ravel()):
        raise ValueError(f'Input `q` must be within limits {min_limit:~} and {max_limit:~}, but is {q:~}')

    return q


def parse_quantity(value: Union[dict, list, Q, pd.Series]) -> Q:
    if (value is None) or isinstance(value, Q):
        return value
    elif 'magnitude' and 'units' in value:
        return Q(value['magnitude'], value['units'])
    elif isinstance(value, pd.Series):
        return Q(value.astype('float64').to_numpy(), value.pint.units.__str__())
    elif isinstance(value, list):
        try:
            return Q(value[0], value[1])
        except (IndexError, TypeError):
            raise ConfigurationError("If passing quantities as lists, they must be in the form: [magnitude, unit], "
                                     "e.g. [1, 'm'], and unit must be a valid Pint unit string, see "
                                     "https://github.com/hgrecco/pint/blob/master/pint/default_en.txt")
    else:
        raise ConfigurationError("Component attributes must be passed as either Pint Quantity objects, a dict with "
                                 "'magnitude' and 'units' keys, or a list like [1, 'unit']")
