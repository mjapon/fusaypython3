# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
from sqlalchemy import Column, Integer, Numeric, DateTime, Text, String

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy


class TFinCredito(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_credito'

    cre_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    per_id = Column(Integer, nullable=False)
    cre_monto = Column(Numeric(15, 6), default=0.0, nullable=False)
    cre_tasa = Column(Numeric(8, 4), default=0.0, nullable=False)
    cre_fechacrea = Column(DateTime, nullable=False)
    cre_usercrea = Column(Integer, nullable=False)
    cre_estado = Column(Integer, nullable=False, default=1)
    cre_obs = Column(Text)
    cre_plazo = Column(Integer, nullable=False, default=0)
    cre_prod = Column(Integer, default=0)
    cre_tipoint = Column(Integer, default=0)
    cre_cuota = Column(Numeric(15, 6), default=0.0)
    cre_totalint = Column(Numeric(15, 6), default=0.0)
    cre_saldopend = Column(Numeric(15, 6), default=0.0)


class TFinHistoCred(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_histo_cred'

    hc_id = Column(Integer, nullable=False, primary_key=True)
    cre_id = Column(Integer, nullable=False)
    hc_estado = Column(Integer, nullable=False)
    hc_usercrea = Column(Integer, nullable=False)
    hc_fechacrea = Column(DateTime, nullable=False)
    hc_obs = Column(Text)
    hc_estadoprevio = Column(Integer, nullable=False)


class TFinAdjunto(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_adjuntos'

    fadj_id = Column(Integer, nullable=False, primary_key=True)
    adj_id = Column(Integer, nullable=False)
    cre_id = Column(Integer, nullable=False)
    fadj_nombre = Column(String(300), nullable=False)
    fadj_obs = Column(Text)
    user_crea = Column(Integer, nullable=False)
    fadj_fechacrea = Column(DateTime)
