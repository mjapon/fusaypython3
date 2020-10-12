# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import logging
from datetime import datetime

from sqlalchemy import Column, Integer, TIMESTAMP, String, Text, DateTime

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TRol(Declarative, JsonAlchemy):
    __tablename__ = 'trol'
    rl_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    rl_name = Column(String(50), nullable=False)
    rl_desc = Column(String(100))
    rl_abreviacion = Column(String(50), nullable=False)
    rl_grupo = Column(Integer, default=0, nullable=False)
    rl_estado = Column(Integer, default=0, nullable=False)
    rl_fechacrea = Column(DateTime, nullable=False, default=datetime.now())
    rl_usercrea = Column(Integer)
    rl_fechaanula = Column(DateTime)
    rl_fechaedita = Column(DateTime)


