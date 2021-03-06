# coding: utf-8
"""
Fecha de creacion 4/4/20
@autor: mjapon
"""
import logging

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, TIMESTAMP, CHAR, Text


class TItemConfigAudit(Declarative, JsonAlchemy):
    __tablename__ = 'titemconfig_audit'

    ica_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ic_id = Column(Integer, nullable=False)
    user_crea = Column(Integer, nullable=False)
    fecha_crea = Column(TIMESTAMP, nullable=False)
    ica_tipo = Column(CHAR, nullable=False)  # c-precio de compra, v-precio de venta, s-stock, n-creacion
    ica_valantes = Column(Text)
    ica_valdespues = Column(Text)
    sec_id = Column(Integer, nullable=False)
    ica_ref = Column(Integer, default=0)
    ica_obs = Column(Text)
    ica_tracod = Column(Integer)
