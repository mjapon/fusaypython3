# coding: utf-8
"""
Fecha de creacion 1/21/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TPlan(Declarative, JsonAlchemy):
    __tablename__ = 'tplan'
    pln_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    pln_fechacrea = Column(DateTime, nullable=False)
    pln_estado = Column(Integer, default=0, nullable=False)
    pln_usercrea = Column(Integer, nullable=False)
    pln_nombre = Column(String(100), nullable=False)
    pln_obs = Column(Text)
    trn_codigo = Column(Integer)
