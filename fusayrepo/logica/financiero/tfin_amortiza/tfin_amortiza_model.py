# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, Numeric, Date, DateTime
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFinAmortiza(Declarative, JsonAlchemy):
    __tablename__ = 'tfin_amortiza'

    amo_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    cre_id = Column(Integer, nullable=False)
    amo_ncuota = Column(Integer, nullable=False)
    amo_fechapago = Column(Date, nullable=False)
    amo_capital = Column(Numeric(15, 6), default=0.0, nullable=False)
    amo_interes = Column(Numeric(15, 6), default=0.0, nullable=False)
    amo_saldo = Column(Numeric(15, 6), default=0.0, nullable=False)
    amo_estado = Column(Integer, default=0, nullable=False) #1-
    amo_fechacrea = Column(DateTime, nullable=False)
    amo_usercrea = Column(Integer, default=0, nullable=False)
    pgc_id = Column(Integer)  # Reprsenta el pago con el que se crean una nueva tabla de amortizacion (x abonos capital)
