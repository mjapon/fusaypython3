# coding: utf-8
"""
Fecha de creacion 11/13/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class Tcieasiento(Declarative, JsonAlchemy):
    __tablename__ = 'tcieasiento'

    cas_codigo = Column(Integer, nullable=False, primary_key=True)
    cie_codigo = Column(Integer)
    trn_codigo = Column(Integer)
    cas_tipo = Column(Integer, default=0)
