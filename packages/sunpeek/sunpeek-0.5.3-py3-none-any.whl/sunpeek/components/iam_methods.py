# -*- coding: utf-8 -*-
"""
This modules hosts a number of functions and classes for calculation of the IAM (incidence angle modifier) that is
used to quantify the effect of non-normal incident radiation on a solar collector surface.

In solar thermal engineering, different IAM calculation models exist, using different inputs.
Some popular calculation models are implemented in this module, including:
- The popular ASHRAE model (using one parameter: `b`): :func:`get_iam_ASHRAE()`
- The Ambrosetti model (one parameter: `kappa`): :func:`get_iam_ambrosetti()`
- An IAM calculated based on an interpolation of given reference IAM and incidence angle values.
"""

from abc import abstractmethod
import pandas as pd
import numbers
import pvlib
import numpy as np
from sqlalchemy import Column, Integer, Enum, Identity, ForeignKey
from sqlalchemy.orm import relationship

from sunpeek.common.unit_uncertainty import Q, to_s, to_numpy
from sunpeek.components.helpers import ORMBase, ComponentParam, AttrSetterMixin


# -----------
# Functions
# -----------

def get_iam_ASHRAE(aoi: pd.Series, b: Q):
    """ Determines the incidence angle modifier using the ASHRAE transmission model, using :py:mod:pvlib.

    Parameters
    ----------
    aoi : pd.Series
        The angle of incidence (AOI) between the normal vector of the collector plane and the
        sun-beam vector, as pint (unit aware) pandas Series. Angles of NaN will result in NaN.
    b : float, default 0.05
        A parameter to adjust the incidence angle modifier as a function of
        angle of incidence. Typical values are on the order of 0.05 to 0.2 [3].

    Returns
    -------
    `pd.Series`
        A unit-aware, dimensionless pandas Series containing the IAM values.

    See Also
    --------
    IAM_ASHRAE
    """
    aoi = to_numpy(aoi, 'deg')
    b = b.m_as('')
    iam = pvlib.iam.ashrae(aoi, b=b)
    return to_s(iam)


def get_iam_k50(aoi: pd.Series, k50: Q):
    """ Determines the incidence angle modifier using the ASHRAE transmission model, if only `k50`, the IAM value at
    aoi=50° is given.

    Parameters
    ----------
    aoi : pd.Series
        The angle of incidence (AOI) between the module normal vector and the
        sun-beam vector, as pint (unit aware) pandas Series. Angles of NaN will result in NaN.
    k50 : Quantity
        Incidence angle modifier for angle of incidence of 50°. This can be converted to b0 used for the ASHRAE IAM
        model.

    Returns
    -------
    `pd.Series`
        A unit-aware, dimensionless pandas Series containing the IAM values.

    See Also
    --------
    sunpeek.components.iam_methods.IAM_ASHRAE
    """
    aoi = to_numpy(aoi, 'deg')
    k50 = k50.m_as('')
    rad_50 = 50 * np.pi / 180
    b = -(k50 - 1) / (1 / np.cos(rad_50) - 1)
    iam = pvlib.iam.ashrae(aoi, b=b)
    return to_s(iam)


def get_iam_ambrosetti(aoi: pd.Series, kappa: Q):
    """ Determines the incidence angle modifier using the Ambrosetti function, as defined in ISO 9806.

    Parameters
    ----------
    aoi : pd.Series
        The angle of incidence (AOI) between the module normal vector and the
        sun-beam vector, as pint (unit aware) pandas Series. Angles of NaN will result in NaN.
    kappa : Quantity
        Exponent used for the Ambrosetti function.

    Returns
    -------
    `pd.Series`
        A unit-aware, dimensionless pandas Series containing the IAM values.

    Notes
    -----
    The incidence angle modifier is calculated using the Ambrosetti function, as

    .. math::

        IAM = 1 - (\tan (aoi/2))^(kappa)
    """
    aoi = to_numpy(aoi, 'rad')
    kappa = kappa.m_as('')
    iam = 1 - np.tan(aoi / 2) ** kappa
    return to_s(iam)


def get_iam_interpolated(aoi: pd.Series, iam_reference: Q, aoi_reference: Q, azimuth_diff: Q = Q(0, 'deg')):
    """ Determines the incidence angle modifier by interpolating over a set of given reference values.

    Parameters
    ----------
    aoi : pandas.Series
        The angle of incidence between the module normal vector and the
        sun-beam vector, as pint (unit aware) pandas Series. Angles of NaN will result in NaN.
    aoi_reference : Quantity
        Vector of angles at which the IAM is known [degrees].
    iam_reference : Quantity
        IAM values for each angle in ``aoi_reference`` [unitless].
    azimuth_diff : pandas.Series
        The difference between solar and collector azimuth angle [degrees].

    Returns
    -------
    pandas.Series
        A unit-aware, dimensionless pandas Series containing the IAM values.

    Notes
    -----
    Determines the IAM based on interpolating a set of reference values based on ISO 9806 [1]_. This is similar to
    `pvlib.iam.interp`, but allows separation in longitudinal and transversal plane, whereas pvlib works only for
    symmetric collector IAMs.

    The IAM reference values `iam_reference` are usually measured values [1]_.

    ``aoi_reference`` must have two or more points and may span any range of angles. Typically there will be a dozen
    or more points in the range 0..90 degrees. Beyond the range of ``aoi_reference``, IAM values are extrapolated,
    but constrained to be non-negative.

    The sign of ``aoi`` is ignored; only the magnitude is used.

    See Also
    --------
    pvlib.iam.interp

    References
    ----------
    .. [1] ISO 9806 Solar Energy Draft pp.53 Formula (22, 23, 25, 27)
    """

    aoi_reference = aoi_reference.m_as('deg')
    iam_reference = iam_reference.m_as('')
    aoi = to_numpy(aoi, 'deg')
    azimuth_diff = to_numpy(azimuth_diff, 'deg')

    aoi_reference, iam_reference = _normalize_iam_reference(aoi_reference=aoi_reference, iam_reference=iam_reference)

    # get components in transversal and longitudinal plane
    aoi_transversal = _get_aoi_transversal(aoi=aoi, azimuth_diff=azimuth_diff)
    aoi_longitudinal = _get_aoi_longitudinal(aoi=aoi, azimuth_diff=azimuth_diff)

    # interpolate IAM
    iam_transversal = np.interp(np.abs(aoi_transversal), aoi_reference[0], iam_reference[0])
    iam_longitudinal = np.interp(np.abs(aoi_longitudinal), aoi_reference[1], iam_reference[1])
    iam = np.multiply(iam_transversal, iam_longitudinal)
    return to_s(iam)


def _get_aoi_transversal(aoi, azimuth_diff):
    """ Determines the angle of incidence on the transversal plane (in degrees).

    Parameters
    ----------
    aoi : numeric
        The angle of incidence between the module normal vector and the
        sun-beam vector [degrees].
    azimuth_diff : numeric
        The difference between solar and collector azimuth angle [degrees].

    Notes
    -----
    Calculation is based on equation 5 of this paper:
    S. Hess and V. I. Hanby, “Collector Simulation Model with Dynamic Incidence Angle Modifier for Anisotropic Diffuse
    Irradiance,” Energy Procedia, vol. 48, pp. 87–96, 2014, doi: 10.1016/j.egypro.2014.02.011.
    """
    aoi_rad = np.deg2rad(aoi)
    azimuth_diff_rad = np.deg2rad(azimuth_diff)
    aoi_transversal = np.rad2deg(-np.arctan(np.tan(aoi_rad) * np.cos(azimuth_diff_rad)))
    return np.abs(aoi_transversal)


def _get_aoi_longitudinal(aoi, azimuth_diff):
    """ Determines the angle of incidence on the longitudinal plane (in degrees)

    Parameters
    ----------
    aoi : numeric
        The angle of incidence between the module normal vector and the
        sun-beam vector [degrees].
    azimuth_diff : numeric
        The difference between solar and collector azimuth angle [degrees].

    Notes
    -----
    Calculation is based on equation 4 of this paper:
    S. Hess and V. I. Hanby, “Collector Simulation Model with Dynamic Incidence Angle Modifier for Anisotropic Diffuse
    Irradiance,” Energy Procedia, vol. 48, pp. 87–96, 2014, doi: 10.1016/j.egypro.2014.02.011.
    """
    aoi_rad = np.deg2rad(aoi)
    azimuth_diff_rad = np.deg2rad(azimuth_diff)
    aoi_longitudinal = np.rad2deg(np.arctan(np.sin(aoi_rad) * np.sin(azimuth_diff_rad) / np.cos(aoi_rad)))
    return np.abs(aoi_longitudinal)


# -----------
# HELPER
# -----------

def _normalize_iam_reference(aoi_reference: list, iam_reference: list):
    """ Normalizes reference values for incidence angle modifier and corresponding incidence angle references.

    Parameters
    ----------
    aoi_reference : list of floats
        Vector of angles at which the IAM is known [degrees].
    iam_reference : list of floats
        IAM values for each angle in ``aoi_reference`` [unitless].
    """
    if iam_reference is None or aoi_reference is None:
        return None, None

    aoi_reference, iam_reference = _to_2D_list(aoi_reference=aoi_reference, iam_reference=iam_reference)
    aoi_reference[0], iam_reference[0] = _add_boundaries(aoi_reference=aoi_reference[0], iam_reference=iam_reference[0])
    aoi_reference[1], iam_reference[1] = _add_boundaries(aoi_reference=aoi_reference[1], iam_reference=iam_reference[1])
    return aoi_reference, iam_reference


def _to_2D_list(aoi_reference: list, iam_reference: list):
    """ Modifies the supplied references so 2D lists for iam and aoi are returned
    (one for transversal aoi, and one for longitudinal aoi).

    Parameters
    ----------
    aoi_reference : list of floats
        Vector of angles at which the IAM is known [degrees].
    iam_reference : list of floats
        IAM values for each angle in ``aoi_reference`` [unitless].
    """
    aoi_is_not_2D = isinstance(aoi_reference[0], numbers.Number)
    iam_is_not_2D = isinstance(iam_reference[0], numbers.Number)

    if aoi_is_not_2D:
        aoi_reference = [aoi_reference, aoi_reference]
    if iam_is_not_2D:
        iam_reference = [iam_reference, iam_reference]

    iam_reference = [list(iam_reference[0]), list(iam_reference[1])]
    aoi_reference = [list(aoi_reference[0]), list(aoi_reference[1])]
    return aoi_reference, iam_reference


def _add_boundaries(aoi_reference: list, iam_reference: list):
    """ Applies default boundary values for the IAM based on ISO 9806 Solar Energy Draft:
     - the incidence angle modifier is 0.00 at an incidence angle of 90°
     - the incidence angle modifier is 1.00 at an incidence angle of 0°
    if not otherwise specified.

    Parameters
    ----------
    aoi_reference : list of floats
        Vector of angles at which the IAM is known [degrees].
    iam_reference : list of floats
        IAM values for each angle in ``aoi_reference`` [unitless].
    """
    aoi = aoi_reference.copy()
    iam = iam_reference.copy()
    max_boundary_missing = (0 not in aoi_reference)
    min_boundary_missing = (90 not in aoi_reference)

    if max_boundary_missing:
        aoi.insert(0, 0)
        iam.insert(0, 1.00)

    if min_boundary_missing:
        aoi.append(90)
        iam.append(0.00)
    return aoi, iam


# -----------
# CLASSES
# -----------

class IAM_Method(ORMBase, AttrSetterMixin):
    __tablename__ = 'iam_methods'
    """ Abstract class for determining the incidence angle modifier (IAM) with different methods.
    """
    id = Column(Integer, Identity(0), primary_key=True)
    method_type = Column(Enum('IAM_Ambrosetti', 'IAM_ASHRAE', 'IAM_Interpolated', 'IAM_K50', name='iam_method_type'))
    collector_id = Column(Integer, ForeignKey('collectors.id', ondelete="CASCADE"))
    collector = relationship("Collector", back_populates="iam_method")

    __mapper_args__ = {
        'polymorphic_identity': 'iam_method',
        'polymorphic_on': method_type,
        'with_polymorphic': '*'
    }

    @abstractmethod
    def get_iam(self, aoi: pd.Series, azimuth_diff: pd.Series):
        """ Determines the IAM for given incidence angles ``aoi`` [degrees] and difference between solar and collector
        azimuth angle [degrees].

        Parameters
        ----------
        aoi : pd.Series
            The angle of incidence (AOI) between the module normal vector and the sun-beam vector,
            as pint (unit aware) pandas Series. Angles of NaN will result in NaN.
        azimuth_diff : pd.Series
            The difference between solar and collector azimuth angle, as pint (unit aware) pandas Series.
        """
        raise NotImplementedError("")


class IAM_ASHRAE(IAM_Method):
    """
    Determine the IAM for given incidence angles ``aoi`` [degrees], using the ASHRAE formula.

    Parameters
    ----------
    b : float, default 0.05
        A parameter to adjust the incidence angle modifier as a function of
        angle of incidence. Typical values are on the order of 0.05 [3].

    See Also
    --------
    :func:`components.iam_methods.get_iam_ASHRAE`
    """

    __mapper_args__ = {
        'polymorphic_identity': 'IAM_ASHRAE',
    }

    b = ComponentParam('', 0, 1)

    def __init__(self, b: Q, plant=None):
        self.b = b

    def get_iam(self, aoi: pd.Series, **kwargs):
        return get_iam_ASHRAE(aoi, b=self.b)


class IAM_K50(IAM_Method):
    """
    Determine the IAM for given incidence angles ``aoi`` [degrees], using the ASHRAE formula, if only `k50`,
    the IAM value at an incidence angle of 50°, is given.

    Parameters
    ----------
    k50 : float
        IAM value at an incidence angle of 50°

    See Also
    --------
    :func:`components.iam_methods.get_iam_k50`
    """
    __mapper_args__ = {
        'polymorphic_identity': 'IAM_K50',
    }

    b = ComponentParam('', 0, 1)
    k50 = ComponentParam('', 0, 2)

    def __init__(self, k50: Q, plant=None):
        self.k50 = k50
        self.b = -(self.k50 - 1) / (1 / np.cos(np.deg2rad(50)) - 1)

    def get_iam(self, aoi: pd.Series, **kwargs):
        return get_iam_ASHRAE(aoi, b=self.b)


class IAM_Ambrosetti(IAM_Method):
    """Determine the IAM for given incidence angles ``aoi`` [degrees], using the Ambrosetti formula.

    Parameters
    ----------
    kappa : float
        exponent used for the Ambrosetti function

    See Also
    --------
    :func:`components.iam_methods.get_iam_ambrosetti`
    """

    __mapper_args__ = {
        'polymorphic_identity': 'IAM_Ambrosetti',
    }

    kappa = ComponentParam('', 1, 50)

    def __init__(self, kappa: Q, plant=None):
        self.kappa = kappa

    def get_iam(self, aoi: pd.Series, **kwargs):
        return get_iam_ambrosetti(aoi, kappa=self.kappa)


class IAM_Interpolated(IAM_Method):
    """
    Determine the incidence angle modifier by interpolating over a set of given reference values.

    Parameters
    ----------
    iam_reference: list
        Reference values for IAM values at certain incidence angles. (must match with `aoi_reference`)
    aoi_reference: list
        Reference values for IAM values at certain incidence angles. (must match with `iam_reference`)

    See Also
    --------
    :func:`components.iam_methods.get_iam_interpolated`
    """

    __mapper_args__ = {
        'polymorphic_identity': 'IAM_Interpolated',
    }

    aoi_reference = ComponentParam('deg', 0, 90, param_type='array')
    iam_reference = ComponentParam('', 0, 2, param_type='array')

    def __init__(self, iam_reference: Q, aoi_reference: Q, plant=None):
        # is then saved as a 2D list = 2 lists, one for longitudinal and one for transversal values
        aoi_reference, iam_reference = _normalize_iam_reference(aoi_reference=aoi_reference.m_as('deg'),
                                                                iam_reference=iam_reference.m_as(''))
        self.aoi_reference = Q(aoi_reference, 'deg')
        self.iam_reference = Q(iam_reference)
        return

    def get_iam(self, aoi: pd.Series, azimuth_diff: pd.Series):
        return get_iam_interpolated(aoi,
                                    iam_reference=self.iam_reference,
                                    aoi_reference=self.aoi_reference,
                                    azimuth_diff=azimuth_diff)
