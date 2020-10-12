# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging

log = logging.getLogger(__name__)

from sqlalchemy import Column, Integer, TIMESTAMP, String, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

class TPermiso(Declarative, JsonAlchemy):
    __tablename__ = 'tpermiso'

    prm_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    prm_nombre = Column(String(50), nullable=False)
    prm_abreviacion = Column(String(50), nullable=False, unique=True)
    prm_detalle = Column(String(200))
    prm_estado = Column(Integer, default=0, nullable=False)