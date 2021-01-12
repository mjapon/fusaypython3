# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Numeric

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsidetalle(Declarative, JsonAlchemy):
    __tablename__ = 'tasidetalle'
    dt_codigo = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    trn_codigo = Column(Integer, nullable=False)
    cta_codigo = Column(Integer, nullable=False)
    art_codigo = Column(Integer, nullable=False)
    per_codigo = Column(Integer, nullable=False)
    pry_codigo = Column(Integer)
    dt_cant = Column(Numeric(12, 5), default=0.0, nullable=False)
    dt_precio = Column(Numeric(15, 6), default=0.0, nullable=False)
    dt_debito = Column(Integer, nullable=False, default=0)
    dt_preref = Column(Numeric(15, 6), default=0.0, nullable=False)
    dt_decto = Column(Numeric(7, 4), default=0.0)
    dt_valor = Column(Numeric(15, 6), default=0.0, nullable=False)
    dt_dectogen = Column(Numeric(7, 4), default=0.0, nullable=False)
    dt_tipoitem = Column(Integer, default=0, nullable=False)
    dt_valdto = Column(Numeric(11, 4), default=0.0, nullable=False)
    dt_valdtogen = Column(Numeric(11, 4), default=0.0, nullable=False)
    dt_codsec = Column(Integer, default=0, nullable=False)
