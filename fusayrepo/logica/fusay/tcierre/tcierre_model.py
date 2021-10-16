# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""

import logging

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Numeric, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TCierre(Declarative, JsonAlchemy):
    __tablename__ = 'tcierre'

    cie_codigo = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    cie_dia = Column(Date, nullable=False)
    cie_fechapertura = Column(TIMESTAMP)
    cie_fechacierre = Column(TIMESTAMP)
    cie_usercrea = Column(Integer)
    cie_usercierra = Column(Integer)
    cie_estado = Column(Integer, default=0, nullable=False)  # 0-Valido, 1-Anulado
    cie_obsaper = Column(Text)
    cie_obscierre = Column(Text)
    cie_estadocierre = Column(Integer, default=0, nullable=False)  # 0-Abierto, 1-Cerrado
