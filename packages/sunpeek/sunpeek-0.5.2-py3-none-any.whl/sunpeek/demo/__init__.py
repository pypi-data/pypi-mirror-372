try:
    import sunpeek_exampledata

    DEMO_DATA_AVAILABLE = True

    DEMO_CONFIG_PATH = sunpeek_exampledata.DEMO_CONFIG_PATH

    DEMO_DATA_PATH_2DAYS = sunpeek_exampledata.DEMO_DATA_PATH_2DAYS
    DEMO_DATA_PATH_1MONTH = sunpeek_exampledata.DEMO_DATA_PATH_1MONTH
    DEMO_DATA_PATH_1YEAR = sunpeek_exampledata.DEMO_DATA_PATH_1YEAR

    DEMO_FLUID_RHO_PATH = sunpeek_exampledata.DEMO_FLUID_RHO_PATH
    DEMO_FLUID_CP_PATH = sunpeek_exampledata.DEMO_FLUID_CP_PATH

except ModuleNotFoundError:
    DEMO_DATA_AVAILABLE = False
