# coding: utf-8
"""
Fecha de creacion 02/01/2020
@autor: mejg231019
"""
import logging
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TFuser(Declarative, JsonAlchemy):
    __tablename__ = 'tfuser'

    us_id = Column(Integer, primary_key=True, nullable=False)
    us_cuenta = Column(String(20), nullable=False)
    us_clave = Column(String(20), nullable=False)
    per_id = Column(Integer, nullable=False)
    us_fechacrea = Column(DateTime)
    us_estado = Column(Integer, nullable=False, default=0)
    us_fechaupd = Column(DateTime)
    us_userupd = Column(Integer)


class TFuserSec(Declarative, JsonAlchemy):
    __tablename__ = 'tfusersec'

    fus_id = Column(Integer, primary_key=True, nullable=False)
    us_id = Column(Integer, nullable=False)
    sec_id = Column(Integer, nullable=False)
    fus_main = Column(Boolean, nullable=False, default=False)
