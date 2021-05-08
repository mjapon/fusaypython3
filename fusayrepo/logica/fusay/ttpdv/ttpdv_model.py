# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTpdv(Declarative, JsonAlchemy):
    __tablename__ = 'ttpdv'
    tdv_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    tdv_numero = Column(String(3), default='001', nullable=False)
    tdv_nombre = Column(String(20), nullable=False)
    tdv_descri = Column(Text)
    tdv_estado = Column(Integer, default=0, nullable=False)
    tdv_maxitem = Column(Integer, default=0, nullable=False)
    alm_codigo = Column(Integer, nullable=False)
