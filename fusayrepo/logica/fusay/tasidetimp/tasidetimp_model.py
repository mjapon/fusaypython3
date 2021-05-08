# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Numeric

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsidetimp(Declarative, JsonAlchemy):
    __tablename__ = 'tasidetimp'
    dai_codigo = Column(Integer, nullable=False, primary_key=True)
    dt_codigo = Column(Integer, nullable=False)
    dai_imp0 = Column(Numeric(6, 3), nullable=False)
    dai_impg = Column(Numeric(6, 3))
    dai_ise = Column(Numeric(6, 3))
    dai_ice = Column(Numeric(6, 3))
