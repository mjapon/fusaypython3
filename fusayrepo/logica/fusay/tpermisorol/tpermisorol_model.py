# coding: utf-8
"""
Fecha de creacion 10/9/20
@autor: mjapon
"""
import datetime
import logging

from sqlalchemy import Column, Integer, TIMESTAMP

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TPermisoRol(Declarative, JsonAlchemy):
    __tablename__ = 'tpermisorol'
    prl_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    prm_id = Column(Integer, nullable=False)
    rl_id = Column(Integer, nullable=False)
    prl_fechacrea = Column(TIMESTAMP, default=datetime.datetime.now())
