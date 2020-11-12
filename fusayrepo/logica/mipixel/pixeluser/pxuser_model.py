# coding: utf-8
"""
Fecha de creacion 11/12/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TPxuser(Declarative, JsonAlchemy):
    __tablename__ = 'tpxuser'

    pxus_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    pxus_cuenta = Column(String(20), nullable=False, unique=True)
    pxus_clave = Column(String(20), nullable=False)
    pxus_nombre = Column(String(100), nullable=False)
    pxus_email = Column(String(80), nullable=False)
    pxus_fechacrea = Column(TIMESTAMP)
    pxus_estado = Column(Integer, default=0, nullable=False)
