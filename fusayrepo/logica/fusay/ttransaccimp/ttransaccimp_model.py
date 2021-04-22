# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTransaccimp(Declarative, JsonAlchemy):
    __tablename__ = 'ttransaccimp'

    timp_id = Column(Integer, nullable=False, primary_key=True)
    tra_codigo = Column(Integer, nullable=False)
    tra_impg = Column(Integer, default=0, nullable=False)
    tra_imp0 = Column(Integer, default=0, nullable=False)
    tra_iserv = Column(Integer, default=0, nullable=False)
    tra_ice = Column(Integer, default=0, nullable=False)
    tra_ivagasto = Column(Integer, default=0, nullable=False)
    tra_signo = Column(Integer)
    sec_codigo = Column(Integer, default=1, nullable=False)
