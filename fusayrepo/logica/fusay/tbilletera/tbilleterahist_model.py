# coding: utf-8
from sqlalchemy import Column, Integer, DateTime, Numeric, SmallInteger

from fusayrepo.models.conf import Declarative


class TBilleteraHist(Declarative):
    __tablename__ = 'tbillhist'
    bh_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    dt_codigo = Column(Integer, nullable=False)
    bh_debito = Column(Numeric(15, 6), default=0.0, nullable=False)
    bh_credito = Column(Numeric(15, 6), default=0.0, nullable=False)
    bh_saldo = Column(Numeric(15, 6), default=0.0, nullable=False)
    bh_fechacrea = Column(DateTime, nullable=False)
    bh_fechaactualiza = Column(DateTime)
    bh_usercrea = Column(Integer)
    bh_useractualiza = Column(Integer)
    bh_valido = Column(SmallInteger, nullable=False, default=0)
    bh_fechatransacc = Column(DateTime)
    cta_codigo = Column(Integer)
