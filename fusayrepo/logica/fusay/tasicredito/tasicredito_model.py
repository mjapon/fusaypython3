# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Date, Numeric

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAsicredito(Declarative, JsonAlchemy):
    __tablename__ = 'tasicredito'

    cre_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    dt_codigo = Column(Integer, nullable=False)
    cre_fecini = Column(Date, nullable=False)
    cre_fecven = Column(Date)
    cre_intere = Column(Numeric(4, 2), default=0.0)
    cre_intmor = Column(Numeric(4, 2), default=0.0)
    cre_compro = Column(String(15), nullable=False)
    cre_codban = Column(Integer)
    cre_saldopen = Column(Numeric(15, 4), default=0.0)
    cre_tipo = Column(Integer, default=1, nullable=False)
