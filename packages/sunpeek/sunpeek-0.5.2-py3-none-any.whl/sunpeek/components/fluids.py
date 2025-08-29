"""
Caveat: This docstring is outdated.

Summary
-------
This module implements fluids and fluid properties for HarvestIT.

Extended Summary
----------------
A typical calculation involving fluid properties is getting thermal
power when only volume flow and inlet & outlet temperatures are given; this requires knowledge about the fluid
density and heat capacity at given temperatures.
Pressure-dependence of these properties is negligible for practicale purposes and is thus neglected in HarvestIT.

The main superclass is Fluid which provides the two main methods for accessing fluid properties at given temperatures,
namely :meth:`Fluid.get_density()` and :meth:`Fluid.get_heat_capacity()`. Both accept temperature as a scalar or
vector pint Quantity.

**Main classes:** There are two options for using fluids:

1. Class :class:`CoolPropFluid`: An interface to the well-known CoolProp database. This gives access to fluid
properties of all CoolProp
incompressible fluids listed under `CoolProp Incompressibles`_. This includes some general fluids (such as "Propylene
Glycol") and some specific products (such as "Antifrogen L, Propylene Glycol").

2. Class :class:`WPDFluid`: An interface to fluids for which only graphical property information is given. This is a
common case in solar thermal when the only piece of information given for a heat transfer fluid is a data sheet with some
plots. The workflow in this case involves a tool called `WebPlotDigitizer`_ and is described in more detail below.


CoolProp fluids
---------------

CoolProp fluids are implemented in the class :class:`CoolPropFluid` which gives access to fluid properties of all CoolProp
incompressible fluids listed under `CoolProp Incompressibles`_. :class:`CoolPropFluid`  subclasses :class:`Fluid`
and thus gives high level access to properties via `getDensity()` and `getHeatCapacity()`.
Since all fluids in this class are incompressibles, the exact pressure has a minor influence on CoolProps results.
For simplicity, pressure is set to a constant, `P_DEFAULT`.

**Fluids:** The fluids include water, 60 pure fluids and 73 mixed fluids (as of 2022). Water properties follow the
formulation in `IAPWS-95`_, implemented in CoolProps HEOS::water backend.
The mixed fluids are binary mixtures (water + some substance and require a concentration. Depending on the substance,
the concentration is interpreted as mass concentration (`mass-based binary mixtures`_) or volume concentration (
`volume-based binary mixtures`_).


WPD fluids
----------

This module supports

- reading & interpolating csv data created with WebPlotDigitizer.
- training sklearn models for interpolation / fitting, and visual checks of fit quality.
# - exporting the trained models as ONNX files (to be stored in database).
# - calculating fluid properties by using prediction based on ONNX model.
- building WPDFluid instances from these ONNX files.

Here is a step-by-step guide on how to add a fluid to HarvestIT for which only graphical information about fluid
properties is given (see #73).
An example is the FHW plant. Example workflows can be found under `tests/tests_fluids`.

To enable property calculation for WPD fluids, follow this process:

1. Use WebPlotDigitizer, an open source tool, to convert graphical information to numeric data.

    - You may use the web version of [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) or download the desktop version.
    - To get started, read the [tutorial](https://automeris.io/WebPlotDigitizer/tutorial.html) or watch a youtube
    tutorial like [this one](https://www.youtube.com/watch?v=P7GbGdMvopU) or
    [this one](https://www.youtube.com/watch?v=Mv5nqAPCKA4).
    - If graphical information is for multiple concentrations (like in the example image in this issue),
    create multiple datasets in WebPlotDigitizer, with each dataset named like the concentration: e.g. dataset name 20 for
    the 20% concentration curve.
    - Repeat the plot digitization for both density and heat capacity. Export the data to csv, using the default
    settings. Generate files ```density.csv``` and ```heat_capacity.csv```

2. In Python / HarvestIT, create models for density and heat capacity using this code (or see
```tests/tests_fluids/test_wpd.py```).

    - Create a dictionary ```unit``` specifying the units used in the fluid property image: inputs (temperature
    ```te``` and concentration ```c```) and output (density or heat capacity):
```
import fluids.wpd as wpd
unit = {'density': {'te': 'degC', 'out': 'kg m**-3'}, 'heat_capacity': {'te': 'degC', 'out': 'J g**-1 K**-1'}}
# Or if fluid has concentration as input:
unit = {'density': {'te': 'degC', 'c': 'percent', 'out': 'kg m**-3'}, 'heat_capacity': {'te': 'degC', 'c': 'percent', 'out': 'J g**-1 K**-1'}}
# Train the models:
rho_model = wpd.ModelFactory(unit=unit['density']).train("density.csv")
cp_model = wpd.ModelFactory(unit=unit['heat_capacity']).train("heat_capacity.csv")
# Create fluid:
fluid = wpd.FluidFactory(concentration=concentration, density_model=rho_model, heat_capacity_model=cp_model)
```

3. Commit the trained fluid to the SunPeek database:
```
import common.utils as utils
with utils.S() as session:
    session.add(fluid)
    session.commit(fluid)
```

This implementation holds a ModelFactory used to generate a WPDModel. There are 2 subclasses of WPDModel:
- :class:`WPDModelPure`, for fluids that do _not_ have a concentration attached (e.g. measured at fixed concentration).
Here, the interpolation / fit is temperature vs. target value (density or heat capacity).
- :class:`WPDModelMixed`, for fluids that have variable concentration (e.g. variable concentration properties available
from data sheet). Here, the interpolation / fit is temperature and concentration vs. target value. This assumes that each
concentration curve has been treated as a separate dataset in WebPlotDigitizer, with the concentration
curve named after the concentration value, e.g. "50" for concentration 50%.

Sources
-------

.. _WebPlotDigitizer:
    https://automeris.io/WebPlotDigitizer/
.. _CoolProp Incompressibles:
    http://www.coolprop.org/fluid_properties/Incompressibles.html
.. _mass-based binary mixtures:
    http://www.coolprop.org/fluid_properties/Incompressibles.html#id180
.. _volume-based binary mixtures:
    http://www.coolprop.org/fluid_properties/Incompressibles.html#id181
.. _IAPWS-95:
    http://www.iapws.org/relguide/IAPWS-95.html

"""

import numpy as np
import pandas as pd
import warnings
import sqlalchemy
import CoolProp.CoolProp as Cp
from sqlalchemy import Column, String, Integer, ForeignKey, Float, Boolean, Enum, Identity, or_, \
    CheckConstraint, JSON, func
from sqlalchemy.orm import relationship, declared_attr
import sqlalchemy.event
from typing import Union

from sunpeek.common.unit_uncertainty import Q
from sunpeek.common.utils import sp_logger
from sunpeek.common.errors import ConfigurationError
import sunpeek.common.unit_uncertainty as uu
from sunpeek.components.helpers import ORMBase, AttrSetterMixin
from sunpeek.components.fluids_wpd_models import WPDModel, WPDModelPure, ModelFactory
from sunpeek.definitions import FluidProps


class FluidDefinition(ORMBase, AttrSetterMixin):
    """Fluid with all information to store in database.

    Attributes
    ----------
    name : str
        Fluid name / Product name. Must be unique within SunPeek. Example: "Thermum P"
    manufacturer : str
        Manufacturer name. Example: "Thermum GmbH & Co. KG"
    """
    __tablename__ = 'fluid_definitions'

    id = Column(Integer, Identity(0), primary_key=True)
    model_type = Column(Enum('CoolProp', 'WPD', name='fluid_definition_type'))
    name = Column(String, nullable=False, unique=True)
    manufacturer = Column(String)
    description = Column(String)
    is_pure = Column(Boolean)

    _density_data = Column(JSON)
    _heat_capacity_data = Column(JSON)

    __mapper_args__ = {
        'polymorphic_identity': 'fluid_def',
        'polymorphic_on': model_type,
        'with_polymorphic': '*'
    }

    def __init__(self, fluid_string=None, **kwargs):
        warnings.warn(
            f'This returns a generic fluid definition. You probably wanted FluidDefinition.get_definition({fluid_string})'
            ' to locate a fluid definition in the database')
        self.name = fluid_string
        try:
            super().__init__(**kwargs)
        except TypeError as e:
            if "'concentration' is an invalid keyword" in str(e):
                raise TypeError("FluidDefinitions cannot have a concentration. You probably want to create a concrete "
                                "fluid with a definition attached: Fluid(fluid=FluidDefinition(**kwargs), "
                                "concentration=<value>, or Fluid(fluid=FluidDefinition(**kwargs), "
                                "FluidDefinition.get_definition(fluid_string, bd_session), concentration=<value>")

    @classmethod
    def get_definition(cls, fluid_string, session):
        """Tries to find a match for fluid_string among fluids definitions. Compares lower case and neglecting whitespaces.
        Checks against name and description.

        Parameters
        ----------
        fluid_string : str
            User-supplied string that must uniquely define a fluid within the CoolProp incompressible fluids,
            or predefined wpd_fluids.
            See `CoolProp Incompressibles`_.
        session: sqlalchemy.orm.session.Session
            An active database session object

        Returns
        -------
        A CoolpropFluidDefinition or WPDFluidDefinition object if a unique match for `fluid string` is found in the `fluid_definitions` table

        Raises
        ------
        ValueError
            If no or more than one fluid is found.

        """
        if fluid_string.lower() == 'water':
            fluid = session.query(cls).filter(cls.name == 'water').one()
            return fluid
        if fluid_string.isupper() and len(fluid_string) <= 8:
            try:
                search_string = fluid_string.lower()
                fluid = session.query(cls).filter(cls.name == search_string).one()
                return fluid
            except (sqlalchemy.exc.NoResultFound, sqlalchemy.exc.MultipleResultsFound):
                pass
        try:
            # search_string = re.sub('[\W_]+', '', fluid_string)
            search_string = fluid_string.replace(' ', '')
            fluid = session.query(cls).filter(or_(
                func.replace(func.lower(cls.name), ' ', '').ilike('%{}%'.format(search_string.lower())),
                func.replace(func.lower(cls.description), ' ', '').ilike('%{}%'.format(search_string.lower()))
            )).one()
        except sqlalchemy.exc.NoResultFound:
            raise ConfigurationError(f'No entry found for {fluid_string}')
        except sqlalchemy.exc.MultipleResultsFound:
            raise ConfigurationError(f'{fluid_string} is not unique, more than 1 result found.')

        return fluid

    @property
    def density_data(self):
        return pd.read_json(self._density_data)

    @density_data.setter
    def density_data(self, val):
        self._density_data = val.to_json()

    @property
    def heat_capacity_data(self):
        return pd.read_json(self._heat_capacity_data)

    @heat_capacity_data.setter
    def heat_capacity_data(self, val):
        self._heat_capacity_data = val.to_json()


class CoolPropFluidDefinition(FluidDefinition):
    __mapper_args__ = {
        'polymorphic_identity': 'CoolProp',
    }


class WPDFluidDefinition(FluidDefinition):
    """
    Definitions of WPD fluids, for reuse by WPDFluid subclasses

    Notes
    -----
    - To add to the database:
    ```
    import onnx
    dens = onnx.load('E:/HarvestIT/tests/resources/fluids/FHW, Pekasolar/Pekasolar, pdf export, density.onnx')
    hc = onnx.load('E:/HarvestIT/tests/resources/fluids/FHW, Pekasolar/Pekasolar, pdf export, heat capacity.onnx')
    dens_m = fluids.wpd.ModelFactory(unit, onnx_model=dens)
    hc_m = fluids.wpd.ModelFactory(unit, onnx_model=hc)
    definition= WPDFluidDefinition(unique_name, dens_m, hc_m, manufacturer=, datasheet_info)
    with Session(module_engine) as session:
        session.add(definition)
        session.commit()
    ```
    """

    __mapper_args__ = {
        'polymorphic_identity': 'WPD',
    }

    dm_model_sha1 = Column(String)
    hc_model_sha1 = Column(String)
    heat_capacity_unit_te = Column(String)
    heat_capacity_unit_out = Column(String)
    heat_capacity_unit_c = Column(String)
    density_unit_te = Column(String)
    density_unit_out = Column(String)
    density_unit_c = Column(String)

    FluidDefinition.__table_args__ = (
        sqlalchemy.UniqueConstraint('dm_model_sha1', 'hc_model_sha1'),  # Constriant for WPDFluids
    )

    @classmethod
    def from_fluid_info(cls, fluid_info: 'sunpeek.definitions.fluid_definitions.WPDFluidInfo'):
        rho_model = ModelFactory.from_info_and_property(fluid_info, FluidProps.density)
        cp_model = ModelFactory.from_info_and_property(fluid_info, FluidProps.heat_capacity)

        return WPDFluidDefinition(fluid_info.name,
                                  density_model=rho_model,
                                  heat_capacity_model=cp_model,
                                  manufacturer=fluid_info.manufacturer,
                                  description=fluid_info.description)

    def __init__(self, name: str, density_model: WPDModel, heat_capacity_model: WPDModel,
                 manufacturer=None, description=None):
        assert density_model.__class__.__name__ == heat_capacity_model.__class__.__name__, \
            'Inputs "density_model" and "heat_capacity_model" must be of same type (pure or mixed WPD models).'

        self.name = name
        self.manufacturer = manufacturer
        self.description = description

        self.density_model = density_model
        self.density_data = density_model.df

        self.heat_capacity_model = heat_capacity_model
        self.heat_capacity_data = heat_capacity_model.df

        self.heat_capacity_unit_te = self.heat_capacity_model.unit['te']
        self.heat_capacity_unit_out = self.heat_capacity_model.unit['out']
        self.heat_capacity_unit_c = self.heat_capacity_model.unit.get('c')
        self.density_unit_te = self.density_model.unit['te']
        self.density_unit_out = self.density_model.unit['out']
        self.density_unit_c = self.density_model.unit.get('c')

        self.is_pure = isinstance(density_model, WPDModelPure)

    @sqlalchemy.orm.reconstructor
    def _init_on_load(self):
        units_hc = {'te': self.heat_capacity_unit_te,
                    'out': self.heat_capacity_unit_out}
        if self.heat_capacity_unit_c is not None:
            units_hc['c'] = self.heat_capacity_unit_c

        units_d = {'te': self.density_unit_te,
                   'out': self.density_unit_out}
        if self.density_unit_c is not None:
            units_d['c'] = self.density_unit_c

        self.density_model = ModelFactory(units_d, is_pure=self.is_pure, df=self.density_data)
        self.heat_capacity_model = ModelFactory(units_hc, is_pure=self.is_pure, df=self.heat_capacity_data)


class FluidFactory:
    def __new__(cls, **kwargs):
        if kwargs.get('fluid') is None:
            warnings.warn(
                'This returns a generic fluid. You probably wanted FluidFactory(fluid=<fluid definition object>'
                'attaching a fluid definition allows for a return of a concrete Fluid subtype')
            return Fluid(**kwargs)

        if isinstance(kwargs['fluid'], CoolPropFluidDefinition):
            return CoolPropFluid(**kwargs)

        if isinstance(kwargs['fluid'], WPDFluidDefinition):
            if kwargs['fluid'].is_pure:
                if kwargs.pop('concentration', None) is not None:
                    warnings.warn('You passed a "concentration" kwargs to a pure fluid (WPDFluidPure). '
                                  'I will gracefully ignore the concentration.')
                return WPDFluidPure(**kwargs)

            return WPDFluidMixed(**kwargs)

        elif isinstance(kwargs['fluid'], str):
            return UninitialisedFluid(kwargs.pop('fluid'), kwargs)


class Fluid(ORMBase):
    """
    Stores basic information about fluids in SunPeek and a high level, and implements a high level abstract fluid
    interface for SunPeek.

    Notes
    -----
    - Provides get_density() and get_heat_capacity() accessors for all fluids, accepting scalar or vector pint Quantity
    as temperature input.
    - Subclasses must implement _get_density() and _get_heat_capacity().
    - Forms the base class for a joined table class hierarchy in the database,
    see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    the polymorphic discriminator column is `model_type`, this parameter is set automatically, do not alter by hand.

    .. _CoolProp:
        http://www.coolprop.org/fluid_properties/Incompressibles.html#mixture-examples
    """
    __tablename__ = 'fluids'

    id = Column(Integer, Identity(0), primary_key=True)
    fluid_definition_id = Column(ForeignKey(WPDFluidDefinition.id))
    model_type = Column(Enum('CoolProp', 'WPD', 'WPDPure', 'WPDMixed', name='fluid_model_type'))
    fluid = relationship("FluidDefinition", foreign_keys=[fluid_definition_id])
    plant_id = Column(ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", foreign_keys=[plant_id], uselist=False)

    DENSITY_DEFAULT_UNIT = 'kg m**-3'
    HEAT_CAPACITY_DEFAULT_UNIT = 'J kg**-1 K**-1'

    __mapper_args__ = {
        'polymorphic_identity': 'fluid',
        'polymorphic_on': model_type,
        'with_polymorphic': '*'
    }

    __table_args__ = (
        CheckConstraint('_concentration between 0 and 1', name='concentration_check'),
    )

    def _get_density(self, te):
        raise NotImplementedError()

    def _get_heat_capacity(self, te):
        raise NotImplementedError()

    def get_density(self, te):
        """Calculate density of fluid at given temperature and self.concentration
        Parameters
        ----------
        te : pd.Series
            Temperature for which density is evaluated.

        Returns
        -------
        pd.Series
        """
        rho = self._get_density(te)
        rho.index = te.index
        return rho.pint.to(self.DENSITY_DEFAULT_UNIT)

    def get_heat_capacity(self, te):
        """Calculate heat capacity of fluid at given temperature and self.concentration
        Parameters
        ----------
        te : pd.Series, scalar or vector
            Temperature for which heat cpaacity is evaluated.

        Returns
        -------
        pd.Series
        """
        cp = self._get_heat_capacity(te)
        cp.index = te.index
        return cp.pint.to(self.HEAT_CAPACITY_DEFAULT_UNIT)

    @property
    def name(self):
        return self.fluid.name


class UninitialisedFluid(Fluid):
    __mapper_args__ = {
        'polymorphic_identity': 'Uninitialised',
    }

    def __init__(self, fluid_def_name, stored_args):
        self.fluid_def_name = fluid_def_name
        self.stored_args = stored_args


# def assert_valid_fluid(fluid: Fluid):
#     assert fluid is not None
#     assert not isinstance(fluid, UninitialisedFluid)


class CoolPropFluid(Fluid):
    """High level class for interface with CoolProp incompressible fluids.

    Input and output units to CoolProp are standardized and thus don't need to be specified.

    Attributes
    ----------
    fluid : CoolPropFluidDefinition
        User-supplied string that must uniquely define a fluid within the CoolProp incompressible fluids.
        See `CoolProp Incompressibles`_.
    concentration : Quantity or dict
        If fluid does not require concentration, leave at default None.
        `concentration` is interpreted as mass concentration for `mass-based binary mixtures`_.
        `concentration` is interpreted as volume concentration for `volume-based binary mixtures`_.

    Raises
    ------
    ValueError, TypeError
        If concentration is given for pure fluid or missing for mixed fluid, or concentration is wrong Quantity.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'CoolProp',
    }

    @declared_attr
    def _concentration(cls):
        """concentration column, shared with WPDMixedFluid class"""
        return Fluid.__table__.c.get('_concentration', Column(Float))

    # Default pressure (in Pa) that is passed to CoolProp. See note in module docstring.
    P_DEFAULT = 101325

    def __init__(self, fluid: CoolPropFluidDefinition = None, concentration: Union[Q, dict] = None):
        if fluid is not None:
            self.fluid = fluid

            if self.fluid.is_pure:
                if concentration is not None:
                    raise ValueError('Non-None concentration was given for a pure fluid.')
            else:
                if concentration is None:
                    raise ValueError('None concentration was given a for a non-pure fluid.')
                self.concentration = concentration

    @property
    def concentration(self):
        if not self.fluid.is_pure:
            return Q(self._concentration, 'dimensionless').to('percent')
        else:
            return None

    @concentration.setter
    def concentration(self, val):
        val = uu.parse_quantity(val)
        self._concentration = val.m_as('dimensionless')

    @property
    def query_str(self):
        """String to be sent to CoolProp backend, adds concentration to self.coolprop_fluid, if necessary.
        Return
        ------
        str
        """
        if self.fluid.name == 'water':
            return 'HEOS::water'
        query_str = 'INCOMP::' + self.fluid.name
        if self.concentration is not None:
            query_str = f"{query_str}[{self.concentration.to('').m}]"
        return query_str

    def _get_density(self, te):
        val = self._get_coolprop('density', te)
        return uu.to_s(val.flatten().astype('float64'), 'kg m**-3')

    def _get_heat_capacity(self, te):
        val = self._get_coolprop('heat capacity', te)
        return uu.to_s(val.flatten().astype('float64'), 'J kg**-1 K**-1')

    def _get_coolprop(self, prop, te):
        """Return density or heat capacity, with common error handling / CoolProp allowed temperature ranges.
        """
        coolprop_prop = "D" if prop == "density" else "C"
        try:
            val = Cp.PropsSI(coolprop_prop, "P", self.P_DEFAULT, "T", uu.to_numpy(te, 'K'), self.query_str)
            # If some (but not all) temperatures exceed the allowed fluid temperature range, they are returned as Inf.
            # Convert to NaN so all downstream methods can keep relying that everything is either ok or np.nan
            sp_logger.warn(f'CoolProp returned Inf results in {prop} calculation of fluid "{self.query_str}". '
                           f'This is probably because some of the given temperatures exceed the allowed '
                           f'temperature range. '
                           f'For more details, see http://www.coolprop.org/fluid_properties/Incompressibles.html')
        except ValueError:
            # This happens if all temperatures passed to CoolProp exceed the allowed fluid temperature range.
            # For allowed fluid temperatures, see http://www.coolprop.org/fluid_properties/Incompressibles.html
            val = np.full(len(te), np.inf)
            sp_logger.warn(f'CoolProp raised ValueError in {prop} calculation of fluid "{self.query_str}". '
                           f'This is probably because all given temperatures exceed the allowed temperature range. '
                           f'For more details, see http://www.coolprop.org/fluid_properties/Incompressibles.html '
                           f'All {prop} values have been set to Inf.')

        return val


class WPDFluid(Fluid):
    """
    Fluid with given trained sklearn models for density and heat capacity.
    Accepts pint Quantity for temperature and (optionally) concentration. Returns fluid properties as pint Quantity.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'WPD',
    }

    @property
    def density_model(self):
        return self.fluid.density_model

    @property
    def heat_capacity_model(self):
        return self.fluid.heat_capacity_model

    def _get_density(self, te):
        return self._get_property(self.density_model, te)

    def _get_heat_capacity(self, te):
        return self._get_property(self.heat_capacity_model, te)

    def _get_property(self, model, te):
        raise NotImplementedError()


class WPDFluidPure(WPDFluid, ORMBase):
    """WPDFluid subclass for fluids that do not have a variable concentration, so they are either pure fluids or have
    a fixed concentration.

    Attributes
    ----------
    density_model, heat_capacity_model : WPDModel
        Trained WPDModel objects for density and heat capacity.
    """

    __mapper_args__ = {
        'polymorphic_identity': 'WPDPure',
    }

    def _get_property(self, model, te):
        """Return model property (density, heat capacity). Accepts & returns pd.Series with dtype pint unit."""
        te_ = te.pint.m_as(model.unit['te'])
        output = model.predict(te_)
        return uu.to_s(output.astype('float64'), model.unit['out'])


class WPDFluidMixed(WPDFluid, ORMBase):
    """WPDFluid subclass for fluids that do have a variable concentration, either mass or volume concentration.
    Attributes
    ----------
    concentration : Quantity or dict
        Scalar concentration value of fluid
    density_model, heat_capacity_model : WPDModel
        Trained WPDModel objects for density and heat capacity
    """

    __mapper_args__ = {
        'polymorphic_identity': 'WPDMixed',
    }

    @declared_attr
    def _concentration(cls):
        """Concentration column, shared with WPDMixedFluid class.
        """
        return Fluid.__table__.c.get('_concentration', Column(Integer))

    def __init__(self, concentration: Union[Q, dict], **kwargs):
        self.concentration = concentration
        super().__init__(**kwargs)

    @property
    def concentration(self):
        return Q(self._concentration, 'dimensionless').to('percent')

    @concentration.setter
    def concentration(self, val):
        val = uu.parse_quantity(val)
        self._concentration = val.m_as('dimensionless')

    def _get_property(self, model, te):
        te_ = te.pint.m_as(model.unit['te'])
        c_ = self.concentration.m_as(model.unit['c'])
        output = model.predict(te_, c_)

        return uu.to_s(output, model.unit['out'])


