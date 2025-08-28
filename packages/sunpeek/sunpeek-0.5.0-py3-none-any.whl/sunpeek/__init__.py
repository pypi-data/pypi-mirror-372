import os
from pathlib import Path
import tomllib
import importlib.metadata
import pandas as pd


try:
    __version__ = importlib.metadata.version('sunpeek')
except importlib.metadata.PackageNotFoundError:
    try:
        with open(Path(__file__).parent.with_name('pyproject.toml'), 'rb') as f:
            t = tomllib.load(f)
        __version__ = t['tool']['poetry']['version']
    except FileNotFoundError:    # Package is in a context where pyproject not available (e.g. pip installed)
        __version__ = os.environ['SUNPEEK_VERSION']

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 500)
pd.set_option('plotting.backend', 'matplotlib')

