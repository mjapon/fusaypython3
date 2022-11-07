# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Numeric, SmallInteger

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TComprobante(Declarative, JsonAlchemy):
    __tablename__ = 'tcomprobante'

    cmp_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    cmp_tipo = Column(SmallInteger, nullable=False)
    cmp_numero = Column(String(20), nullable=False)
    cmp_trncod = Column(Integer, nullable=False)
    cmp_claveaccesso = Column(String(60), nullable=False)
    cnt_id = Column(Integer, nullable=False)
    emp_codigo = Column(Integer, nullable=False)
    cmp_fecha = Column(DateTime, nullable=False)
    cmp_total = Column(Numeric(15, 6), default=0.0, nullable=False)
    cmp_estado = Column(SmallInteger, nullable=False)
    cmp_fecsys = Column(DateTime)
    cmp_ambiente = Column(SmallInteger, nullable=False)
