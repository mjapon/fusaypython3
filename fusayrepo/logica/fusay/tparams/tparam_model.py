# coding: utf-8
"""
Fecha de creacion 3/18/20
@autor: mjapon
"""
import datetime
import logging

from sqlalchemy import Column, Integer, String, TIMESTAMP, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TParams(Declarative, JsonAlchemy):
    __tablename__ = 'tparams'
    tprm_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    tprm_abrev = Column(String(20), nullable=False)
    tprm_nombre = Column(String(80), nullable=False)
    tprm_val = Column(Text, nullable=False)
    tprm_fechacrea = Column(TIMESTAMP, default=datetime.datetime.now())
    tprm_seccion = Column(Integer, default=0)
    tprm_estado = Column(Integer, default=0)  # 0-valido, 1-anulado
    tprm_usercrea = Column(Integer, default=0)
    tprm_userupd = Column(Integer)
    tprm_fechaupd = Column(TIMESTAMP)
