# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import datetime
import logging

from sqlalchemy import Column, Integer, Date, Boolean, TIMESTAMP, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TPeriodoContable(Declarative, JsonAlchemy):
    __tablename__ = 'tperiodocontable'

    pc_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pc_desde = Column(Date, nullable=False)
    pc_hasta = Column(Date, nullable=False)
    pc_activo = Column(Boolean, nullable=False)
    pc_fechacrea = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())
    pc_usercrea = Column(Integer, nullable=False)
    pc_fechaupd = Column(TIMESTAMP)
    pc_userupd = Column(Integer)
    pc_asientos_cierre = Column(String(100))
    pc_asiento_inicial = Column(Integer)
