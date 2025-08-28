from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Float, Integer, Identity, ForeignKey, DateTime, Enum, Interval, Boolean, ARRAY, \
    JSON
from sunpeek.components.helpers import ORMBase, ComponentParam, AttrSetterMixin
from sunpeek.components import Fluid


class PCMethodOutput(ORMBase, AttrSetterMixin):
    __tablename__ = 'pc_method_outputs'

    id = Column(Integer, Identity(0), primary_key=True)

    plant_id = Column(Integer, ForeignKey('plant.id'))
    plant = relationship("Plant")

    datetime_eval_start = Column(DateTime(timezone=True))
    datetime_eval_end = Column(DateTime(timezone=True))

    # Algorithm / Strategy
    pc_method_name = Column(String)  # The version of the PC method used to reflect the plant hydraulic layout
    evaluation_mode = Column(Enum('ISO', 'extended', name='pc_evaluation_modes'))
    formula = Column(Integer)
    wind_used = Column(Boolean)

    # PCSettings
    settings = Column(JSON)

    # Plant results
    plant_output = relationship("PCMethodOutputPlant", uselist=False)

    # Array results
    array_output = relationship("PCMethodOutputArray")


class PCMethodOutputPlant(ORMBase, AttrSetterMixin):
    __tablename__ = 'pc_results_plant'

    id = Column(Integer, Identity(0), primary_key=True)
    parent_result_id = Column(Integer, ForeignKey('pc_method_outputs.id', ondelete="CASCADE"))

    plant_id = Column(Integer, ForeignKey('plant.id'))
    plant = relationship("Plant")

    n_intervals = Column(Integer)
    total_interval_length = Column(Interval)

    datetime_intervals_start = Column(JSON)
    datetime_intervals_end = Column(JSON)

    tp_measured = ComponentParam('W', param_type='array')
    tp_sp_measured = ComponentParam('W m**-2', param_type='array')
    tp_sp_estimated = ComponentParam('W m**-2', param_type='array')
    tp_sp_estimated_safety = ComponentParam('W m**-2', param_type='array')
    mean_tp_sp_measured = ComponentParam('W m**-2')
    mean_tp_sp_estimated = ComponentParam('W m**-2')
    mean_tp_sp_estimated_safety = ComponentParam('W m**-2')

    target_actual_slope = ComponentParam('')
    target_actual_slope_safety = ComponentParam('')

    fluid_solar_id = Column(ForeignKey(Fluid.id))
    fluid_solar = relationship("Fluid")
    mean_temperature = ComponentParam('K')
    mean_fluid_density = ComponentParam('kg m**-3')
    mean_fluid_heat_capacity = ComponentParam('J kg**-1 K**-1')


class PCMethodOutputArray(ORMBase, AttrSetterMixin):
    __tablename__ = 'pc_results_arrays'

    id = Column(Integer, Identity(0), primary_key=True)
    parent_result_id = Column(Integer, ForeignKey('pc_method_outputs.id', ondelete="CASCADE"))

    array_id = Column(ForeignKey('arrays.id'))
    array = relationship("Array")

    # Input data used in calculation
    data_id = Column(Integer, ForeignKey('pc_results_data.id'))
    data = relationship("PCMethodOutputData", uselist=False, foreign_keys=[data_id])

    tp_sp_measured = ComponentParam('W m**-2', param_type='array')
    tp_sp_estimated = ComponentParam('W m**-2', param_type='array')
    tp_sp_estimated_safety = ComponentParam('W m**-2', param_type='array')
    mean_tp_sp_measured = ComponentParam('W m**-2')
    mean_tp_sp_estimated = ComponentParam('W m**-2')
    mean_tp_sp_estimated_safety = ComponentParam('W m**-2')


class PCMethodOutputData(ORMBase, AttrSetterMixin):
    __tablename__ = 'pc_results_data'

    id = Column(Integer, Identity(0), primary_key=True)
    parent_result_id = Column(Integer, ForeignKey('pc_results_arrays.id', ondelete="CASCADE"))

    te_amb = ComponentParam('degC', param_type='array')
    te_in = ComponentParam('degC', param_type='array')
    te_out = ComponentParam('degC', param_type='array')
    te_op = ComponentParam('degC', param_type='array')
    te_op_deriv = ComponentParam('K hour**-1', param_type='array')

    aoi = ComponentParam('deg', param_type='array')
    iam_b = ComponentParam('dimensionless', param_type='array')
    ve_wind = ComponentParam('m s**-1', param_type='array')

    rd_gti = ComponentParam('W m**-2', param_type='array')
    rd_bti = ComponentParam('W m**-2', param_type='array')
    rd_dti = ComponentParam('W m**-2', param_type='array')
