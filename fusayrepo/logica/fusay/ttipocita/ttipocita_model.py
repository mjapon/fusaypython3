# coding: utf-8
"""
Fecha de creacion 3/10/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Numeric

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTipoCita(Declarative, JsonAlchemy):
    __tablename__ = 'ttipocita'

    tipc_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    tipc_calini = Column(Numeric(4, 2), nullable=False, default=8.0)
    tipc_calfin = Column(Numeric(4, 2), nullable=False, default=17.0)
    tipc_nombre = Column(String(20))
