# coding: utf-8
"""
Fecha de creacion 11/9/20
@autor: mjapon
"""
import logging

from sqlalchemy import Column, Integer, String, Text

from fusayrepo.models.conf import Declarative
from fusayrepo.utils.jsonutil import JsonAlchemy

log = logging.getLogger(__name__)


class TTransacc(Declarative, JsonAlchemy):
    __tablename__ = 'ttransacc'

    tra_codigo = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    tra_nombre = Column(String(50), nullable=False)
    tra_obs = Column(Text)
    tra_xmlsav = Column(Integer, nullable=False, default=0)
    tra_tipart = Column(Integer, nullable=False, default=0)
    tra_edcomp = Column(Integer, nullable=False, default=0)
    tra_tipdoc = Column(Integer, default=0)
    tra_tipoprecio = Column(Integer, nullable=False, default=0)
    tra_codrep = Column(Integer, nullable=False, default=0)
    tra_dupite = Column(Integer, nullable=False, default=0)
    tra_preiva = Column(Integer, nullable=False, default=0)
    tra_vietot = Column(Integer, nullable=False, default=0)
    tra_contab = Column(Integer, nullable=False, default=0)
    tra_inv = Column(Integer, nullable=False, default=0)
    tra_seccion = Column(Integer, nullable=False, default=0)