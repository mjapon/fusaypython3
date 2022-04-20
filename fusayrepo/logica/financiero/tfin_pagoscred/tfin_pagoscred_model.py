# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, Numeric, Date, DateTime, SMALLINT, Text
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFinPagosCredDet(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_pagoscreddet'

    pg_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    pg_total = Column(Numeric(15, 6), nullable=False, default=0.0)
    pg_capital = Column(Numeric(15, 6), nullable=False, default=0.0)
    pg_interes = Column(Numeric(15, 6), nullable=False, default=0.0)
    pg_mora = Column(Numeric(15, 6), nullable=False, default=0.0)
    pg_npago = Column(SMALLINT, nullable=False, default=1)
    pg_fecpagocalc = Column(Date)
    pg_fechacrea = Column(DateTime, nullable=False)
    pg_usercrea = Column(Integer, nullable=False)
    pg_estado = Column(SMALLINT, nullable=False, default=1)
    pg_useranul = Column(Integer)
    pg_fecanul = Column(DateTime)
    pg_obsanul = Column(Text)
    pg_obs = Column(Text)
    pg_amoid = Column(Integer, nullable=False)  # Se relaciona con la tabla de amortizacion
    pgc_id = Column(Integer, nullable=False)


class TFinPagosCredCab(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_pagoscredcab'

    pgc_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    cre_id = Column(Integer, nullable=False)
    pgc_usercrea = Column(Integer, nullable=False)
    pgc_total = Column(Numeric(15, 6), nullable=False, default=0.0)
    pgc_adj = Column(Integer)
    pgc_obs = Column(Text)
    pgc_adelanto = Column(Numeric(15, 6), default=0.0)
    pgc_fechacrea = Column(DateTime, nullable=False)
    pgc_estado = Column(SMALLINT, default=1)
    pgc_useranul = Column(Integer)
    pgc_fechanul = Column(DateTime)
    pgc_obsanul = Column(Text)
    pgc_saldopend = Column(Numeric(15, 6), default=0.0)
    pgc_total_capital = Column(Numeric(15, 6), default=0.0, nullable=False)
    pgc_total_interes = Column(Numeric(15, 6), default=0.0, nullable=False)
    pgc_total_intmora = Column(Numeric(15, 6), default=0.0, nullable=False)
