# coding: utf-8
"""
Fecha de creacion 1/21/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text, DateTime, Date

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TSuscripcion(Declarative, JsonAlchemy):
    __tablename__ = 'tsuscripcion'

    sus_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    pln_id = Column(Integer, nullable=False)
    per_id = Column(Integer, nullable=False)
    sus_estado = Column(Integer, default=0, nullable=False)
    sus_diacobro = Column(Integer, default=1, nullable=False)
    sus_diasgracia = Column(Integer, default=0, nullable=False)
    sus_periodicidad = Column(Integer, default=1, nullable=False)
    sus_observacion = Column(Text)
    sus_plantobsfact = Column(Text)
    sus_fechacrea = Column(DateTime)
    sus_usercrea = Column(Integer)
    sus_fechainiserv = Column(Date)
    sus_fechaupd = Column(DateTime)
    sus_userupd = Column(Integer)
