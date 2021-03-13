# coding: utf-8
"""
Fecha de creacion 3/12/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, SmallInteger

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TModelocontab(Declarative, JsonAlchemy):
    __tablename__ = 'tmodelocontab'

    mc_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    mc_nombre = Column(String(100), nullable=False)
    mc_estado = Column(Integer, default=1, nullable=False)
    mc_fechacrea = Column(DateTime, nullable=False)


class TModelocontabdet(Declarative, JsonAlchemy):
    __tablename__ = 'tmodelocontabdet'

    mcd_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    mc_id = Column(Integer, nullable=False)
    tra_codigo = Column(Integer, nullable=False)
    cta_codigo = Column(Integer, nullable=False)
    mcd_signo = Column(SmallInteger, default=1, nullable=False)
