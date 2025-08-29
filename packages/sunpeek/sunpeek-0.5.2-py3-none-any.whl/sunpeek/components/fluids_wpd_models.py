from typing import Union, Optional
from pathlib import Path
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
import numbers

import matplotlib
from matplotlib.offsetbox import VPacker
from matplotlib.figure import Figure
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import GridSearchCV, ShuffleSplit
from sunpeek.definitions import FluidProps, fluid_data_dir
import sunpeek.common.plot_utils as pu
from sunpeek.common.unit_uncertainty import units


class ModelFactory:

    @classmethod
    def from_info_and_property(cls, fluid_info: 'sunpeek.definitions.fluid_definitions.WPDFluidInfo', prop: FluidProps):
        fn = fluid_data_dir / fluid_info.name / prop.value
        csv_file = fn.with_suffix('.csv')

        unit = fluid_info.unit_density if prop == FluidProps.density else fluid_info.unit_heat_capacity

        return ModelFactory(unit=unit,
                            is_pure=fluid_info.is_pure,
                            csv_file=csv_file)

    def __new__(cls, unit: dict = None,
                is_pure: bool = None,
                csv_file: Union[str, Path] = None,
                df: pd.DataFrame = None):
        """Returns an instance of a trained WPDModel.

        Returns a pure fluid model (WPDModelPure) if unit has only 2 entries (output, temperature),
        otherwise if unit has 3 entries (output, temperature, concentration) a mixed fluid model (WPDFluidMixed).
        This method also trains the model (= fits a sklearn model), based on the given df or csv_file.

        Parameters
        ----------
        unit : dict
            Units for inputs and outputs of the fluid model.
            Must have keys 'te' and 'out', optionally 'c' (then a WPDModelMixed is returned).
            Values must be valid pint unit strings.
        is_pure : bool
            True if unit
        csv_file : str, Path
            Data file used to train the model. Usually, this is a WebPlotDigitizer export csv file.
            Is expected to have multiple datasets, one for each concentration level.
        df: pd.DataFrame
            Is used to train the model.

        Raises
        ------
        TypeError
            If unit is not a dict.
        KeyError
            If required keys 'te' and 'out' are not found, or dictionary has extra keys not 'te', 'c' or 'out'.
        """

        model = WPDModelPure(unit) if is_pure else WPDModelMixed(unit)

        # Make sure either df or csv_file is given
        has_df = df is not None
        has_file = csv_file is not None
        if not (has_df ^ has_file):
            raise ValueError(
                'Model training accepts either a raw data file or a DataFrame. None or both of them were given.')

        # Train model
        model.df = df if has_df else model.csv2df(csv_file)
        model.sk_model = model.train()

        return model


class WPDModel(ABC):
    """
    Model for a particular property of a fluid, e.g. for density or for heat capacity.
    # Has an ONNX filename and the units for all inputs (temperature, optionally concentration) and the calculated output.
    Has the units for all inputs (temperature, optionally concentration) and the calculated output.
    Can read WebPlotDigitizer csv files, train sklearn fit, save trained model as ONNX file and make predictions.
    Attributes
    ----------
    unit : dict
        Units for temperature ['te'], optionally concentration ['c'] and (mandatory) output property ['out'].
        Must be valid pint unit strings. These units are sent to the trained model if a prediction is required,
        and the prediction output is interpreted in unit['out'].
    """

    n_inputs = None
    predictor_cols_in = []
    predictor_col_out = 'out'

    def __init__(self, unit):
        if len(unit) != 1 + self.n_inputs:
            raise ValueError(f'Unit dictionary of fluid definition must have length {self.n_inputs}, '
                             f'the units for output (e.g. density), temperature, and concentration (for mixed fluids).')

        expected_cols = set(['out'] + self.predictor_cols_in)
        if set(unit.keys()) != expected_cols:
            raise KeyError(f'Missing or mismatched keys in unit dictionary. Required keys: {", ".join(expected_cols)}.')

        self.unit = unit
        self.df = None
        self.sk_model = None

    def train(self, fit_type: str = 'polynomial'):
        """Fits polynomial interpolation model to fluid raw data in df.

        Parameters
        ----------
        fit_type : str
            Type of sklearn fit. Currently, only 'polynomial' implemented, works good enough.

        Returns
        -------
        Trained sklearn model.
        """
        if fit_type == 'polynomial':
            # Polynomial interpolation with grid-search cross-validation of interpolation coefficients.
            # Inspired by https://stackoverflow.com/questions/47442102/how-to-find-the-best-degree-of-polynomials
            degree_range = np.arange(2, 4)  # quadratic or cubic polynomials
            pipe = make_pipeline(StandardScaler(), PolynomialFeatures(), Ridge(alpha=1e-3))
            param_grid = {'polynomialfeatures__degree': degree_range}
            # grid = GridSearchCV(pipe, param_grid, cv=20)
            # grid = GridSearchCV(pipe, param_grid, cv=20, scoring='neg_mean_absolute_error')
            # grid = GridSearchCV(pipe, param_grid, cv=LeaveOneOut(), scoring='neg_mean_absolute_error')
            grid = GridSearchCV(pipe, param_grid, cv=ShuffleSplit(n_splits=10), scoring='neg_mean_absolute_error')

        # elif fit_type == 'spline':
        # # SplineTransformer not supported in ONNX conversion
        # Spline & ridge regression: Would be an interesting option, but currently not convertible to onnx.
        # https://scikit-learn.org/stable/auto_examples/linear_model/plot_polynomial_interpolation.html#sphx-glr-auto-examples-linear-model-plot-polynomial-interpolation-py
        # pipeline example: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.SplineTransformer.html#sklearn.preprocessing.SplineTransformer
        # pipe = make_pipeline(SplineTransformer(degree=3), Ridge(alpha=1e-3))
        # param_grid = {'splinetransformer__n_knots': np.arange(4,10)}
        # # grid = GridSearchCV(pipe, param_grid, cv=20)
        # # grid = GridSearchCV(pipe, param_grid, cv=20, scoring='neg_mean_absolute_error')
        # # grid = GridSearchCV(pipe, param_grid, cv=LeaveOneOut(), scoring='neg_mean_absolute_error')
        # grid = GridSearchCV(pipe, param_grid, cv=ShuffleSplit(n_splits=10), scoring='neg_mean_absolute_error')

        else:
            raise ValueError(f'Unknown "fit_type": {fit_type}.')

        # X = self.df[['te', 'c']].to_numpy()
        # X = self.get_predictors_in().to_numpy()
        # y = self.df['out'].to_numpy()
        # grid.fit(X, y)
        # grid.fit(self.get_predictors_in, self.get_predictors_out)

        X = self.df[self.predictor_cols_in]
        y = self.df[self.predictor_col_out]
        grid.fit(X, y)
        model = grid.best_estimator_

        return model

        # reg = model.named_steps['linearregression']
        # reg.get_params()
        # coefs = reg.coef_
        # intercept = reg.intercept_

    @staticmethod
    def _preprocess_prediction_inputs(*args):
        """Args can be a) only temperature, or b) temperature and concentration.
        If concentration is given as a scalar -> gracefully expand to match temperature dimension.
        Returns temperature or tuple temperature, concentration.
        """

        if len(args) == 1:
            # only temperature given (pure fluid)
            return args,

        # Temperature and concentration given (mixed fluid)
        temperature = args[0]
        concentration_ = args[1]
        if concentration_ is None:
            return temperature

        scalar_concentration = isinstance(concentration_, numbers.Number)
        if scalar_concentration:
            concentration = np.full_like(temperature, concentration_)
        else:
            concentration = concentration_
            if len(temperature) != len(concentration):
                raise ValueError('Dimension mismatch among the given inputs "temperature" and "concentration".')

        return temperature, concentration

    def predict(self, *args):
        """Compute model prediction (fluid density, heat capacity) based on trained sklearn model, self.sk_model.

        Parameters
        ----------
        args : pint Quantity
            Inputs required for prediciton: temperature and (for mixed fluids) concentration.
            Fluid temperature in unit self.unit['te'], typically 'degC'
            Fluid concentration in unit self.unit['c'], typically 'percent'

        Returns
        -------
        pint Quantity : Calculated fluid property (density or heat capacity) in unit self.unit['out']
        """
        inputs = self._preprocess_prediction_inputs(*args)
        X = np.array(inputs).transpose().reshape(-1, self.n_inputs)
        nan_inputs = np.isnan(X).any(axis=1)

        out = np.full(nan_inputs.shape, np.nan)
        out[~nan_inputs] = self.sk_model.predict(X[~nan_inputs].reshape(-1, self.n_inputs))

        return out.flatten()

    @abstractmethod
    def csv2df(self, csv_file):
        raise NotImplementedError()


class WPDModelPure(WPDModel):
    n_inputs = 1
    predictor_cols_in = ['te']

    def csv2df(self, csv_file):
        """Read WebPlotDigitizer csv with single dataset into dataframe.
        """
        df = pd.read_csv(csv_file, header=0, sep=',')
        df = df.rename(columns={'X': 'te', 'Y': 'out'})

        return df

    def plot_fit(self,
                 prop_to_plot: FluidProps,
                 fluid_name: str,
                 settings: Optional[pu.PlotSettings] = None,
                 n_points: Optional[int] = 50,
                 ) -> Figure:
        # ) -> Optional[pu.PlotResult]:
        """Plot model fit and original / ground truth data from the WebPlotDigitizer csv dataset.
        This is useful to check quality of model fit, after calling self.train().
        """
        if prop_to_plot is None or prop_to_plot not in list(FluidProps):
            raise ValueError(f'Invalid "prop_to_plot": {prop_to_plot}')

        if settings is None:
            settings = pu.PlotSettings()

        # Data to plot
        te = np.linspace(self.df['te'].min() - 20, self.df['te'].max() + 20, n_points)
        out = self.predict(te)

        if prop_to_plot == 'density':
            title_str = 'Fluid Density'
            y_label = 'Density'
            legend_loc = 'upper right'
        else:
            title_str = 'Fluid Heat Capacity'
            y_label = 'Heat Capacity'
            legend_loc = 'lower right'

        # Plot Title
        fig, params = pu.prepare_figure(settings=settings)
        box = VPacker(children=[pu.box_title(f'{title_str} of fluid "{fluid_name}"'),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Data plot
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_huge, bottom=0.45)
        ax = fig.add_axes(rect)

        ax.plot(te, out, '-', label='Model prediction', zorder=2.5)
        # Measured values as scatter
        ax.scatter(self.df['te'], self.df['out'],
                   s=pu.DEFAULTS.marker_size_scatter,
                   alpha=pu.DEFAULTS.marker_alpha,
                   facecolors=pu.DEFAULTS.marker_facecolor,
                   edgecolors=pu.DEFAULTS.marker_edgecolor,
                   zorder=2.6,
                   label='WebPlotDigitizer measurements',
                   )

        ax.set_xlabel(f'Temperature [{units(self.unit["te"]).units:~P}]')
        ax.set_ylabel(f'{y_label} [{units(self.unit["out"]).units:~P}]')
        ax.grid()
        ax.set_axisbelow('line')
        ax.legend(loc=legend_loc).set_zorder(3)

        return fig


class WPDModelMixed(WPDModel):
    n_inputs = 2
    predictor_cols_in = ['te', 'c']

    def csv2df(self, csv_file):
        """
        Read WebPlotDigitizer csv with multiple datasets, combine into single dataframe with added dataset level column.
        """
        df_csv = pd.read_csv(csv_file, header=[0, 1], sep=',')
        dataset_names = [c for c in df_csv.columns.get_level_values(0) if not c.startswith('Unnamed')]
        df = pd.DataFrame()
        for n in dataset_names:
            i = df_csv.columns.get_loc((n, 'X'))
            x = df_csv.iloc[:, i].dropna()
            y = df_csv.iloc[:, i + 1].dropna()
            c = pd.Series(float(n), index=x.index)
            df2 = pd.concat([x.rename('te'), y.rename('out'), c.rename('c')], axis=1)
            df = pd.concat([df, df2], ignore_index=True)

        return df

    def plot_fit(self,
                 prop_to_plot: FluidProps,
                 fluid_name: str,
                 settings: Optional[pu.PlotSettings] = None,
                 n_points: Optional[int] = 50,
                 ) -> matplotlib.figure.Figure:
        """Plot model fit and original / ground truth data from the WebPlotDigitizer csv dataset.
        This is useful to check quality of model fit, after calling self.train().
        """
        if prop_to_plot is None or prop_to_plot not in list(FluidProps):
            raise ValueError(f'Invalid "prop_to_plot": {prop_to_plot}')

        if settings is None:
            settings = pu.PlotSettings()

        # Data to plot
        if prop_to_plot == 'density':
            title_str = 'Fluid Density'
            y_label = 'Density'
            legend_loc = 'upper right'
        else:
            title_str = 'Fluid Heat Capacity'
            y_label = 'Heat Capacity'
            legend_loc = 'lower right'

        # Plot Title
        fig, params = pu.prepare_figure(settings=settings)
        box = VPacker(children=[pu.box_title(f'{title_str} of fluid "{fluid_name}"'),
                                ], pad=0, sep=pu.DEFAULTS.sep_major)
        artist = pu.annotation_bbox(box, xy=pu.DEFAULTS.xy_topleft)
        fig.add_artist(artist)

        # Data plot
        rect = pu.get_rectangle_below(artist, vsep=pu.DEFAULTS.sep_huge, bottom=0.45)
        ax = fig.add_axes(rect)

        # For all concentration levels, create output curves within measured temperature limits
        df = self.df.groupby('c').te.agg(['min', 'max'])
        for i in np.arange(df.shape[0]):
            te = np.linspace(df.iloc[i, 0], df.iloc[i, 1], n_points)
            c = df.index[i]
            out = self.predict(te, c)
            ax.plot(te, out, '-', label=f'Model prediction, c={df.index[i]}%', zorder=2.5)

        # Measured values as scatter
        ax.scatter(self.df['te'], self.df['out'],
                   s=pu.DEFAULTS.marker_size_scatter,
                   alpha=pu.DEFAULTS.marker_alpha,
                   facecolors=pu.DEFAULTS.marker_facecolor,
                   edgecolors=pu.DEFAULTS.marker_edgecolor,
                   zorder=2.6,
                   label='WebPlotDigitizer measurements',
                   )

        ax.set_xlabel(f'Temperature [{units(self.unit["te"]).units:~P}]')
        ax.set_ylabel(f'{y_label} [{units(self.unit["out"]).units:~P}]')
        ax.grid()
        ax.set_axisbelow('line')
        ax.legend(loc=legend_loc).set_zorder(3)

        return fig
