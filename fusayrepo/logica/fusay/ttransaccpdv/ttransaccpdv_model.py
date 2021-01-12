# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Text, Date

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTransaccPdv(Declarative, JsonAlchemy):
    __tablename__ = 'ttransaccpdv'

    tps_codigo = Column(Integer, primary_key=True, nullable=False)
    tra_codigo = Column(Integer, nullable=False)
    tdv_codigo = Column(Integer, nullable=False, default=0)
    sec_codigo = Column(Integer, default=0, nullable=False)
    tps_numsec = Column(Integer, default=1, nullable=False)
