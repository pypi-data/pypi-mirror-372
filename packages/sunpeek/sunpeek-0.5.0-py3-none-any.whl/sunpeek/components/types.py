import numpy as np
import enum

import pint
import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, DateTime, Enum, Identity, JSON
from sqlalchemy import inspect
from typing import Union, Tuple
import datetime as dt
import copy
import dataclasses

from sunpeek.components import iam_methods
from sunpeek.components.iam_methods import IAM_Method
from sunpeek.common import unit_uncertainty as uu
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.errors import CollectorDefinitionError
from sunpeek.components.helpers import ORMBase, AttrSetterMixin, ComponentParam
from sunpeek.base_model import BaseModel, Quantity


class ApertureParameters(BaseModel):
    a1: Quantity | None
    a2: Quantity | None
    a5: Quantity | None
    a8: Quantity | None


@dataclasses.dataclass
class SensorType:
    name: str
    compatible_unit_str: str
    description: str
    lower_replace_min: Union[Q, None] = None
    lower_replace_max: Union[Q, None] = None
    lower_replace_value: Union[Q, None] = None
    upper_replace_min: Union[Q, None] = None
    upper_replace_max: Union[Q, None] = None
    upper_replace_value: Union[Q, None] = None
    max_fill_period: Union[dt.timedelta, None] = None
    sensor_hangs_period: Union[dt.timedelta, None] = None
    info_checks: Union[dict, None] = None
    common_units: Union[list, None] = None

    @property
    def info_checks(self):
        if getattr(self, '_info_checks', None) is not None:
            return self._info_checks
        else:
            return {}

    @info_checks.setter
    def info_checks(self, val):
        self._info_checks = val


class CollectorTypes(str, enum.Enum):
    flat_plate = "flat_plate"
    concentrating = "concentrating"
    WISC = "WISC"  # Wind and Infrared Sensitive Collector


class CollectorTestTypes(str, enum.Enum):
    SST = "SST"  # Steady-State Test
    QDT = "QDT"  # Quasi-Dynamic Test


class CollectorReferenceAreaTypes(str, enum.Enum):
    gross = "gross"
    aperture = "aperture"


class Collector(AttrSetterMixin, ORMBase):
    """
    Implements a specific collector (product of some manufacturer), including all performance data acc. to data sheet.

    Stores two different collector type parameters, referring to the two test procedures defined in `ISO 9806`_,
    either quasi-dynamic or steady-state test. The type of test procedure is available from the standard collector
    data sheet / Solar Keymark certificate and must be specified in `test_type`.

    Test parameters may refer to either gross or aperture area. This must be specified in `test_reference_area`. The
    collector parameters stored in Collector _always_ refer to gross area.

    IAM (incidence angle modifier) information may be given as an instance of the IAM_Method class. This holds
    several implementations where the IAM information can be given in either of these ways:
    - If only IAM information at an aoi of 50 degrees is given, use `IAM_K50(k50)`. Internally, this uses the ASHRAE equation.
    - To use the ASHRAE IAM equation with a known parameter `b`, use `IAM_ASHRAE(b)`.
    - To use the Ambrosetti IAM equation with a known parameter `kappa`, use `IAM_Ambrosetti(kappa)`.
    - To use an IAM with given / known IAM values at given aoi angles, use `IAM_Interpolated()`. This requires a list
    of reference aoi's, and either a) 1 list of IAM values or b) 2 lists with transversal and longitudinal IAM
    values.

    Attributes
    ----------
    name : str
        Name of collector type. Must be unique within HarvestIT 'collector' database.
    manufacturer_name : str, optional
        Manufacturer name. Example: "GREENoneTEC Solarindustrie GmbH"
    product_name : str, optional
        Product name. Example: "GK 3133"

    licence_number : str, optional
        Licence number (often also known as Registration number) of the Solar Keymark certificate.
    test_report_id : str, optional
        "Test Report(s)" field on Solar Keymark certificate.
    certificate_date_issued : datetime, optional
        "Date issued" field on Solar Keymark certificate.
    certificate_lab : str, optional
        Laboratory / testing institution that issued the collector test certificate.
    certificate_details : str, optional
        Details concerning the official collector test / Solar Keymark certificate, such as testing institution etc.
    collector_type : CollectorTypes or str
        Construction type of the collector, as defined in Solar Keymark / ISO 9806.
        Main distinction is between flat plate and concentrating collectors.
    test_type : str
        Type of collector test, according to `ISO 9806`_. Valid values: 'QDT' | 'dynamic' | 'SST' | 'static'
    test_reference_area : str
        Collector area to which the test data refer. Valid values: 'area_ap | 'aperture' | 'area_gr' | 'gross'.
    area_gr : pint Quantity, optional
        Gross collector area. Mandatory if `test_reference_area`=='aperture', optional otherwise.
    area_ap : pint Quantity, optional
        Gross collector area. Mandatory if `test_reference_area`=='aperture', optional otherwise.

    gross_length : pint Quantity
        Gross length of one collector (collector side pointing upwards). Typical value around Q(2, 'm')
    gross_width : pint Quantity
        Gross width of one collector (normal to gross_length, i.e. measured parallel to the ground). For large-area
        flat plate collectors, a typical value is Q(6.0, 'm').
    gross_height : pint Quantity
        Gross height ('thickness') of one collector (from cover to backside). A typical value is Q(20, 'cm').

    a1 : pint Quantity
        Linear heat loss coefficient, according to collector test data sheet of quasi dynamic
        or steady state test.
    a2 : pint Quantity
        Quadratic heat loss coefficient, according to collector test data sheet of quasi dynamic
        or steady state test.
    a5 : pint Quantity
        Effective thermal heat capacity, according to collector test data sheet of quasi dynamic
        or steady state test.
    a8 : pint Quantity
        Radiative heat loss coefficient, according to collector test data sheet of quasi dynamic
        or steady state test.
    kd : pint Quantity, optional
        Incidence angle modifier for diffuse radiation, according to collector test data sheet of quasi dynamic test.
        Mandatory if `test_type`=='QDT'.
    eta0b : pint Quantity, optional
        Peak collector efficiency (= zero loss coefficient) based on beam irradiance, according
        to collector test data sheet of quasi dynamic test.
    eta0hem : pint Quantity, optional
        Peak collector efficiency (= zero loss coefficient) based on hemispherical irradiance,
        according to collector test data sheet of steady state test (or calculated from quasi-dynamic test).
    f_prime : pint Quantity
        Collector efficiency factor, i.e. ratio of heat transfer resistances of absorber to ambient vs. fluid to ambient.
    concentration_ratio : pint Quantity
        Geometric concentration ratio: Factor by which solar irradiance is concentrated onto the collector's
        absorbing surface.
        When applying a ISO 24194 Thermal Power Check, the `concentration_ratio` is used to determine which of the
        3 formulae defined in ISO 24194 to apply.
    calculation_info : dictionary
        Contains information about calculated collector parameters, where specific information was not given at
        instantiation of the object, e.g. because the Solar Keymark data sheet does not include a specific parameter.
        Some parameters can be calculated based on given ones, e.g. `Kd` (diffuse IAM) can be calculated based on
        given IAM information. Dictionary keys are the names of calculated parameters (e.g. `kd`), dictionary values
        hold information concerning specific calculation details (e.g. calculation method).
    plant : None
        Not used, included for compatibility with other component types.

    .. _ISO 9806:
        https://www.iso.org/standard/67978.html
    .. _ASHRAE model:
        https://pvlib-python.readthedocs.io/en/stable/generated/pvlib.iam.ashrae.html
    """
    __tablename__ = 'collectors'

    # Name is the PK, and is required whenever a DB store is in use.
    id = Column(Integer, Identity(), primary_key=True)
    name = Column(String, unique=True, nullable=False)
    manufacturer_name = Column(String)
    product_name = Column(String)
    licence_number = Column(String)
    test_report_id = Column(String)
    certificate_date_issued = Column(DateTime)
    certificate_lab = Column(String)
    certificate_details = Column(String)
    collector_type = Column(Enum(CollectorTypes), nullable=False)

    test_type = Column(Enum(CollectorTestTypes))
    test_reference_area = Column(Enum(CollectorReferenceAreaTypes))
    calculation_info = Column(JSON)
    aperture_parameters = Column(JSON)

    # No limit checks for these attributes to avoid code duplication with self._set_collector_parameters()
    iam_method = relationship("IAM_Method", back_populates='collector', uselist=False, cascade="all, delete",
                              passive_deletes=True)
    area_gr = ComponentParam('m**2', minimum=0.1)
    area_ap = ComponentParam('m**2', minimum=0.1)
    gross_length = ComponentParam('cm', minimum=0)
    gross_width = ComponentParam('cm', minimum=0)
    gross_height = ComponentParam('cm', minimum=0)
    a1 = ComponentParam('W m**-2 K**-1', minimum=0, maximum=20)
    a2 = ComponentParam('W m**-2 K**-2', minimum=0, maximum=1)
    a5 = ComponentParam('J m**-2 K**-1', minimum=1, maximum=100000)
    a8 = ComponentParam('W m**-2 K**-4', minimum=0, maximum=1)
    kd = ComponentParam('', minimum=0, maximum=2)
    eta0b = ComponentParam('', minimum=0, maximum=1)
    eta0hem = ComponentParam('', minimum=0, maximum=1)
    f_prime = ComponentParam('', minimum=0, maximum=1)
    concentration_ratio = ComponentParam('', minimum=1)

    def __init__(self, test_reference_area, test_type, gross_length, collector_type: CollectorTypes,
                 iam_method: IAM_Method = None, concentration_ratio=None,
                 name=None, manufacturer_name=None, product_name=None, test_report_id=None, licence_number=None,
                 certificate_date_issued=None, certificate_lab=None, certificate_details=None,
                 area_gr=None, area_ap=None, gross_width=None, gross_height=None,
                 a1=None, a2=None, a5=None, a8=None, kd=None, eta0b=None, eta0hem=None, f_prime=None, **kwargs):

        self.test_reference_area = self._infer_test_reference_area(test_reference_area)
        self.test_type = self._infer_test_type(test_type)
        self.iam_method = iam_method

        self.name = name
        self.manufacturer_name = manufacturer_name
        self.product_name = product_name

        self.licence_number = licence_number
        self.test_report_id = test_report_id
        self.certificate_date_issued = certificate_date_issued
        self.certificate_lab = certificate_lab
        self.certificate_details = certificate_details
        self.collector_type = collector_type
        self.concentration_ratio = concentration_ratio
        # self.description = description

        self.gross_length = gross_length
        self.gross_width = gross_width
        self.gross_height = gross_height
        self.f_prime = f_prime

        self.area_gr = area_gr
        self.area_ap = area_ap
        self.a1 = a1
        self.a2 = a2
        self.a5 = a5
        self.a8 = a8
        self.kd = kd
        self.eta0b = eta0b
        self.eta0hem = eta0hem

        self._aperture_parameters = {}
        self.update_parameters()

    def update_parameters(self) -> None:
        """
        Check and set collector parameters. Convert parameters from aperture to gross are, if ref area is aperture.

        Raises
        ------
        CollectorDefinitionException
            If definition of collector parameters is incomplete or contradictory.

        Notes
        -----
        - This method checks that we have a complete and valid Collector definition, for both test_types 'SST' | 'QDT'.
        - This method exists because parameters are interdependent, so setting collector parameters can't be done
           per-attribute (in setter methods e.g.). Attributes that don't depend on others are set in __init__ directly.
        - This methods sets the instance attributes, with reference to gross area "area_gr", if params is sane.
        - Converts from aperture to gross area, if necessary. To do so, both "area_gr" and "area_ap" are required.
        - Either "eta0b" or "eta0hem" must be provided in params
        - For statically-tested collectors only: Estimates `kd` using calculate_kd_Hess_and_Hanby(), if necessary.
        """
        # Parse & store current object parameters -> might refer to aperture, may be overwritten
        required_not_none = {'gross_length', 'area_gr', 'a1', 'a2', 'a5'}
        for k in required_not_none:
            if self.__getattribute__(k) is None:
                raise CollectorDefinitionError(f'Collector parameter is None, but must be specified: "{k}".')

        coll_params = {'a1', 'a2', 'a5', 'a8', 'kd', 'eta0b', 'eta0hem'}
        p = {k: uu.parse_quantity(self.__getattribute__(k)) for k in coll_params}

        if self.area_ap is not None and (self.area_ap > self.area_gr):
            raise CollectorDefinitionError(f'Aperture area must be smaller than gross area. You provided '
                                           f'"area_ap"={self.area_ap}, "area_gr"={self.area_gr}.')

        if (p['eta0hem'] is None) and (p['eta0b'] is None):
            raise CollectorDefinitionError('Either "eta0b" or "eta0hem" must be provided for a collector, '
                                           'but both are missing.')

        is_aperture = (self.test_reference_area == CollectorReferenceAreaTypes.aperture.value)
        if is_aperture and self.area_ap is None:
            raise CollectorDefinitionError(f'In a collector with test_reference_area "aperture", '
                                           f'both gross and aperture collector areas must be given.')

        is_qdt = (self.test_type == CollectorTestTypes.QDT.value)
        if is_qdt and p['kd'] is None:
            raise CollectorDefinitionError('For a collector with QDT collector test ("dynamically-tested"), '
                                           '"kd" must be provided.')

        # Calculate missing parameters, if needed and if possible  -------------------------
        self.calculation_info = {}

        if p['kd'] is None and not is_qdt:  # Is applied to SST collectors only, QDT must already have 'kd'
            p['kd'], info = calculate_kd_Hess_and_Hanby(self.iam_method)
            self.calculation_info['kd'] = info

        if p['eta0hem'] is None:
            p['eta0hem'], info = calculate_eta0hem(eta0b=p['eta0b'], kd=p['kd'])
            self.calculation_info['eta0hem'] = info

        if p['eta0b'] is None:
            p['eta0b'], info = calculate_eta0b(eta0hem=p['eta0hem'], kd=p['kd'])
            self.calculation_info['eta0b'] = info

        if self.test_reference_area == CollectorReferenceAreaTypes.gross.value:
            self.aperture_parameters = {}
            self._write_attribs(p)
            return  # Nothing to do, no area conversion needed. Otherwise, conversion aperture -> gross follows.

        # Convert aperture -> gross  ------------------------

        # Use values stored in self.aperture_parameters if possible
        if not self.aperture_parameters:
            # Store parameters with reference area "aperture"
            self.aperture_parameters = {k: uu.to_dict(p[k]) for k in ['a1', 'a2', 'a5', 'a8']}

        # Do the area conversion
        conversion_factor = self.area_ap / self.area_gr
        p_final = {k: None if v is None else conversion_factor * uu.parse_quantity(v)
                   for k, v in self.aperture_parameters.items()}
        p_final.update({k: p[k] for k in coll_params if k not in p_final})  # Update with non-converted params
        self._write_attribs(p_final)

        # Add calculation_info about area conversion
        for k, v in self.aperture_parameters.items():
            self.calculation_info.setdefault(k, '')
            self.calculation_info[k] += 'Converted from aperture to gross area by SunPeek.'

    def _write_attribs(self, p: dict) -> None:
        """Set collector object attributes from dictionary. Dict values may be dicts, parsable by parse_quantity.
        """
        for k, v in p.items():
            try:
                self.__setattr__(k, None if v is None else uu.parse_quantity(v))
            except:
                pass

    @sqlalchemy.orm.validates('aperture_parameters')
    def _validate_aperture_parameters(self, _, val):
        if val == {} or val is None:
            return None
        return ApertureParameters(**val).dict()

    @sqlalchemy.orm.validates('iam_method')
    def _validate_iam_method(self, _, val):
        if isinstance(val, dict):
            val = copy.copy(val)
            # because the iam methods expect Quantities, we need to convert them here in case we have dict...
            for key, value in val.items():
                if "magnitude" in value:
                    val[key] = Q(value["magnitude"], value["units"])
            return iam_methods.__dict__[val.pop('method_type')](**val)
        return val

    @staticmethod
    def _infer_test_type(test_type: Union[str, None]) -> str:
        """Returns test type (static, dynamic) based on user input.
        """
        if test_type is None or test_type not in list(CollectorTestTypes):
            raise CollectorDefinitionError(f'Collector "test_type" invalid: {test_type}. '
                                           f'Must be one of {", ".join(CollectorTestTypes)}.')
        return test_type

    @staticmethod
    def _infer_test_reference_area(area: Union[str, None]) -> str:
        """Return test reference area type (gross, aperture) based on user input.
        """
        if area is None or area not in list(CollectorReferenceAreaTypes):
            raise CollectorDefinitionError(f'Collector "test_reference_area" invalid: {area}. '
                                           f'Must be one of: {", ".join(CollectorReferenceAreaTypes)}.')
        return area

    def is_attrib_missing(self, attrib_name):
        # May raise AttributeError
        attrib = getattr(self, attrib_name)
        if attrib is None:
            return True
        if not isinstance(attrib, Q):
            return True
        return False

    def is_zero(self, param_name: str) -> bool:
        """Return True if some collector parameter is zero.
        """
        param = getattr(self, param_name)
        return (param is None) or (param == Q(0, param.units))

    def is_nonzero(self, param_name: str) -> bool:
        """Return True if some collector parameter is greater than zero.
        """
        param = getattr(self, param_name)
        return (param is not None) and (param > Q(0, param.units))

    def __eq__(self, other):
        try:
            inst = inspect(self)
            attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs if c_attr.key != 'id']

            for attr in attr_names:
                if getattr(self, attr) != getattr(other, attr):
                    return False
            return True
        except AttributeError:
            return False


def calculate_eta0hem(eta0b: Q, kd: Q) -> Tuple[Q, str]:
    """
    Calculate hemispherical peak collector efficiency `eta_0hem` from beam peak `eta0b` and diffuse IAM `kd`.

    Parameters
    ----------
    eta0b: beam peak collector efficiency based on QDT test
    kd:  diffuse incidence angle modifier

    Notes
    -----
    This method is based on the QDT-SST conversion formulas in ISO 9806 Annex B.
    Note: This essentially assumes a fixed diffuse irradiance ratio of 15%.

    Returns
    -------
    eta0hem: Quantity, The calculated hemispherical peak collector efficiency
    info: string, information on calculation method used
    """
    eta0hem = eta0b * (0.85 + 0.15 * kd)
    info = ('Collector parameter "eta0hem" (hemispherical peak collector efficiency) is calculated by SunPeek '
            'based on "eta0b" and "Kd" (diffuse incidence angle modifier), '
            'using the formula: eta0hem = eta0b * (0.85 + 0.15 * Kd). ')
    return eta0hem, info


def calculate_eta0b(eta0hem: Q, kd: Q) -> Tuple[Q, str]:
    """
    Calculate beam peak collector efficiency `eta_0b` from hemispheric peak `eta0hem` and diffuse IAM `kd`.

    Parameters
    ----------
    eta0hem: hemispherical peak collector efficiency based on SST test
    kd:  diffuse incidence angle modifier

    Notes
    -----
    This method is based on the SST-QDT conversion formulas in ISO 9806 Annex B.

    Returns
    -------
    eta0hem: Quantity, The calculated hemispherical peak collector efficiency
    info: string, information on calculation method used
    """
    eta0b = eta0hem / (0.85 + 0.15 * kd)
    info = ('Collector parameter "eta0b" (beam peak collector efficiency) is calculated by SunPeek '
            'based on "eta0hem" and "Kd" (diffuse incidence angle modifier), '
            'using the formula: eta0b = eta0hem / (0.85 + 0.15 * Kd). ')
    return eta0b, info


def calculate_kd_Hess_and_Hanby(iam_method: IAM_Method) -> Tuple[Q, str]:
    """
    Calculate collector parameter "Kd" (incidence angle modifier for diffuse radiation) based on "Kb" (IAM for beam).

    Parameters
    ----------
    iam_method : IAM_Method
        Instance based on a _IAM_Method class with a method ``get_iam(aoi, azimuth_diff)`` to calculate the IAM
        (incidence angle modifier) based on the angle of incidence ``aoi`` and the solar azimuth angle.

    Returns
    -------
    kd: Quantity, The calculated diffuse radiation incidence angle modifier.
    info: string. Information on the used calculation method.

    Notes
    -----
    - This method calculates an estimated value of "Kd" by integrating the "eta0b" values
    (incidence angle modifier for beam radiation) over the hemispherical plane.
    - Use results with caution. The used method reported by Hess & Hanby assumes isotropic diffuse radiation.
    This typically underestimates the derived "Kd" values.

    References
    ----------
    S. Hess and V. I. Hanby, “Collector Simulation Model with Dynamic Incidence Angle Modifier for Anisotropic Diffuse
    Irradiance,” Energy Procedia, vol. 48, pp. 87–96, 2014, doi: 10.1016/j.egypro.2014.02.011.
    https://repositorio.lneg.pt/bitstream/10400.9/1063/1/SOLARTHRMAL.pdf
    """

    n_range = 180
    min_angle = 0
    max_angle = 90
    theta_range = np.linspace(min_angle, max_angle, n_range, endpoint=False)
    phi_range = np.linspace(-max_angle, max_angle, n_range, endpoint=False)
    ai_theta = (max_angle - min_angle) / n_range
    ai_phi = 2 * ai_theta

    angles = np.array(np.meshgrid(theta_range, phi_range)).T.reshape(-1, 2)
    theta_angles = angles[:, [0]].flatten() + 0.5 * ai_theta
    theta_angles = Q(theta_angles, 'deg')
    phi_angles = angles[:, [1]].flatten() + 0.5 * ai_phi
    phi_angles = Q(phi_angles, 'deg')

    iam = iam_method.get_iam(aoi=theta_angles, azimuth_diff=phi_angles)

    v = np.sin(np.deg2rad(theta_angles)) * np.cos(np.deg2rad(theta_angles))
    W = v.sum()
    kd = np.multiply(v, iam).sum() / W

    info = ('Collector parameter "Kd" (incidence angle modifier for diffuse radiation) is calculated by SunPeek '
            'based on integration of the values of "eta0b" (beam IAM) over the hemispherical plane '
            '(Hess & Hanby method), as described in doi: 10.1016/j.egypro.2014.02.011')
    return kd, info


class UninitialisedCollector(Collector):
    def __init__(self, collector_name, parent, attribute):
        self.name = collector_name
        self.parent = parent
        self.attribute = attribute
        self.a1 = Q(0, "W m**-2 K**-1")
        self.a2 = Q(0, "W m**-2 K**-2")
        self.a5 = Q(1, "kJ m**-2 K**-1")
        self.gross_length = Q(0, 'm')

