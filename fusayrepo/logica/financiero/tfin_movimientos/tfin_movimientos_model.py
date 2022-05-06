# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, Numeric, DateTime, SMALLINT, Text, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy


class TFinMovimientos(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_movimientos'

    mov_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    cue_id = Column(Integer, nullable=False)
    mov_fecha_sistema = Column(DateTime, nullable=False)
    mov_numero_comprob = Column(String(80))
    user_crea = Column(Integer, nullable=False)
    mov_abreviado = Column(String(80), nullable=False)
    mov_deb_cred = Column(SMALLINT, nullable=False, default=1)
    mov_total_transa = Column(Numeric(15, 6), nullable=False, default=0.0)
    mov_num_linea = Column(Integer, nullable=False, default=1)
    mov_estado = Column(SMALLINT, nullable=False, default=1)
    mov_saldo_transa = Column(Numeric(15, 6), nullable=False, default=0.0)
    mov_tipotransa = Column(Integer, nullable=False)
    mov_obs = Column(Text)
