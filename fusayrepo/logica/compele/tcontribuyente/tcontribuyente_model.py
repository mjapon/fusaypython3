# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: Manuel Japon
"""
import logging

from sqlalchemy import Column, Integer, String, SmallInteger

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TContribuyente(Declarative, JsonAlchemy):
    __tablename__ = 'tcontribuyente'

    cnt_id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    cnt_ciruc = Column(String(15), unique=True, nullable=False)
    cnt_nombres = Column(String(100), nullable=False)
    cnt_apellidos = Column(String(100))
    cnt_direccion = Column(String(100))
    cnt_telf = Column(String(40))
    cnt_email = Column(String(40), nullable=False)
    cnt_movil = Column(String(20))
    cnt_estado = Column(SmallInteger, nullable=False, default=0)
    cnt_clave = Column(String(40), nullable=False)
    cnt_estado_clave = Column(Integer, nullable=False, default=0)
