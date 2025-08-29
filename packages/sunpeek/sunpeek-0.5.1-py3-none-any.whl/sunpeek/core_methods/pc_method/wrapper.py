import warnings
from typing import List
import datetime as dt
import itertools

from sunpeek.common.utils import sp_logger
from sunpeek.components import Plant
from sunpeek.components.helpers import AlgoCheckMode
from sunpeek.core_methods.virtuals import CoreAlgorithm, CoreStrategy
from sunpeek.serializable_models import CoreMethodFeedback, PCMethodFeedback
from sunpeek.core_methods.pc_method.main import PCMethod
from sunpeek.core_methods.pc_method import PCFormulae, PCMethods
from sunpeek.core_methods.common.main import AlgoResult


def run_performance_check(plant: Plant,
                          method: List[PCMethods | str | None] | None = None,
                          formula: List[PCFormulae | int | None] | None = None,
                          use_wind: List[None | bool] | None = None,
                          # Context
                          eval_start: dt.datetime | None = None,
                          eval_end: dt.datetime | None = None,
                          # Settings:
                          safety_pipes: float | None = None,
                          safety_uncertainty: float | None = None,
                          safety_others: float | None = None,
                          interval_length: dt.timedelta | None = None,
                          min_data_in_interval: int | None = None,
                          max_gap_in_interval: dt.timedelta | None = None,
                          max_nan_density: float | None = None,
                          min_intervals_in_output: int | None = None,
                          accuracy_level: str | None = None,
                          ) -> AlgoResult:
    """Run Performance Check analysis with given settings, trying all possible strategies in order.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'accuracy_level': accuracy_level,
    }
    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    pc_algo.check_interval(eval_start, eval_end)
    algo_result = pc_algo.run()
    return algo_result


def list_feedback(plant: Plant,
                  method: List[PCMethods | str | None] | None = None,
                  formula: List[PCFormulae | int | None] | None = None,
                  use_wind: List[bool | None] | None = None,
                  ) -> List[PCMethodFeedback]:
    """Report which strategies of the Performance Check analysis can be run for given plant config and settings.
    Does not actually run PC calculation. Can operate on a plant without data uploaded.
    """
    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind)
    pc_feedback = []
    for strategy in pc_algo.strategies:
        fb = strategy.get_feedback(AlgoCheckMode.config_only)
        pc_feedback.append(strategy.get_pc_from_core_feedback(fb))

    return pc_feedback


def get_feedback(plant: Plant,
                 method: List[PCMethods | str | None] | None = None,
                 formula: List[PCFormulae | int | None] | None = None,
                 use_wind: List[bool | None] | None = None,
                 # Settings:
                 safety_pipes: float | None = None,
                 safety_uncertainty: float | None = None,
                 safety_others: float | None = None,
                 interval_length: dt.timedelta | None = None,
                 min_data_in_interval: int | None = None,
                 max_gap_in_interval: dt.timedelta | None = None,
                 max_nan_density: float | None = None,
                 min_intervals_in_output: int | None = None,
                 accuracy_level: str | None = None,
                 ) -> CoreMethodFeedback:
    """Report which strategy of the Performance Check analysis can be run for given plant config and settings, if any.
    Stops at first successful strategy.
    Does not actually run PC calculation. Can operate on a plant without data uploaded.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'accuracy_level': accuracy_level,
    }

    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    return pc_algo.get_config_feedback()


class PCStrategy(CoreStrategy):
    def __init__(self, pc: PCMethod):
        super().__init__(pc.plant)
        self.pc = pc
        self.name = (f'Thermal Power Check with '
                     f'Mode: {pc.mode.value}, '
                     f'Formula: {pc.formula.id}, '
                     f'{"Using wind" if pc.formula.use_wind else "Ignoring wind"}')

    def _calc(self):
        return self.pc.run()  # results.PCMethodOutput

    def _get_feedback(self, check_mode: AlgoCheckMode) -> CoreMethodFeedback:
        return self.pc.get_feedback(check_mode)

    def get_pc_from_core_feedback(self, core_feedback: CoreMethodFeedback) -> PCMethodFeedback:
        return PCMethodFeedback(self.pc.mode.value,
                                self.pc.formula.id,
                                self.pc.formula.use_wind,
                                core_feedback.success,
                                core_feedback.parse())


class PCAlgo(CoreAlgorithm):

    name = 'Performance Check analysis'

    def define_strategies(self, methods=None, formulae=None, use_wind=None, **kwargs) -> List[PCStrategy]:
        """Returns list of all possible PC method strategies in the order they will be executed.
        """
        variants = {'methods': self.create_variants(methods, allowed_type=PCMethods,
                                                    default=[PCMethods.iso, PCMethods.extended]),
                    'formulae': self.create_variants(formulae, allowed_type=PCFormulae,
                                                     default=[PCFormulae.two, PCFormulae.one, PCFormulae.three]),
                    'wind': self.create_variants(use_wind, allowed_type=bool, default=[True, False])}
        all_variants = list(itertools.product(*variants.values()))
        strategies = [PCStrategy(PCMethod.create(self.component, m, f, w, **kwargs)) for m, f, w in all_variants]

        return strategies


def get_successful_strategy(plant: Plant,
                            method: List[PCMethods | str | None] | None = None,
                            formula: List[PCFormulae | int | None] | None = None,
                            use_wind: List[bool | None] | None = None,
                            # Settings:
                            safety_pipes: float | None = None,
                            safety_uncertainty: float | None = None,
                            safety_others: float | None = None,
                            interval_length: dt.timedelta | None = None,
                            min_data_in_interval: int | None = None,
                            max_gap_in_interval: dt.timedelta | None = None,
                            max_nan_density: float | None = None,
                            min_intervals_in_output: int | None = None,
                            accuracy_level: str | None = None,
                            ) -> PCStrategy:
    """Report the first strategy of the Performance Check analysis that is successful with given plant and
    settings. Like `get_feedback()`, this does not actually run calculations.
    """
    kwds = {
        'safety_pipes': safety_pipes,
        'safety_uncertainty': safety_uncertainty,
        'safety_others': safety_others,
        'interval_length': interval_length,
        'min_data_in_interval': min_data_in_interval,
        'max_gap_in_interval': max_gap_in_interval,
        'max_nan_density': max_nan_density,
        'min_intervals_in_output': min_intervals_in_output,
        'accuracy_level': accuracy_level,
    }

    pc_algo = PCAlgo(plant, methods=method, formulae=formula, use_wind=use_wind, **kwds)
    strategy = pc_algo.successful_strategy

    return strategy  # noqa
