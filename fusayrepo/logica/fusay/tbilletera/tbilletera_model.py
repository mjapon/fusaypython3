# coding: utf-8
"""
Fecha de creacion 3/18/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric, Text, SmallInteger

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TBilletera(Declarative, JsonAlchemy):
    __tablename__ = 'tbilletera'

    bil_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bil_code = Column(String(40), nullable=False)
    bil_nombre = Column(String(40), nullable=False)
    bil_fechacrea = Column(DateTime, nullable=False)
    bil_usercrea = Column(Integer, nullable=False)
    bil_saldo = Column(Numeric(10, 4), default=0.0, nullable=False)
    bil_saldoini = Column(Numeric(10, 4), default=0.0, nullable=False)
    bil_obs = Column(Text)
    ic_id = Column(Integer, nullable=False)  # Codigo de la cuenta contable
    bil_estado = Column(Integer, default=1)  # 1: Valido, 2:Anulado


class TBilleteraMov(Declarative, JsonAlchemy):
    __tablename__ = 'tbilleteramov'

    bmo_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bmo_fechacrea = Column(DateTime, nullable=False)
    bmo_codadj = Column(Integer)
    trn_codigo = Column(Integer, default=0)
    bmo_clase = Column(SmallInteger, default=1)  # 1:Ingreso, 2:Egreso, 3:Transferencia
    vt_id = Column(Integer, default=0)
    bmo_estado = Column(SmallInteger, default=0)  # 0: Pendiente, 1:Confirmado, 2:Anulado
    bmo_fechatransacc = Column(Date)
    bmo_numero = Column(Integer)
    bmo_monto = Column(Numeric(15, 6), default=0.0)


class TBilleteraMovDet(Declarative, JsonAlchemy):
    __tablename__ = 'tbilleteramovdet'

    bmd_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    bmo_id = Column(Integer, nullable=False)
    bil_id = Column(Integer, nullable=False)
