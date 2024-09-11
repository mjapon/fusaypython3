from sqlalchemy import Column, Integer, Boolean, DateTime, Text, Date, Numeric, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy


class TTransaccRel(Declarative, JsonAlchemy):
    __tablename__ = 'ttransaccrel'
    trel_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    trn_codorigen = Column(Integer, nullable=False)
    trn_coddestino = Column(Integer, nullable=False)
    trel_tracoddestino = Column(Integer, nullable=False)
    trel_fechacrea = Column(DateTime, nullable=False)
    trel_usercrea = Column(Integer, nullable=False)
    trel_activo = Column(Boolean, nullable=False, default=True)
