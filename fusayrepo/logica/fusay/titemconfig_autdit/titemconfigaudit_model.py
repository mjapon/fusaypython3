# coding: utf-8
"""
Fecha de creacion 4/4/20
@autor: mjapon
"""
import logging

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, TIMESTAMP, Numeric, CHAR


class TItemConfigAudit(Declarative, JsonAlchemy):
    __tablename__ = 'titemconfig_audit'

    ica_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ic_id = Column(Integer, nullable=False)
    user_crea = Column(Integer, nullable=False)
    fecha_crea = Column(TIMESTAMP, nullable=False)
    ica_tipo = Column(CHAR, nullable=False)
    ica_valantes = Column(Numeric(10, 4))
    ica_valdespues = Column(Numeric(10, 4))
    sec_id = Column(Integer, nullable=False)
