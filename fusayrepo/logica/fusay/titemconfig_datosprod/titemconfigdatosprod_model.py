# coding: utf-8
"""
Fecha de creacion 3/12/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, Numeric, Date, Boolean

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TItemConfigDatosProd(Declarative, JsonAlchemy):
    __tablename__ = 'titemconfig_datosprod'

    icdp_id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    ic_id = Column(Integer, nullable=False)
    icdp_fechacaducidad = Column(Date)
    icdp_proveedor = Column(Integer, default=-2, nullable=False)
    icdp_modcontab = Column(Integer)
    icdp_preciocompra = Column(Numeric(10,4), default=0.0, nullable=False)
    icdp_precioventa = Column(Numeric(10, 4), default=0.0, nullable=False)
    icdp_precioventamin = Column(Numeric(10, 4), default=0.0, nullable=False)
    icdp_grabaiva = Column(Boolean, default=False)