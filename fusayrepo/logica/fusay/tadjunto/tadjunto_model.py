# coding: utf-8
"""
Fecha de creacion 4/29/21
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, DateTime

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TAdjunto(Declarative, JsonAlchemy):
    __tablename__ = 'tadjunto'

    adj_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    adj_ruta = Column(String(500), nullable=False)
    adj_ext = Column(String(80))
    adj_filename = Column(String(100))
    adj_estado = Column(Integer, default=1, nullable=False)
    adj_fechacrea = Column(DateTime, nullable=False)
    adj_usercrea = Column(Integer, nullable=False)
    adj_hash = Column(String(80))
