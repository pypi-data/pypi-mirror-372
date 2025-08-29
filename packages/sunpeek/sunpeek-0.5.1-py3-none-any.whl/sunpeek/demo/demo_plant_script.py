"""
This module holds an example to show the functionality of the SunPeek package and the Performance Check method.

The Python code shows how to configure the plant / collector array, call the Performance Check method (ISO 24194) and
produce some plots. 
This script is based on the FHW / Fernheizwerk plant in Graz, Austria.
The data used here (together with a detailed description) is available at https://zenodo.org/record/7741084

.. codeauthor:: Philip Ohnewein <p.ohnewein@aee.at>
.. codeauthor:: Marnoch Hamilton-Jones <m.hamilton-jones@aee.at>
.. codeauthor:: Daniel Tschopp <d.tschopp@aee.at>
"""

import os
import json
import datetime as dt
import pytz

import sunpeek.demo
from sunpeek.data_handling.wrapper import use_csv
from sunpeek.demo.demo_plant import requires_demo_data
from sunpeek.core_methods.pc_method.wrapper import run_performance_check
from sunpeek.core_methods.pc_method.plotting import create_pdf_report
from sunpeek.common.unit_uncertainty import Q
from sunpeek.common import config_parser
from sunpeek.common.utils import DatetimeTemplates
from sunpeek.components import CollectorQDT, CollectorTypes, iam_methods, FluidFactory, CoolPropFluid, Plant
from sunpeek.definitions.fluid_definitions import get_definition, WPDFluids


def get_fluid(fluid_str: str = WPDFluids.fhw_pekasolar.value.name):
    """Return heat transfer fluid: Default is fluid of FHW plant. Choose other fluid to see how they would behave.
    """
    if fluid_str == WPDFluids.fhw_pekasolar.value.name:
        # FHW laboratory-tested fluid, with property models trained from csv files
        return FluidFactory(fluid=get_definition(fluid_str))

    # Examples of CoolProp fluids
    if fluid_str.lower() == 'water':
        return FluidFactory(fluid=get_definition('water'))

    fluid = CoolPropFluid(get_definition(fluid_str), concentration=Q(40, 'percent'))

    if fluid is not None:
        return fluid
    raise ValueError(f'Unknown fluid string "{fluid_str}".')


def get_collector():
    """Return collector definition of flat plate collector used in collector array.
    """
    return CollectorQDT(name="Arcon 3510",
                        manufacturer_name="Arcon-Sunmark A/S",
                        product_name="HTHEATstore 35/10",
                        licence_number='SP SC0843-14',
                        test_report_id="6P02267-C-Rev 1 (2016-07-06), 4P04266-C-Rev 2 (2015-11-10)",
                        certificate_date_issued=dt.datetime(2016, 7, 14),
                        certificate_lab='SP Technical Research Institute of Sweden',
                        collector_type=CollectorTypes.flat_plate.value,
                        description="Cover: single-glazed & foil. Absorber: harp. Hydraulics: Non-Tichelmann",
                        test_reference_area="gross",
                        area_gr=Q(13.57, "m**2"),
                        gross_width=Q(5973, "mm"),
                        gross_length=Q(2272, "mm"),
                        gross_height=Q(145, "mm"),
                        a1=Q(2.067, "W m**-2 K**-1"),
                        a2=Q(0.009, "W m**-2 K**-2"),
                        a5=Q(7.313, "kJ m**-2 K**-1"),
                        a8=Q(0, 'W m**-2 K**-4'),
                        kd=Q(0.93, ""),
                        eta0b=Q(0.745, ""),
                        f_prime=Q(0.95, ""),
                        iam_method=iam_methods.IAM_Interpolated(
                            aoi_reference=Q([10, 20, 30, 40, 50, 60, 70, 80, 90], 'deg'),
                            iam_reference=Q([1, 0.99, 0.97, 0.94, 0.9, 0.82, 0.65, 0.32, 0]))
                        )


def get_demo_plant_nodata() -> Plant:
    """Return configured FHW plant ("demo plant") without data, but with fluid and collector set.

    Returns
    -------
    `plant` : A :class:`physical.Plant` object, the FHW demo plant: https://doi.org/10.5281/zenodo.7741084
    """
    with open(sunpeek.demo.DEMO_CONFIG_PATH) as f:
        conf = json.load(f)
    plant = config_parser.make_full_plant(conf=conf)
    # Define collector type
    plant.arrays[0].collector = get_collector()
    # Define heat transfer fluid
    plant.fluid_solar = get_fluid()
    # This is just to showcase how other fluids would be used:
    # plant.fluid_solar = get_fluid('water')
    # plant.fluid_solar = get_fluid('ASHRAE, Propylene Glycol')
    # plant.fluid_solar = get_fluid('Antifrogen L')

    return plant


if __name__ == '__main__':
    plant = get_demo_plant_nodata()
    # Submit measurement data
    requires_demo_data(None)
    # data = sunpeek.demo.DEMO_DATA_PATH_2DAYS
    data = sunpeek.demo.DEMO_DATA_PATH_1MONTH
    # data = sunpeek.demo.DEMO_DATA_PATH_1YEAR
    data_output = use_csv(plant, csv_files=[data], timezone='utc', datetime_template=DatetimeTemplates.year_month_day)

    # STEP 3: Run Performance Check method & create plots
    # Use default settings:
    pc_output = run_performance_check(plant).output
    # or try specific settings:
    # pc_output = run_performance_check(plant,
    #                                   method=['extended'],
    #                                   formula=[2],
    #                                   safety_uncertainty=0.9,
    #                                   ).output

    # Create pdf report
    report_path = create_pdf_report(pc_output)
    # Include all hourly-interval plots -> may be slow!
    # report_path = create_pdf(pc_output, include_interval_plots=True)
    # Optionally, open file
    # os.startfile(report_path)
