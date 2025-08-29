from sunpeek.components.helpers import ORMBase, ResultStatus
from sqlalchemy import Column, String, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy_utils import UUIDType


class Job(ORMBase):
    __tablename__ = 'jobs'

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    status = Column(Enum(ResultStatus))
    result_path = Column(String)
    plant_id = Column(Integer, ForeignKey('plant.id', ondelete="CASCADE"))
    plant = relationship("Plant", backref="jobs")

    def __init__(self, **kwargs):
        self.id = uuid.uuid4()
        super().__init__(**kwargs)
        self.result_url = None
