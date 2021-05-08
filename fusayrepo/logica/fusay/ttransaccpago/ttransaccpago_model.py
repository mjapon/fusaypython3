# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTransaccPago(Declarative, JsonAlchemy):
    __tablename__ = 'ttransaccpago'

    ttp_codigo = Column(Integer, nullable=False, primary_key=True)
    tra_codigo = Column(Integer, nullable=False)
    cta_codigo = Column(Integer, nullable=False)
    ttp_signo = Column(Integer, nullable=False, default=1)
    ttp_coddocs = Column(Text)
    ttp_tipcomprob = Column(Integer)
    ttp_orden = Column(Integer, default=1)
