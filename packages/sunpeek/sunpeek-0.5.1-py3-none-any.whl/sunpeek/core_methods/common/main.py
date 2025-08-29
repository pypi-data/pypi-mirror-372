from typing import List, Optional, Any, Dict
from abc import ABC, abstractmethod
import warnings
import enum
import traceback
from dataclasses import dataclass
import datetime as dt
import pandas as pd
import pendulum

from sunpeek.common.errors import AlgorithmError
from sunpeek.common.utils import sp_logger
from sunpeek.components import Plant, Component
from sunpeek.components.helpers import AlgoCheckMode
from sunpeek.components.fluids import UninitialisedFluid
from sunpeek.components.types import UninitialisedCollector
from sunpeek.serializable_models import ProblemType, CoreProblem, CoreMethodFeedback, PCMethodFeedback


@dataclass
class AlgoResult:
    """AlgoResult is returned by CoreAlgorithm.run(). It holds the algorithm output, the successful strategy (on of all
    possible algorithm strategies), and a CoreMethodFeedback with details about problems in any of the strategies.
    """
    output: Optional[Any]
    successful_strategy: Optional['CoreStrategy']
    feedback: Optional[CoreMethodFeedback]

    @property
    def success(self):
        return self.feedback.success

    @property
    def successful_strategy_str(self):
        return self.feedback.successful_strategy_str


class CoreStrategy(ABC):
    """Strategy of some CoreAlgorithm. To be attached to an algorithm with algo.define_strategies().

    A strategy is defined for a specific component and should implement methods _calc() and _get_feedback().
    """
    name = '(unnamed strategy)'
    feedthrough_real_sensor = False

    def __init__(self, component: Component):
        self.component: Component = component

    @abstractmethod
    def _calc(self) -> Dict[str, pd.Series]:
        """Implement calculation of strategy, using information from self.component
        """
        raise NotImplementedError()

    @abstractmethod
    def _get_feedback(self, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        """Return CoreMethodProblem for given strategy.
        """
        raise NotImplementedError()

    def get_feedback(self, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        feedback = self._get_feedback(check_mode)
        if not isinstance(feedback, CoreMethodFeedback):
            raise AlgorithmError(f'Strategy "{self}" returned problems with invalid type. '
                                 f'Expected "CoreMethodFeedback", got "{type(feedback)}".')
        return feedback

    def execute(self):
        """Try to calculate strategy, sanitize check output dict and return if ok.

        Returns
        -------
        elapsed_time : float, elapsed time in algorithm in seconds
        output : dict, strategy output, values are asserted to be unit-aware (pint-pandas) Series.

        Raises
        ------
        AlgorithmError
        """
        start_time = pendulum.now()
        output = self._calc()
        elapsed_time = (pendulum.now() - start_time).total_seconds()
        self.check_output(output)

        return elapsed_time, output

    def check_output(self, output):
        """Additional checks to be performed on output of a strategy.
        """
        pass

    @property
    def plant(self):
        return self.component.plant

    def __repr__(self):
        return f'SunPeek {self.__class__.__name__} called "{self.name}"'

    def __str__(self):
        return self.__class__.__name__


class VirtualSensorStrategy(CoreStrategy):  # noqa

    def check_output(self, output):
        """Specific checks for the output of virtual sensor calculations.
        """
        super().check_output(output)
        if not isinstance(output, dict):
            raise AlgorithmError(f'Strategy "{self}": Expected dict from call to execute(), but got {type(output)}.')

        for k, v in output.items():
            if v is None:
                if self.feedthrough_real_sensor:
                    # Output is allowed to be None for strategies that only use a real sensor, example:
                    # power_from_real_sensor strategy
                    continue
                else:
                    raise AlgorithmError(
                        f'Strategy "{self}": Calculation output {k} is None, expected pd.Series.')

            if not isinstance(v, pd.Series):
                raise AlgorithmError(f'Strategy "{self}": Calculation output {k} is {type(v)}, expected pd.Series.')

            # Test for length of calculated data
            if len(v) != len(self.plant.time_index):
                raise AlgorithmError(
                    f'Strategy "{self}": Size of returned virtual sensor data ({len(v)}) is incompatible with size of '
                    f'"Plant.time_index" ({len(self.plant.time_index)}).')

            # Test for a unit-aware (pint) pd.Series
            try:
                v.pint
            except AttributeError:
                raise AlgorithmError(f'Strategy "{self}": Calculation output {k} is pd.Series as expected, '
                                     f'but is not unit-aware (it lacks a dtype from pint-pandas).')


class StrategyErrorBehavior(str, enum.Enum):
    skip = 'skip'
    error = 'error'


# noinspection PyArgumentList
class CoreAlgorithm(ABC):
    """Superclass for all SunPeek core algorithms, mainly virtual sensors, PC (Performance Check) method and D-CAT
    energy yield methods.

    This class handles various strategies for an algorithm (e.g. various implementations to calculate thermal power,
    or various Performance Check methods, equations etc.

    *args and **kwargs passed to object creation are forwarded to :meth:`define_strategies`.
    """

    name = 'CoreAlgorithm'

    def __init__(self, component: Component, strategies: Optional[List[VirtualSensorStrategy]] = None, *args, **kwargs):
        self.component = component
        self.strategies = strategies or self.define_strategies(*args, **kwargs)
        self.feedback = CoreMethodFeedback()

    @abstractmethod
    def define_strategies(self, *args, **kwargs) -> List[VirtualSensorStrategy]:
        raise NotImplementedError()

    def run(self, on_strategy_error: StrategyErrorBehavior = 'skip') -> AlgoResult:
        """Calculates algorithm using its defined strategies, stopping at the first successful strategy.

        Parameters
        ----------
        on_strategy_error : str, optional
            If 'raise', exceptions that occur during a strategy.execute() are raised. If not, they are saved as
            own_feedback in self.problems. In any case, errors are logged.

        Raises
        ------
        AlgorithmError : if algorithm has no strategies defined, or if getting some strategy problems fails.
        """
        if on_strategy_error not in list(StrategyErrorBehavior):
            raise AlgorithmError(f'Invalid value for "on_strategy_error": {on_strategy_error}. '
                                 f'Valid values are: {", ".join(StrategyErrorBehavior)}')

        if not self.strategies:
            raise AlgorithmError(f'Cannot run algo "{self}": No calculation strategies defined.')

        self.feedback = CoreMethodFeedback(success=False)
        for strategy in self.strategies:
            feedback = strategy.get_feedback(check_mode=AlgoCheckMode.config_and_data)
            self.feedback.add_sub(strategy.name, feedback)

            if feedback.success:
                try:
                    elapsed_time, output = strategy.execute()
                    self.feedback.success = True
                    self.feedback.problem_slots = feedback.problem_slots
                    sp_logger.debug(f'Done in {elapsed_time:3.1f}s '
                                    f'Algo "{self}" run() on component "{self.component.name}": '
                                    f'Successful using strategy "{strategy.name}". ')
                    return AlgoResult(output, strategy, self.feedback)

                except Exception as e:
                    # The philosophy behind catching all Exceptions here: We always calculate all virtual sensors
                    # at `calculate_virtuals(plant)`, we don't know beforehand and therefore don't calculate virtuals
                    # specifically for some particular evaluation (like the PC method).
                    # For example: A particular virtual sensor that is not required by the PC method might fail
                    # to calculate, but that would not affect running the PC method. That's why we decided to catch
                    # all exceptions during calculation here and feedback them as `AlgoProblem`.
                    # The full exception trace is reported in the log files.
                    sp_logger.error(f'Algo "{self}" run() on component {self.component.name}: '
                                    f'error in strategy.execute() for "{strategy}": {traceback.format_exc()}')
                    if on_strategy_error == StrategyErrorBehavior.error:
                        raise
                    else:
                        self.feedback.add_own(
                            CoreProblem(ProblemType.unexpected_in_calc,
                                        description=f'An unexpected calculation error of type "{type(e)}" has occurred '
                                                    f'during calculation of strategy "{strategy}". '
                                                    f'For further information, see '
                                                    f'https://docs.sunpeek.org/errors.html#unexpected-calculation-error'))

        sp_logger.info(f'Algo "{self}" run(): Could not calculate, none of the {len(self.strategies)} strategies was '
                       f'successful.')

        return AlgoResult(None, None, self.feedback)

    def get_config_feedback(self) -> CoreMethodFeedback:
        """Cycle through all algo strategies, return CoreMethodFeedback of all strategy problems.
        Stops at first successful strategy, copies problem slots from strategy.
        """
        if not self.strategies:
            raise AlgorithmError(f'Cannot run algo "{self}": No calculation strategies defined.')

        algo_feedback = CoreMethodFeedback(success=False)
        for strategy in self.strategies:
            feedback = strategy.get_feedback(AlgoCheckMode.config_only)
            algo_feedback.add_sub(strategy.name, feedback)
            if feedback.success:
                algo_feedback.success = True
                algo_feedback.problem_slots = feedback.problem_slots
                break

        return algo_feedback

    def allowed_components(self) -> tuple:
        # List of allowed components. By default, only Plant is allowed.
        return Plant,

    @property
    def component(self):
        return self._component

    @component.setter
    def component(self, val):
        allowed_components = self.allowed_components()
        if not isinstance(allowed_components, tuple):
            raise AlgorithmError(f'Algo "{self}": allowed_components() returned invalid type. '
                                 f'Expected tuple, got {type(allowed_components)}.')
        for c in allowed_components:
            if not issubclass(c, Component):
                raise AlgorithmError(f'Algo "{self}": allowed_components() returned an invalid component '
                                     f'of class "{c.__name__}". '
                                     f'Allowed components must be subclasses of "Component", e.g. Plant, Array etc.')
        if not isinstance(val, self.allowed_components()):
            raise AlgorithmError(f'Algo "{self}" got a component of invalid type {str(val)}. '
                                 f'Valid types are: {self.valid_components}.')

        self._component = val

    @property
    def strategies(self):
        if self._strategies is None:
            self._strategies = self.define_strategies()
        return self._strategies

    @strategies.setter
    def strategies(self, strategies):
        if strategies is None:
            self._strategies = []
            return

        for s in strategies:
            if not issubclass(type(s), CoreStrategy):
                raise AlgorithmError(f'Cannot add strategy to algorithm {self}: '
                                     f'Expected "CoreStrategy" object, but got "{type(s)}".')

        snames = [s.name for s in strategies]
        duplicates = [x for n, x in enumerate(snames) if x in snames[:n]]
        if duplicates:
            raise AlgorithmError(f'Cannot add strategies with duplicate names to algo "{self}". '
                                 f'Duplicate strategy names: {", ".join(duplicates)}.')

        self._strategies = strategies

    @property
    def valid_components(self):
        valid_component_names = [c.__name__ for c in self.allowed_components()]
        return ', '.join(valid_component_names)

    @property
    def successful_strategy(self) -> Optional[CoreStrategy]:
        for strategy in self.strategies:
            fb = strategy.get_feedback(AlgoCheckMode.config_only)
            if fb.success:
                return strategy
        return None

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return f'SunPeek algorithm "{self.__class__.__name__}"'

    @staticmethod
    def create_variants(arg: Any, allowed_type: type, default: Any) -> List[Any]:
        """Create list with sanitized inputs for algo strategies. Set default if needed.

        Raises
        ------
        TypeError : if `arg` or `default` does not match `allowed_type`.
        AlgorithmError : if no valid variants are found
        """
        def check_args(args: List[Any]) -> List[Any]:
            if args is None:
                return []
            args = args if isinstance(args, list) else [args]
            if is_enum:
                args = [allowed_type(item) for item in args if item is not None]
            for item in args:
                if item is not None and not isinstance(item, allowed_type):
                    raise TypeError(f'Input is not a valid {allowed_type.__name__}.')
            # Remove None
            args = [x for x in args if x is not None]
            # Return without duplicates
            return list(dict.fromkeys(args))

        is_enum = isinstance(allowed_type, type) and issubclass(allowed_type, enum.Enum)
        args = check_args(arg)
        args = args if args else check_args(default)
        if not args:
            raise AlgorithmError('No valid variants found.')
        return args

    def check_interval(self,
                       eval_start: dt.datetime | pd.Timestamp | None = None,
                       eval_end: dt.datetime | pd.Timestamp | None = None) -> None:
        """Make sure we have data in the specified interval, and check that plant's virtual sensors are up-to-date.
        """
        plant = self.component.plant
        if not plant.virtuals_calculation_uptodate:
            warnings.warn(f'{self.name} is called on a plant with outdated virtual sensors'
                          f' (plant.virtuals_calculation_uptodate flag is False). '
                          f'{self.name} results might be outdated or inconsistent with the plant configuration. '
                          f'To overcome this, call "virtuals.calculate_virtuals(plant)".')

        plant.context.set_eval_interval(eval_start, eval_end, check_overlap=True, method_name=self.name)



## Specific validation code

def is_valid_fluid(fluid, check_mode: AlgoCheckMode) -> bool:
    if check_mode == AlgoCheckMode.config_only:
        return fluid is not None
    return (fluid is not None) and (not isinstance(fluid, UninitialisedFluid))


def is_valid_collector(collector, check_mode: AlgoCheckMode) -> bool:
    if check_mode == AlgoCheckMode.config_only:
        return collector is not None
    return (collector is not None) and (not isinstance(collector, UninitialisedCollector))
