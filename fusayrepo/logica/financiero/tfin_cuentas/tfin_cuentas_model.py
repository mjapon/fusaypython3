# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, Numeric, DateTime, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFinCuentas(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_cuentas'

    cue_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    per_id = Column(Integer, nullable=False)
    tc_id = Column(Integer, nullable=False)
    cue_fecha_apertura = Column(DateTime, nullable=False)
    cue_estado = Column(Integer, nullable=False, default=1)
    cue_nombre = Column(String(80))
    cue_num_libreta = Column(String(80))
    cue_fecha_cierre = Column(DateTime)
    cue_saldo_total = Column(Numeric(16, 6), nullable=False, default=0.0)
    cue_saldo_bloq = Column(Numeric(16, 6), nullable=False, default=0.0)
    cue_saldo_disp = Column(Numeric(16, 6), nullable=False, default=0.0)
    user_crea = Column(Integer, nullable=False)
    user_cierre = Column(Integer)
